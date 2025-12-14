> [!WARNING]
> 由于出现很多复制下载此存储库后又重新上传发布冒充的情况
> 
> 源项目所属 【FGODailyBonus -> FGO-Daily-Login -> F-D-L】
> 
> 特此提醒，使用本存储库以外类似存储库的代码前，应检查代码是存在否异常行为防止出现盗号和其它损失！

 # FGO每日自动登录 (青龙面板修改版)

本项目基于 [DNNDHH/F-D-L](https://github.com/DNNDHH/F-D-L) 修改，适配青龙面板运行，并使用钉钉机器人推送通知。

<img width="40%" style="border: 1px solid black" src="./libs/2024-10-20 204307.png">

🤓这么多年来…就目前来说有那么亿点点封号风险(^_-)-☆

⚠️注意事项
 - 2024年5月7日起 连接绑定 Aniplex Online 后的游戏账号文件  可以继续使用！没有影响！

该修改版 项目源 及 原作者

- [hexstr](https://github.com/hexstr)
- [Isaac](https://github.com/O-Isaac)
- [FGODailyBonus](https://github.com/hexstr/FGODailyBonus)
- [FGO-Daily-Login](https://github.com/O-Isaac/FGO-Daily-Login)
- [DNNDHH/F-D-L](https://github.com/DNNDHH/F-D-L) (**原项目地址**)
  

它具有以下特点：
- 适配青龙面板 (Python3)
- 全自动游戏版本更新同步
- 向你的钉钉群发送登录结果等信息 (Markdown格式，无图模式)
- 只支持 JP 版本游戏(日服)😛
- ---------------------------------------------------------------------------------- -
- Fork此库后按顺序操作
- ---------------------------------------------------------------------------------- -

# 1. 提取 游戏账号数据

你需要提取账号数据才能执行此操作。
很简单，你所需要做的就是用文件管理器到以下路径并获取以下文件（可能需要ROOT）： 

| 版本 | 文件路径 | 文件名称 |
| --- | --- | --- | 
| JP | `android/data/com.aniplex.fategrandorder/files/data/` | 54cc790bf952ea710ed7e8be08049531 |

ADB命令复制到 下载 目录中 即 Download（可跳过部分系统的Root要求）
```console
adb shell cp /storage/emulated/0/Android/data/com.aniplex.fategrandorder/files/data/54cc790bf952ea710ed7e8be08049531 /storage/emulated/0/Download/
```  
-----------------

# 2. 解密 游戏账号数据

请小心处理这些数据，你不应将此数据传递给其他人，这是直接与服务器通信的关键数据，能直接盗你的号！

1. 下载 FGO-ADET ，按照解密方法, 并解密游戏文件! [FGO-ADET](https://github.com/DNNDHH/FGO-ADET)
2. 获取 userId, authKey, secretKey

# 3. 获取设备信息 (可选)

1. 获取你的设备（手机或模拟器）的 用户代理 & 设备信息 : [Post Device info](https://github.com/DNNDHH/Post-Device-info)
2. 得到的 UserAgent 留作 USER_AGENT_SECRET_2 备用
3. 得到的 Device Info 留作 DEVICE_INFO_SECRET 备用


# 4. 创建 钉钉 消息通知机器人
- 在钉钉群组设置中添加自定义机器人
- 安全设置选择 "加签"
- 复制 `Webhook` 地址
- 复制 `SEC` 开头的密钥 (Secret)


# 5. 青龙面板环境变量设置

在青龙面板的 "环境变量" 中添加以下变量：

| 变量名 | 说明 | 示例 |
| --- | --- | --- |
| `userIds` | 游戏 User ID，多个账号用逗号分隔 | `123456789,987654321` |
| `authKeys` | 游戏 Auth Key，多个账号用逗号分隔 | `key1,key2` |
| `secretKeys` | 游戏 Secret Key，多个账号用逗号分隔 | `secret1,secret2` |
| `DINGTALK_WEBHOOK` | 钉钉机器人 Webhook 地址 | `https://oapi.dingtalk.com/robot/send?access_token=...` |
| `DINGTALK_SECRET` | 钉钉机器人加签密钥 | `SEC...` |
| `USER_AGENT_SECRET_2` | (选填) 设备 User Agent | `Dalvik/2.1.0...` |
| `DEVICE_INFO_SECRET` | (选填) 设备 Info | `Google Pixel 5...` |
| `APP_CHECK_SECRET` | (选填) App Check | 留空 |


# 6. 设置执行 定时签到任务

在青龙面板中添加定时任务：
- **命令**: `python3 main.py`
- **定时规则**: 自定义，例如 `0 19 * * *` (每天19点)

- -------------------------------------------------------------------------------------- -

# 已完成 
- [x] 适配青龙面板运行
- [x] 钉钉机器人通知 (支持签名校验)
- [x] 移除通知图片
- [x] 自动每日友情召唤/友情活动限定召唤
- [x] 自动领取礼物盒
- [x] 自动兑换达芬奇商店 每月&限时活动 呼符
- [x] 自动兑换 素材交換券
- [x] 屏蔽自动种蓝苹果 (已注释)

- -------------------------------------------------------------------------------------- -
# 感谢
- [DNNDHH/F-D-L](https://github.com/DNNDHH/F-D-L) (本项目基于此仓库修改)
- [hexstr](https://github.com/hexstr) 
