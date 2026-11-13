"""Offline coverage for material-ticket selection; no account or webhook calls."""

import base64
import copy
import json
import logging
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs

import msgpack
import requests

# main.py reads account credentials on import. Only its logger is needed here.
with patch.dict(sys.modules, {'main': SimpleNamespace(logger=logging.getLogger(__name__))}):
    import user


class MaterialTicketTests(unittest.TestCase):
    def setUp(self):
        workspace = tempfile.TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        previous_cwd = os.getcwd()
        os.chdir(workspace.name)
        self.addCleanup(os.chdir, previous_cwd)

        self.catalogue = [{
            'id': 10114, 'name': '11月交換券',
            'itemSelects': [self.option(3, 6501), self.option(7, 6502), self.option(9, 6503)],
        }] + [{'id': item_id, 'originalName': f'素材{item_id}'}
             for item_id in (6501, 6502, 6503)]
        self.write_presents([
            {'giftType': 2, 'objectId': 10114, 'presentId': 101},
            {'giftType': 2, 'objectId': 10114, 'presentId': 102},
            {'giftType': 2, 'objectId': 10113, 'presentId': 103},
        ])

        self.post = self.start_patch(user.fgourl, 'PostReq', return_value={})
        self.get = self.start_patch(user.requests, 'get')
        self.get.return_value.json.side_effect = lambda: copy.deepcopy(self.catalogue)
        self.notify = self.start_patch(user.webhook, 'Present')
        self.logger = self.start_patch(user.main, 'logger')
        self.client = user.user('123', 'test-auth', 'test-secret')

    def start_patch(self, target, attribute, **kwargs):
        patcher = patch.object(target, attribute, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    @staticmethod
    def option(idx, item_id):
        return {'idx': idx, 'requireNum': 1,
                'gifts': [{'type': 'item', 'objectId': item_id, 'num': 1}]}

    @staticmethod
    def write_presents(presents):
        Path('present.json').write_text(json.dumps({
            'cache': {'replaced': {'userPresentBox': presents}},
        }), encoding='utf-8')

    def seed_inventory(self, counts):
        self.post.return_value = {'cache': {'replaced': {'userItem': [
            {'itemId': item_id, 'num': count} for item_id, count in counts.items()
        ]}}}
        self.client.Post('offline://login')
        self.post.return_value = {}
        self.post.reset_mock()

    def receive_parameters(self):
        self.post.assert_called_once()
        self.assertIn('/present/receive?', self.post.call_args.args[1])
        return parse_qs(self.post.call_args.args[2])

    def test_redeems_batch_for_least_stocked_option_using_server_index(self):
        self.seed_inventory({6501: 90, 6502: 4, 6503: 20})
        self.client.Present()
        params = self.receive_parameters()
        self.assertEqual(params['itemSelectIdx'], ['7'])
        self.assertEqual(params['itemSelectNum'], ['2'])
        self.assertEqual(msgpack.unpackb(base64.b64decode(params['presentIds'][0])),
                         [101, 102])
        self.notify.assert_called_once_with('11月交換券', '素材6502', 2)
        self.assertIn('兑换前库存 4', self.logger.info.call_args.args[0])

    def test_missing_material_row_in_complete_inventory_means_zero(self):
        self.seed_inventory({6501: 9, 6503: 2})
        self.client.Present()
        self.assertEqual(self.receive_parameters()['itemSelectIdx'], ['7'])

    def test_tied_balances_keep_first_option_in_catalogue_order(self):
        self.catalogue[0]['itemSelects'].reverse()
        self.seed_inventory({6501: 2, 6502: 2, 6503: 2})
        self.client.Present()
        self.assertEqual(self.receive_parameters()['itemSelectIdx'], ['9'])

    def test_complete_empty_inventory_is_distinct_from_unknown_inventory(self):
        self.seed_inventory({})
        self.client.Present()
        self.assertEqual(self.receive_parameters()['itemSelectIdx'], ['3'])

    def test_latest_absolute_balances_override_login_snapshot(self):
        self.seed_inventory({6501: 1, 6502: 5, 6503: 8})
        self.post.return_value = {'cache': {'updated': {'userItem': [
            {'itemId': 6501, 'num': 20}, {'itemId': 6502, 'num': 4},
        ]}}}
        self.client.Post('offline://home')
        self.post.return_value = {}
        self.post.reset_mock()
        self.client.Present()
        self.assertEqual(self.receive_parameters()['itemSelectIdx'], ['7'])
        self.assertEqual(self.client.item_counts_[6501], 20)
        self.assertEqual(self.client.item_counts_[6502], 4)

    def test_receive_response_updates_inventory_for_next_batch(self):
        self.seed_inventory({6501: 3, 6502: 4, 6503: 8})
        self.post.return_value = {'cache': {'updated': {'userItem': [
            {'itemId': 6501, 'num': 5},
        ]}}}
        self.client.Present()
        self.assertEqual(self.receive_parameters()['itemSelectIdx'], ['3'])
        self.write_presents([{'giftType': 2, 'objectId': 10114, 'presentId': 201}])
        self.post.reset_mock()
        self.post.return_value = {}
        self.client.Present()
        self.assertEqual(self.receive_parameters()['itemSelectIdx'], ['7'])

    def test_partial_updates_without_snapshot_do_not_allow_redemption(self):
        self.post.return_value = {'cache': {'updated': {'userItem': [
            {'itemId': 6501, 'num': 8},
        ]}}}
        self.client.Post('offline://partial')
        self.post.reset_mock()
        self.client.Present()
        self.post.assert_not_called()
        self.notify.assert_not_called()
        self.logger.warning.assert_called_once()

    def test_inventory_is_isolated_between_accounts_and_snapshots_replace_it(self):
        self.seed_inventory({6501: 1, 6502: 5})
        other_client = user.user('456', 'other-auth', 'other-secret')
        self.assertIsNone(other_client.item_counts_)
        self.seed_inventory({6503: 4})
        self.assertEqual(self.client.item_counts_, {6503: 4})
        self.assertIsNone(other_client.item_counts_)

    def test_no_tickets_still_refreshes_drop_names_without_redeeming(self):
        self.write_presents([
            {'giftType': 2, 'objectId': None, 'presentId': 1},
            {'giftType': 2, 'objectId': 6501, 'presentId': 2},
            {'giftType': 1, 'objectId': 10114, 'presentId': 3},
        ])
        self.client.Present()
        self.get.assert_called_once()
        self.assertEqual(json.loads(Path('nice_item.json').read_text(encoding='utf-8')),
                         self.catalogue)
        self.post.assert_not_called()
        self.notify.assert_not_called()

    def test_catalogue_failure_skips_redemption(self):
        self.seed_inventory({6501: 3})
        for error in (requests.Timeout('offline'), ValueError('invalid JSON')):
            with self.subTest(error=type(error).__name__):
                self.get.side_effect = error
                self.client.Present()
                self.post.assert_not_called()
                self.notify.assert_not_called()

    def test_unsupported_options_skip_redemption(self):
        self.seed_inventory({})
        multi_gift = self.option(1, 6501)
        multi_gift['gifts'].append({'type': 'item', 'objectId': 6502, 'num': 1})
        non_item = self.option(2, 6501)
        non_item['gifts'][0]['type'] = 'servant'
        expensive = self.option(3, 6501)
        expensive['requireNum'] = 2
        self.catalogue[0]['itemSelects'] = [{}, multi_gift, non_item, expensive]
        self.client.Present()
        self.post.assert_not_called()
        self.notify.assert_not_called()

    def test_failed_receive_does_not_report_success(self):
        self.seed_inventory({6501: 3, 6502: 5, 6503: 8})
        self.post.side_effect = RuntimeError('receive rejected')
        with self.assertRaisesRegex(RuntimeError, 'receive rejected'):
            self.client.Present()
        self.notify.assert_not_called()
        self.logger.info.assert_not_called()
        self.assertEqual(self.client.item_counts_[6501], 3)


if __name__ == '__main__':
    unittest.main()
