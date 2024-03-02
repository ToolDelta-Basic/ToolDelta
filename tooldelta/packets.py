class PacketIDS:
    Text = 9
    PlayerList = 63
    CommandOutput = 79


packets = {
    "1": "IDLogin",
    "2": "IDPlayStatus",
    "3": "IDServerToClientHandshake",
    "4": "IDClientToServerHandshake",
    "5": "IDDisconnect",
    "6": "IDResourcePacksInfo",
    "7": "IDResourcePackStack",
    "8": "IDResourcePackClientResponse",
    "9": "IDText",
    "10": "IDSetTime",
    "11": "IDStartGame",
    "12": "IDAddPlayer",
    "13": "IDAddActor",
    "14": "_",
    "15": "IDRemoveActor",
    "16": "IDAddItemActor",
    "17": "IDTakeItemActor",
    "18": "IDMoveActorAbsolute",
    "19": "IDMovePlayer",
    "20": "IDPassengerJump",
    "21": "IDUpdateBlock",
    "22": "IDAddPainting",
    "23": "IDTickSync",
    "24": "_",
    "25": "IDLevelEvent",
    "26": "IDBlockEvent",
    "27": "IDActorEvent",
    "28": "IDMobEffect",
    "29": "IDUpdateAttributes",
    "30": "IDInventoryTransaction",
    "31": "IDMobEquipment",
    "32": "IDMobArmourEquipment",
    "33": "IDInteract",
    "34": "IDBlockPickRequest",
    "35": "IDActorPickRequest",
    "36": "IDPlayerAction",
    "37": "_",
    "38": "IDHurtArmour",
    "39": "IDSetActorData",
    "40": "IDSetActorMotion",
    "41": "IDSetActorLink",
    "42": "IDSetHealth",
    "43": "IDSetSpawnPosition",
    "44": "IDAnimate",
    "45": "IDRespawn",
    "46": "IDContainerOpen",
    "47": "IDContainerClose",
    "48": "IDPlayerHotBar",
    "49": "IDInventoryContent",
    "50": "IDInventorySlot",
    "51": "IDContainerSetData",
    "52": "IDCraftingData",
    "53": "IDCraftingEvent",
    "54": "IDGUIDataPickItem",
    "55": "IDAdventureSettings",
    "56": "IDBlockActorData",
    "57": "IDPlayerInput",
    "58": "IDLevelChunk",
    "59": "IDSetCommandsEnabled",
    "60": "IDSetDifficulty",
    "61": "IDChangeDimension",
    "62": "IDSetPlayerGameType",
    "63": "IDPlayerList",
    "64": "IDSimpleEvent",
    "65": "IDEvent",
    "66": "IDSpawnExperienceOrb",
    "67": "IDClientBoundMapItemData",
    "68": "IDMapInfoRequest",
    "69": "IDRequestChunkRadius",
    "70": "IDChunkRadiusUpdated",
    "71": "IDItemFrameDropItem",
    "72": "IDGameRulesChanged",
    "73": "IDCamera",
    "74": "IDBossEvent",
    "75": "IDShowCredits",
    "76": "IDAvailableCommands",
    "77": "IDCommandRequest",
    "78": "IDCommandBlockUpdate",
    "79": "IDCommandOutput",
    "80": "IDUpdateTrade",
    "81": "IDUpdateEquip",
    "82": "IDResourcePackDataInfo",
    "83": "IDResourcePackChunkData",
    "84": "IDResourcePackChunkRequest",
    "85": "IDTransfer",
    "86": "IDPlaySound",
    "87": "IDStopSound",
    "88": "IDSetTitle",
    "89": "IDAddBehaviourTree",
    "90": "IDStructureBlockUpdate",
    "91": "IDShowStoreOffer",
    "92": "IDPurchaseReceipt",
    "93": "IDPlayerSkin",
    "94": "IDSubClientLogin",
    "95": "IDAutomationClientConnect",
    "96": "IDSetLastHurtBy",
    "97": "IDBookEdit",
    "98": "IDNPCRequest",
    "99": "IDPhotoTransfer",
    "100": "IDModalFormRequest",
    "101": "IDModalFormResponse",
    "102": "IDServerSettingsRequest",
    "103": "IDServerSettingsResponse",
    "104": "IDShowProfile",
    "105": "IDSetDefaultGameType",
    "106": "IDRemoveObjective",
    "107": "IDSetDisplayObjective",
    "108": "IDSetScore",
    "109": "IDLabTable",
    "110": "IDUpdateBlockSynced",
    "111": "IDMoveActorDelta",
    "112": "IDSetScoreboardIdentity",
    "113": "IDSetLocalPlayerAsInitialised",
    "114": "IDUpdateSoftEnum",
    "115": "IDNetworkStackLatency",
    "116": "_",
    "117": "IDScriptCustomEvent",
    "118": "IDSpawnParticleEffect",
    "119": "IDAvailableActorIdentifiers",
    "120": "_",
    "121": "IDNetworkChunkPublisherUpdate",
    "122": "IDBiomeDefinitionList",
    "123": "IDLevelSoundEvent",
    "124": "IDLevelEventGeneric",
    "125": "IDLecternUpdate",
    "126": "_",
    "127": "IDAddEntity",
    "128": "IDRemoveEntity",
    "129": "IDClientCacheStatus",
    "130": "IDMapCreateLockedCopy",
    "131": "IDOnScreenTextureAnimation",
    "132": "IDStructureTemplateDataRequest",
    "133": "IDStructureTemplateDataResponse",
    "134": "_",
    "135": "IDClientCacheBlobStatus",
    "136": "IDClientCacheMissResponse",
    "137": "IDEducationSettings",
    "138": "IDEmote",
    "139": "IDMultiPlayerSettings",
    "140": "IDSettingsCommand",
    "141": "IDAnvilDamage",
    "142": "IDCompletedUsingItem",
    "143": "IDNetworkSettings",
    "144": "IDPlayerAuthInput",
    "145": "IDCreativeContent",
    "146": "IDPlayerEnchantOptions",
    "147": "IDItemStackRequest",
    "148": "IDItemStackResponse",
    "149": "IDPlayerArmourDamage",
    "150": "IDCodeBuilder",
    "151": "IDUpdatePlayerGameType",
    "152": "IDEmoteList",
    "153": "IDPositionTrackingDBServerBroadcast",
    "154": "IDPositionTrackingDBClientRequest",
    "155": "IDDebugInfo",
    "156": "IDPacketViolationWarning",
    "157": "IDMotionPredictionHints",
    "158": "IDAnimateEntity",
    "159": "IDCameraShake",
    "160": "IDPlayerFog",
    "161": "IDCorrectPlayerMovePrediction",
    "162": "IDItemComponent",
    "163": "IDFilterText",
    "164": "IDClientBoundDebugRenderer",
    "165": "IDSyncActorProperty",
    "166": "IDAddVolumeEntity",
    "167": "IDRemoveVolumeEntity",
    "168": "IDSimulationType",
    "169": "IDNPCDialogue",
    "170": "IDEducationResourceURI",
    "171": "IDCreatePhoto",
    "172": "IDUpdateSubChunkBlocks",
    "173": "IDPhotoInfoRequest",
    "174": "IDSubChunk",
    "175": "IDSubChunkRequest",
    "176": "IDClientStartItemCooldown",
    "177": "IDScriptMessage",
    "178": "IDCodeBuilderSource",
    # 以下为机翻数据包名称(仅供参考！)
    # 1. "IDLogin" -> "ID 登录"
    # 2. "IDPlayStatus" -> "ID 游戏状态"
    # 3. "IDServerToClientHandshake" -> "ID 服务器到客户端握手"
    # 4. "IDClientToServerHandshake" -> "ID 客户端到服务器握手"
    # 5. "IDDisconnect" -> "ID 断开连接"
    # 6. "IDResourcePacksInfo" -> "ID 资源包信息"
    # 7. "IDResourcePackStack" -> "ID 资源包堆栈"
    # 8. "IDResourcePackClientResponse" -> "ID 资源包客户端响应"
    # 9. "IDText" -> "ID 文本"
    # 10. "IDSetTime" -> "ID 设置时间"
    # 11. "IDStartGame" -> "ID 开始游戏"
    # 12. "IDAddPlayer" -> "ID 添加玩家"
    # 13. "IDAddActor" -> "ID 添加角色"
    # 14. "_" -> "_"
    # 15. "IDRemoveActor" -> "ID 移除角色"
    # 16. "IDAddItemActor" -> "ID 添加物品角色"
    # 17. "IDTakeItemActor" -> "ID 拿起物品角色"
    # 18. "IDMoveActorAbsolute" -> "ID 绝对移动角色"
    # 19. "IDMovePlayer" -> "ID 移动玩家"
    # 20. "IDPassengerJump" -> "ID 乘客跳跃"
    # 21. "IDUpdateBlock" -> "ID 更新方块"
    # 22. "IDAddPainting" -> "ID 添加绘画"
    # 23. "IDTickSync" -> "ID 时钟同步"
    # 24. "_" -> "_"
    # 25. "IDLevelEvent" -> "ID 关卡事件"
    # 26. "IDBlockEvent" -> "ID 方块事件"
    # 27. "IDActorEvent" -> "ID 角色事件"
    # 28. "IDMobEffect" -> "ID 生物效果"
    # 29. "IDUpdateAttributes" -> "ID 更新属性"
    # 30. "IDInventoryTransaction" -> "ID 物品栏交易"
    # 31. "IDMobEquipment" -> "ID 生物装备"
    # 32. "IDMobArmourEquipment" -> "ID 生物护甲装备"
    # 33. "IDInteract" -> "ID 交互"
    # 34. "IDBlockPickRequest" -> "ID 方块选择请求"
    # 35. "IDActorPickRequest" -> "ID 角色选择请求"
    # 36. "IDPlayerAction" -> "ID 玩家动作"
    # 37. "_" -> "_"
    # 38. "IDHurtArmour" -> "ID 伤害护甲"
    # 39. "IDSetActorData" -> "ID 设置角色数据"
    # 40. "IDSetActorMotion" -> "ID 设置角色动作"
    # 41. "IDSetActorLink" -> "ID 设置角色链接"
    # 42. "IDSetHealth" -> "ID 设置生命值"
    # 43. "IDSetSpawnPosition" -> "ID 设置生成位置"
    # 44. "IDAnimate" -> "ID 动画"
    # 45. "IDRespawn" -> "ID 重生"
    # 46. "IDContainerOpen" -> "ID 打开容器"
    # 47. "IDContainerClose" -> "ID 关闭容器"
    # 48. "IDPlayerHotBar" -> "ID 玩家快捷栏"
    # 49. "IDInventoryContent" -> "ID 物品栏内容"
    # 50. "IDInventorySlot" -> "ID 物品栏槽位"
    # 51. "IDContainerSetData" -> "ID 设置容器数据"
    # 52. "IDCraftingData" -> "ID 制作数据"
    # 53. "IDCraftingEvent" -> "ID 制作事件"
    # 54. "IDGUIDataPickItem" -> "ID GUI 数据选取物品"
    # 55. "IDAdventureSettings" -> "ID 冒险设置"
    # 56. "IDBlockActorData" -> "ID 方块角色数据"
    # 57. "IDPlayerInput" -> "ID 玩家输入"
    # 58. "IDLevelChunk" -> "ID 关卡区块"
    # 59. "IDSetCommandsEnabled" -> "ID 设置命令启用"
    # 60. "IDSetDifficulty" -> "ID 设置难度"
    # 61. "IDChangeDimension" -> "ID 切换维度"
    # 62. "IDSetPlayerGameType" -> "ID 设置玩家游戏模式"
    # 63. "IDPlayerList" -> "ID 玩家列表"
    # 64. "IDSimpleEvent" -> "ID 简单事件"
    # 65. "IDEvent" -> "ID 事件"
    # 66. "IDSpawnExperienceOrb" -> "ID 生成经验球"
    # 67. "IDClientBoundMapItemData" -> "ID 客户端绑定的地图物品数据"
    # 68. "IDMapInfoRequest" -> "ID 地图信息请求"
    # 69. "IDRequestChunkRadius" -> "ID 请求区块半径"
    # 70. "IDChunkRadiusUpdated" -> "ID 区块半径更新"
    # 71. "IDItemFrameDropItem" -> "ID 物品展示框掉落物品"
    # 72. "IDGameRulesChanged" -> "ID 游戏规则更改"
    # 73. "IDCamera" -> "ID 摄像机"
    # 74. "IDBossEvent" -> "ID Boss 事件"
    # 75. "IDShowCredits" -> "ID 显示制作人员"
    # 76. "IDAvailableCommands" -> "ID 可用命令"
    # 77. "IDCommandRequest" -> "ID 命令请求"
    # 78. "IDCommandBlockUpdate" -> "ID 命令方块更新"
    # 79. "IDCommandOutput" -> "ID 命令输出"
    # 80. "IDUpdateTrade" -> "ID 更新交易"
    # 81. "IDUpdateEquip" -> "ID 更新装备"
    # 82. "IDResourcePackDataInfo" -> "ID 资源包数据信息"
    # 83. "IDResourcePackChunkData" -> "ID 资源包区块数据"
    # 84. "IDResourcePackChunkRequest" -> "ID 资源包区块请求"
    # 85. "IDTransfer" -> "ID 传输"
    # 86. "IDPlaySound" -> "ID 播放声音"
    # 87. "IDStopSound" -> "ID 停止声音"
    # 88. "IDSetTitle" -> "ID 设置标题"
    # 89. "IDAddBehaviourTree" -> "ID 添加行为树"
    # 90. "IDStructureBlockUpdate" -> "ID 结构方块更新"
    # 91. "IDShowStoreOffer" -> "ID 显示商店优惠"
    # 92. "IDPurchaseReceipt" -> "ID 购买凭据"
    # 93. "IDPlayerSkin" -> "ID 玩家皮肤"
    # 94. "IDSubClientLogin" -> "ID 子客户端登录"
    # 95. "IDAutomationClientConnect" -> "ID 自动化客户端连接"
    # 96. "IDSetLastHurtBy" -> "ID 设置最后受伤者"
    # 97. "IDBookEdit" -> "ID 编辑书籍"
    # 98. "IDNPCRequest" -> "ID NPC 请求"
    # 99. "IDPhotoTransfer" -> "ID 照片传输"
    # 100. "IDModalFormRequest" -> "ID 模态表单请求"
    # 101. "IDModalFormResponse" -> "ID 模态表单响应"
    # 102. "IDServerSettingsRequest" -> "ID 服务器设置请求"
    # 103. "IDServerSettingsResponse" -> "ID 服务器设置响应"
    # 104. "IDShowProfile" -> "ID 显示个人资料"
    # 105. "IDSetDefaultGameType" -> "ID 设置默认游戏模式"
    # 106. "IDRemoveObjective" -> "ID 移除目标"
    # 107. "IDSetDisplayObjective" -> "ID 设置显示目标"
    # 108. "IDSetScore" -> "ID 设置分数"
    # 109. "IDLabTable" -> "ID 实验室桌子"
    # 110. "IDUpdateBlockSynced" -> "ID 同步更新方块"
    # 111. "IDMoveActorDelta" -> "ID 移动角色增量"
    # 112. "IDSetScoreboardIdentity" -> "ID 设置记分板身份"
    # 113. "IDSetLocalPlayerAsInitialised" -> "ID 设置本地玩家已初始化"
    # 114. "IDUpdateSoftEnum" -> "ID 更新软枚举"
    # 115. "IDNetworkStackLatency" -> "ID 网络堆栈延迟"
    # 116. "_" -> "_"
    # 117. "IDScriptCustomEvent" -> "ID
}


class SubPacket_CmdOutputMsg:
    Success: bool
    Message: str
    Parameters: list[str]

    def __init__(self, pkt: dict):
        self.Success = pkt["Success"]
        self.Parameters = pkt["Parameters"]
        self.Message = pkt["Message"]


class SubPacket_CmdOrigin:
    Origin: int
    UUID: str
    RequestID: str
    PlayerUniqueID: int

    def __init__(self, pkt: dict):
        self.Origin = pkt["Origin"]
        self.UUID = pkt["UUID"]
        self.RequestID = pkt["RequestID"]
        self.PlayerUniqueID = pkt["PlayerUniqueID"]


class Packet_CommandOutput:
    CommandOrigin: SubPacket_CmdOrigin
    OutputType: int
    SuccessCount: int
    OutputMessages: list[SubPacket_CmdOutputMsg]
    as_dict: dict

    def __init__(self, pkt: dict):
        self.as_dict = pkt
        self.CommandOrigin = SubPacket_CmdOrigin(pkt["CommandOrigin"])
        self.OutputMessages = [
            SubPacket_CmdOutputMsg(imsg) for imsg in pkt["OutputMessages"]
        ]
        self.SuccessCount = pkt["SuccessCount"]
        self.OutputType = pkt["OutputType"]
