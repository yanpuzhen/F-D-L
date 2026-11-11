import requests
import main

from mytime import GetTimeStamp

NICE_GACHA_URL = "https://api.atlasacademy.io/export/JP/nice_gacha.json"
FP_GACHA_ID = 1


def GetGachaSubIdFP():
    # 同 gacha_lab: 只取常驻友情池 (gachaId=1) 当前开放、priority 最高的 gachaSubId
    # 限定友情池 (如 gachaId=28) 的 subId 与 gachaId=1 不配套, 混用会报 [99]
    # (旧的 git.atlasacademy.io/mstGachaSub.json 现在需要登录, 已无法使用)
    timeNow = GetTimeStamp()
    gachas = requests.get(NICE_GACHA_URL, timeout=120).json()

    for gacha in gachas:
        if gacha.get("type") != "friendPoint" or gacha.get("id") != FP_GACHA_ID:
            continue
        if not (gacha["openedAt"] <= timeNow <= gacha["closedAt"]):
            continue
        subs = [s for s in gacha.get("gachaSubs", [])
                if s["openedAt"] <= timeNow <= s["closedAt"]]
        if subs:
            return str(max(subs, key=lambda s: s["priority"])["id"])

    main.logger.info("No suitable gacha found")
    return None
