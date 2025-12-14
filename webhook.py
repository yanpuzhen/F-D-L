import main
import requests
import user
import json


def topLogin(data: list) -> None:
    endpoint = main.webhook_dingtalk_url

    rewards: user.Rewards = data[0]
    login: user.Login = data[1]
    bonus: user.Bonus or str = data[2]
    with open('login.json', 'r', encoding='utf-8')as f:
        data22 = json.load(f)

        name1 = data22['cache']['replaced']['userGame'][0]['name']
        fpids1 = data22['cache']['replaced']['userGame'][0]['friendCode']
    
    messageBonus = ''
    nl = '\n'

    if bonus != "No Bonus":
        messageBonus += f"**{bonus.message}**\n> {nl.join(bonus.items)}\n"

        if bonus.bonus_name != None:
            messageBonus += f"\n**{bonus.bonus_name}**\n{bonus.bonus_detail}\n> {nl.join(bonus.bonus_camp_items)}\n"

        messageBonus += "\n"

    jsonData = {
        "msgtype": "markdown",
        "markdown": {
            "title": "FGO登录系统 - " + main.fate_region,
            "text": f"### FGO登录系统 - {main.fate_region}\n\n"
                    f"**登录成功**\n\n{messageBonus}"
                    f"- **御主名**: {name1}\n"
                    f"- **朋友ID**: {fpids1}\n"
                    f"- **等级**: {rewards.level}\n"
                    f"- **呼符**: {rewards.ticket}\n"
                    f"- **圣晶石**: {rewards.stone}\n"
                    f"- **圣晶片**: {rewards.sqf01}\n"
                    f"- **金苹果**: {rewards.goldenfruit}\n"
                    f"- **银苹果**: {rewards.silverfruit}\n"
                    f"- **铜苹果**: {rewards.bronzefruit}\n"
                    f"- **蓝苹果**: {rewards.bluebronzefruit}\n"
                    f"- **蓝苹果树苗**: {rewards.bluebronzesapling}\n"
                    f"- **连续登录**: {login.login_days}\n"
                    f"- **累计登录**: {login.total_days}\n"
                    f"- **白方块**: {rewards.pureprism}\n"
                    f"- **友情点**: {login.total_fp}\n"
                    f"- **今日FP**: +{login.add_fp}\n"
                    f"- **当前AP**: {login.remaining_ap}\n"
                    f"- **圣杯**: {rewards.holygrail}\n"
                    f"![Image](https://www.fate-go.jp/manga_fgo/images/commnet_chara01.png)"
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    requests.post(endpoint, json=jsonData, headers=headers)


def shop(item: str, quantity: str) -> None:
    endpoint = main.webhook_dingtalk_url
    
    jsonData = {
        "msgtype": "markdown",
        "markdown": {
            "title": "FGO自动购物 - " + main.fate_region,
            "text": f"### FGO自动购物 - {main.fate_region}\n\n"
                    f"**购买成功**\n\n"
                    f"- **商店**: 消费 {40 * quantity}Ap 购买 {quantity}x {item}\n"
                    f"![Image](https://www.fate-go.jp/manga_fgo2/images/commnet_chara10.png)"
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    requests.post(endpoint, json=jsonData, headers=headers)


def drawFP(servants, missions) -> None:
    endpoint = main.webhook_dingtalk_url

    message_mission = ""
    message_servant = ""
    
    if (len(servants) > 0):
        servants_atlas = requests.get(
            f"https://api.atlasacademy.io/export/JP/basic_svt.json").json()

        svt_dict = {svt["id"]: svt for svt in servants_atlas}

        for servant in servants:
            objectId = servant.objectId
            if objectId in svt_dict:
                svt = svt_dict[objectId]
                message_servant += f"{svt['name']} "
            else:
                continue

    if(len(missions) > 0):
        for mission in missions:
            message_mission += f"**{mission.message}**\n{mission.progressTo}/{mission.condition}\n"

    jsonData = {
        "msgtype": "markdown",
        "markdown": {
            "title": "FGO自动抽卡 - " + main.fate_region,
            "text": f"### FGO自动抽卡 - {main.fate_region}\n\n"
                    f"**每日免费友情抽卡**\n\n"
                    f"{message_mission}\n"
                    f"- **友情卡池**: {message_servant}\n"
                    f"![Image](https://www.fate-go.jp/manga_fgo/images/commnet_chara02_rv.png)"
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    requests.post(endpoint, json=jsonData, headers=headers)


def LTO_Gacha(servants) -> None:
    endpoint = main.webhook_dingtalk_url

    message_servant = ""
    
    if (len(servants) > 0):
        servants_atlas = requests.get(
            f"https://api.atlasacademy.io/export/JP/basic_svt.json").json()

        svt_dict = {svt["id"]: svt for svt in servants_atlas}

        for servant in servants:
            objectId = servant.objectId
            if objectId in svt_dict:
                svt = svt_dict[objectId]
                message_servant += f"{svt['name']} "
            else:
                continue

    jsonData = {
        "msgtype": "markdown",
        "markdown": {
            "title": "FGO限定抽卡 - " + main.fate_region,
            "text": f"### FGO限定抽卡 - {main.fate_region}\n\n"
                    f"**限定友情抽卡结果**\n\n"
                    f"- **限定卡池**: {message_servant}\n"
                    f"![Image](https://www.fate-go.jp/manga_fgo/images/commnet_chara02_rv.png)"
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    requests.post(endpoint, json=jsonData, headers=headers)


def Free_Gacha(servants) -> None:
    endpoint = main.webhook_dingtalk_url
    message_servant = ""
    
    if (len(servants) > 0):
        servants_atlas = requests.get(
            f"https://api.atlasacademy.io/export/JP/basic_svt.json").json()

        svt_dict = {svt["id"]: svt for svt in servants_atlas}

        for servant in servants:
            objectId = servant.objectId
            if objectId in svt_dict:
                svt = svt_dict[objectId]
                message_servant += f"{svt['name']} "
            else:
                continue

    jsonData = {
        "msgtype": "markdown",
        "markdown": {
            "title": "FGO每日免费单抽 - " + main.fate_region,
            "text": f"### FGO每日免费单抽 - {main.fate_region}\n\n"
                    f"**每日免费单抽结果**\n\n"
                    f"- **常驻卡池**: {message_servant}\n"
                    f"![Image](https://www.fate-go.jp/manga_fgo2/images/commnet_chara13_rv.png)"
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    requests.post(endpoint, json=jsonData, headers=headers)


def Present(name, namegift, object_id_count) -> None:
    endpoint = main.webhook_dingtalk_url
    
    jsonData = {
        "msgtype": "markdown",
        "markdown": {
            "title": "FGO兑换系统 - JP",
            "text": f"### FGO兑换系统 - JP\n\n"
                    f"**兑换成功**\n\n"
                    f"- **{name}**: {namegift} x{object_id_count}\n"
                    f"![Image](https://www.fate-go.jp/manga_fgo2/images/commnet_chara06.png)"
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    requests.post(endpoint, json=jsonData, headers=headers)
