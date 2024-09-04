"ToolDelta 常量定义"

TOOLDELTA_LOGO = """╔═════════════════════════════════════════════════════════════════════════╗
║§9████████╗ ██████╗  ██████╗ ██╗     §b██████╗ ███████╗██╗  ████████╗ █████╗ §r║
║§9╚══██╔══╝██╔═══██╗██╔═══██╗██║     §b██╔══██╗██╔════╝██║  ╚══██╔══╝██╔══██╗§r║
║§9   ██║   ██║   ██║██║   ██║██║     §b██║  ██║█████╗  ██║     ██║   ███████║§r║
║§9   ██║   ██║   ██║██║   ██║██║     §b██║  ██║██╔══╝  ██║     ██║   ██╔══██║§r║
║§9   ██║   ╚██████╔╝╚██████╔╝███████╗§b██████╔╝███████╗███████╗██║   ██║  ██║§r║
║§9   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝§b╚═════╝ ╚══════╝╚══════╝╚═╝   ╚═╝  ╚═╝§r║
╚═════════════════════════════════════════════════════════════════════════╝§r
"""
"ToolDelta标志"

PLUGIN_MARKET_SOURCE_OFFICIAL = (
    "https://github.dqyt.online"
    "/https://raw.githubusercontent.com/ToolDelta-Basic/PluginMarket/main"
)
"插件市场源"

LAUNCH_CFG: dict = {
    "启动器启动模式(请不要手动更改此项, 改为0可重置)": 0,
    "验证服务器地址(更换时记得更改fbtoken)": "",
    "是否记录日志": True,
    "是否使用github镜像": True,
    "插件市场源": PLUGIN_MARKET_SOURCE_OFFICIAL,
}
"默认登录配置"

LAUNCH_CFG_STD: dict = {
    "启动器启动模式(请不要手动更改此项, 改为0可重置)": int,
    "验证服务器地址(更换时记得更改fbtoken)": str,
    "是否记录日志": bool,
    "是否使用github镜像": bool,
    "插件市场源": str,
}
"默认登录配置标准验证格式"

LAUNCHER_NEOMEGA_STD: dict = {
    "服务器号": int,
    "密码": str,
    "验证服务器地址(更换时记得更改fbtoken)": str,
}
"启动器：NeOmega 启动配置验证格式"

LAUNCHER_NEOMEGA_DEFAULT: dict = {
    "服务器号": 0,
    "密码": "",
    "验证服务器地址(更换时记得更改fbtoken)": "",
}
LAUNCHER_NEOMGPARALLELTTOOLDELTA_DEFAULT: dict = {
    "服务器号": 0,
    "密码": "",
    "验证服务器地址(更换时记得更改fbtoken)": "",
}
LAUNCHER_NEOMGPARALLELTTOOLDELTA_STD: dict = {
    "服务器号": int,
    "密码": str,
    "验证服务器地址(更换时记得更改fbtoken)": str,
}

"启动器：NeOmega 默认启动配置"

LAUNCHER_BEWS_STD: dict = {"服务端开放地址": str}
"启动器：BEWSServer 启动配置验证格式"

LAUNCHER_BEWS_DEFAULT: dict = {"服务端开放地址": ""}
"启动器：BEWSServer 默认启动配置"

FB_APIS = [
    "https://user.fastbuilder.pro/api/phoenix/login",
    "https://user.fastbuilder.pro/api/new",
    "https://user.fastbuilder.pro",
]
"验证服务器：FastBuilder API 列表"


GUGU_APIS = [
    "https://liliya233.uk/api/phoenix/login",
    "https://liliya233.uk/api/new",
    "https://liliya233.uk",
]
"验证服务器：Liliya API 列表"

AUTH_SERVERS = [
    ("FastBuilder 官方验证服务器", "https://user.fastbuilder.pro"),
    ("咕咕酱 FB验证服务器", "https://liliya233.uk"),
]
"验证服务器列表"

TOOLDELTA_PLUGIN_DIR = "插件文件"
"插件文件路径"

TOOLDELTA_CLASSIC_PLUGIN = "ToolDelta类式插件"
"插件文件：ToolDelta 类式插件 路径"

TOOLDELTA_INJECTED_PLUGIN = "ToolDelta注入式插件"
"插件文件：ToolDelta 注入式插件 路径"

TOOLDELTA_PLUGIN_DATA_DIR = "插件数据文件"
"插件数据文件文件夹路径"

PLUGIN_TYPE_MAPPING = {
    "classic": TOOLDELTA_CLASSIC_PLUGIN,
    "injected": TOOLDELTA_INJECTED_PLUGIN,
}
"插件属性名映射"

TDSPECIFIC_MIRROR = "https://github.dqyt.online"
"ToolDelta镜像"

TDREPO_URL = (
    f"{TDSPECIFIC_MIRROR}/https://api.github.com/repos/ToolDelta-Basic/ToolDelta"
)


class PacketIDS:
    "数据包 ID 常量表"

    IDLogin = 1  # 客户端登录（本地）
    IDPlayStatus = 2  # 玩家状态
    IDServerToClientHandshake = 3  # 服务端到客户端握手
    IDClientToServerHandshake = 4  # 客户端到服务端握手
    IDDisconnect = 5  # 断开连接
    IDResourcePacksInfo = 6  # 资源包信息（非常用）
    IDResourcePackStack = 7  # 资源包堆叠（非常用）
    IDResourcePackClientResponse = 8  # 资源包客户端响应（非常用）
    IDText = 9  # 文本消息
    IDSetTime = 10  # 更新客户端时间（服务端 -> 客户端）
    IDStartGame = 11  # 开始游戏
    IDAddPlayer = 12  # 添加玩家实体
    IDAddActor = 13  # 添加实体
    IDRemoveActor = 14  # 添加实体
    IDAddItemActor = 15  # 添加物品实体
    IDTakeItemActor = 17  # 捡起物品实体（动画）
    IDMoveActorAbsolute = 18  # 移动实体到绝对位置
    IDMovePlayer = 19  # 玩家移动（服务端 <-> 客户端）
    IDPassengerJump = 20  # 乘骑跳跃（客户端 -> 服务端）
    IDUpdateBlock = 21  # 更新方块（单方块修改）
    IDAddPainting = 22  # 添加绘画实体
    IDTickSync = 23  # 同步Tick（服务端 <-> 客户端）
    IDLevelSoundEventV1 = 24  # ???
    IDLevelEvent = 25  # 世界事件（服务端 -> 客户端）
    IDBlockEvent = 26  # 方块事件（服务端 -> 客户端）[打开箱子./././...]
    IDActorEvent = 27  # 实体事件（服务端 -> 客户端）[狼抖干自己./././...]
    IDMobEffect = 28  # 生物效果（服务端 -> 客户端）
    IDUpdateAttributes = 29  # 更新实体属性（服务端 -> 客户端）[移动速度./健康状况./...]
    IDInventoryTransaction = 30  # 物品交易（服务端 <- 客户端）
    IDMobEquipment = 31  # 实体物品持有（服务端 <-> 客户端）[僵尸手持石剑././...]
    IDMobArmourEquipment = 32  # 装备穿戴（服务端 -> 客户端）[玩家./僵尸./其他实体./...]
    IDInteract = 33  # 实体交互（弃用）
    IDBlockPickRequest = 34  # 拾取物品请求（客户端 -> 服务端）
    IDActorPickRequest = 35  # 拾取实体请求（客户端 -> 服务端）
    IDPlayerAction = 36  # 玩家行为（客户端 -> 服务端）
    IDHurtArmour = 38  # 盔甲损害（服务端 -> 客户端）
    IDSetActorData = 39  # 实体元数据（服务端 -> 客户端）[实体是否着火././...]
    IDSetActorMotion = 40  # 设置客户端速度（服务端 -> 客户端）
    IDSetActorLink = 41  # 设置实体乘骑（服务端 -> 客户端）
    IDSetHealth = 42  # 设置玩家血量（服务端 -> 客户端）
    IDSetSpawnPosition = 43  # 设置玩家出生点位置（服务端 -> 客户端）
    IDAnimate = 44  # 动画效果（服务端 -> 客户端）
    IDRespawn = 45  # 重生（服务端 <-> 客户端）
    IDContainerOpen = 46  # 打开容器（服务端 -> 客户端）
    IDContainerClose = 47  # 关闭容器（服务端 -> 客户端）
    IDPlayerHotBar = 48  # 玩家快捷栏槽位（服务端 -> 客户端）
    IDInventoryContent = 49  # 更新玩家背包（服务端 -> 客户端）
    IDInventorySlot = 50  # 玩家背包单槽位更新（服务端 -> 客户端）
    IDContainerSetData = 51  # 容器设置数据（服务端 -> 客户端）
    IDCraftingData = 52  # 合成数据（服务端 -> 客户端）
    IDCraftingEvent = 53  # 合成事件（客户端 -> 服务端）
    IDGUIDataPickItem = 54  # GUI数据拾取物品（客户端 -> 服务端）
    IDAdventureSettings = 55  # 冒险设置（服务端 -> 客户端）
    IDBlockActorData = 56  # 方块实体数据（服务端 -> 客户端）
    IDPlayerInput = 57  # 玩家输入（客户端 -> 服务端）
    IDLevelChunk = 58  # 区块数据（服务端 -> 客户端）
    IDSetCommandsEnabled = 59  # 设置命令启用（服务端 -> 客户端）
    IDSetDifficulty = 60  # 设置难度（服务端 -> 客户端）
    IDChangeDimension = 61  # 改变维度（服务端 -> 客户端）
    IDSetPlayerGameType = 62  # 设置玩家游戏类型（服务端 -> 客户端）
    IDPlayerList = 63  # 玩家列表（服务端 -> 客户端）
    IDSimpleEvent = 64  # 简单事件（服务端 -> 客户端）
    IDEvent = 65  # 事件（服务端 -> 客户端）
    IDSpawnExperienceOrb = 66  # 生成经验球（服务端 -> 客户端）
    IDClientBoundMapItemData = 67  # 客户端绑定地图物品数据（服务端 -> 客户端）
    IDMapInfoRequest = 68  # 地图信息请求（客户端 -> 服务端）
    IDRequestChunkRadius = 69  # 请求区块半径（客户端 -> 服务端）
    IDChunkRadiusUpdated = 70  # 区块半径更新（服务端 -> 客户端）
    IDItemFrameDropItem = 71  # 物品展示框掉落物品（服务端 -> 客户端）
    IDGameRulesChanged = 72  # 游戏规则改变（服务端 -> 客户端）
    IDCamera = 73  # 相机（服务端 -> 客户端）
    IDBossEvent = 74  # Boss事件（服务端 -> 客户端）
    IDShowCredits = 75  # 显示 credits（服务端 -> 客户端）
    IDAvailableCommands = 76  # 可用命令（服务端 -> 客户端）
    IDCommandRequest = 77  # 命令请求（客户端 -> 服务端）
    IDCommandBlockUpdate = 78  # 命令块更新（客户端 -> 服务端）
    IDCommandOutput = 79  # 命令输出（服务端 -> 客户端）
    IDUpdateTrade = 80  # 更新交易（服务端 -> 客户端）
    IDUpdateEquip = 81  # 更新装备（服务端 -> 客户端）
    IDResourcePackDataInfo = 82  # 资源包数据信息（服务端 -> 客户端）
    IDResourcePackChunkData = 83  # 资源包块数据（服务端 -> 客户端）
    IDResourcePackChunkRequest = 84  # 资源包块请求（客户端 -> 服务端）
    IDTransfer = 85  # 传输（服务端 -> 客户端）
    IDPlaySound = 86  # 播放声音（服务端 -> 客户端）
    IDStopSound = 87  # 停止声音（服务端 -> 客户端）
    IDSetTitle = 88  # 设置标题（服务端 -> 客户端）
    IDAddBehaviourTree = 89  # 添加行为树（服务端 -> 客户端）
    IDStructureBlockUpdate = 90  # 结构方块更新（客户端 -> 服务端）
    IDShowStoreOffer = 91  # 显示商店优惠（服务端 -> 客户端）
    IDPurchaseReceipt = 92  # 购买收据（客户端 -> 服务端）
    IDPlayerSkin = 93  # 玩家皮肤（客户端 -> 服务端）
    IDSubClientLogin = 94  # 子客户端登录（客户端 -> 服务端）
    IDAutomationClientConnect = 95  # 自动化客户端连接（客户端 -> 服务端）
    IDSetLastHurtBy = 96  # 设置最后受伤来源（服务端 -> 客户端）
    IDBookEdit = 97  # 书本编辑（客户端 -> 服务端）
    IDNPCRequest = 98  # NPC请求（客户端 -> 服务端）
    IDPhotoTransfer = 99  # 照片传输（客户端 -> 服务端）
    IDModalFormRequest = 100  # 模态表单请求（服务端 -> 客户端）
    IDModalFormResponse = 101  # 模态表单响应（客户端 -> 服务端）
    IDServerSettingsRequest = 102  # 服务器设置请求（客户端 -> 服务端）
    IDServerSettingsResponse = 103  # 服务器设置响应（服务端 -> 客户端）
    IDShowProfile = 104  # 显示资料（客户端 -> 服务端）
    IDSetDefaultGameType = 105  # 设置默认游戏类型（服务端 -> 客户端）
    IDRemoveObjective = 106  # 移除目标（服务端 -> 客户端）
    IDSetDisplayObjective = 107  # 设置显示目标（服务端 -> 客户端）
    IDSetScore = 108  # 设置分数（服务端 -> 客户端）
    IDLabTable = 109  # 实验室表（服务端 -> 客户端）
    IDUpdateBlockSynced = 110  # 同步更新方块（服务端 -> 客户端）
    IDMoveActorDelta = 111  # 移动实体增量（服务端 -> 客户端）
    IDSetScoreboardIdentity = 112  # 设置计分板身份（服务端 -> 客户端）
    IDSetLocalPlayerAsInitialised = 113  # 设置本地玩家为已初始化（服务端 -> 客户端）
    IDUpdateSoftEnum = 114  # 更新软枚举（服务端 -> 客户端）
    IDNetworkStackLatency = 115  # 网络堆栈延迟（服务端 -> 客户端）
    IDScriptCustomEvent = 117  # 脚本自定义事件（客户端 -> 服务端）
    IDSpawnParticleEffect = 118  # 生成粒子效果（服务端 -> 客户端）
    IDAvailableActorIdentifiers = 119  # 可用实体标识符（服务端 -> 客户端）
    IDLevelSoundEventV2 = 120  # 世界声音事件 V2（服务端 -> 客户端）
    IDNetworkChunkPublisherUpdate = 121  # 网络区块发布者更新（服务端 -> 客户端）
    IDBiomeDefinitionList = 122  # 生物群系定义列表（服务端 -> 客户端）
    IDLevelSoundEvent = 123  # 世界声音事件（服务端 -> 客户端）
    IDLevelEventGeneric = 124  # 世界事件通用（服务端 -> 客户端）
    IDLecternUpdate = 125  # 讲台更新（客户端 -> 服务端）
    IDAddEntity = 127  # 添加实体（服务端 -> 客户端）
    IDRemoveEntity = 128  # 移除实体（服务端 -> 客户端）
    IDClientCacheStatus = 129  # 客户端缓存状态（客户端 -> 服务端）
    IDOnScreenTextureAnimation = 130  # 屏幕纹理动画（服务端 -> 客户端）
    IDMapCreateLockedCopy = 131  # 地图创建锁定副本（服务端 -> 客户端）
    IDStructureTemplateDataRequest = 132  # 结构模板数据请求（客户端 -> 服务端）
    IDStructureTemplateDataResponse = 133  # 结构模板数据响应（服务端 -> 客户端）
    IDClientCacheBlobStatus = 135  # 客户端缓存块状态（客户端 -> 服务端）
    IDClientCacheMissResponse = 136  # 客户端缓存未命中响应（服务端 -> 客户端）
    IDEducationSettings = 137  # 教育设置（服务端 -> 客户端）
    IDEmote = 138  # 表情（客户端 -> 服务端）
    IDMultiPlayerSettings = 139  # 多人游戏设置（客户端 -> 服务端）
    IDSettingsCommand = 140  # 设置命令（客户端 -> 服务端）
    IDAnvilDamage = 141  # 铁砧损坏（服务端 -> 客户端）
    IDCompletedUsingItem = 142  # 完成使用物品（客户端 -> 服务端）
    IDNetworkSettings = 143  # 网络设置（服务端 -> 客户端）
    IDPlayerAuthInput = 144  # 玩家认证输入（客户端 -> 服务端）
    IDCreativeContent = 145  # 创造内容（服务端 -> 客户端）
    IDPlayerEnchantOptions = 146  # 玩家附魔选项（服务端 -> 客户端）
    IDItemStackRequest = 147  # 物品堆栈请求（客户端 -> 服务端）
    IDItemStackResponse = 148  # 物品堆栈响应（服务端 -> 客户端）
    IDPlayerArmourDamage = 149  # 玩家盔甲损坏（服务端 -> 客户端）
    IDCodeBuilder = 150  # 代码构建器（客户端 -> 服务端）
    IDUpdatePlayerGameType = 151  # 更新玩家游戏类型（服务端 -> 客户端）
    IDEmoteList = 152  # 表情列表（服务端 -> 客户端）
    IDPositionTrackingDBServerBroadcast = (
        153  # 位置跟踪数据库服务器广播（服务端 -> 客户端）
    )
    IDPositionTrackingDBClientRequest = (
        154  # 位置跟踪数据库客户端请求（客户端 -> 服务端）
    )
    IDDebugInfo = 155  # 调试信息（服务端 -> 客户端）
    IDPacketViolationWarning = 156  # 数据包违规警告（服务端 -> 客户端）
    IDMotionPredictionHints = 157  # 运动预测提示（服务端 -> 客户端）
    IDAnimateEntity = 158  # 动画实体（服务端 -> 客户端）
    IDCameraShake = 159  # 相机震动（服务端 -> 客户端）
    IDPlayerFog = 160  # 玩家迷雾（服务端 -> 客户端）
    IDCorrectPlayerMovePrediction = 161  # 纠正玩家移动预测（服务端 -> 客户端）
    IDItemComponent = 162  # 物品组件（服务端 -> 客户端）
    IDFilterText = 163  # 过滤文本（客户端 -> 服务端）
    IDClientBoundDebugRenderer = 164  # 客户端绑定调试渲染器（服务端 -> 客户端）
    IDSyncActorProperty = 165  # 同步实体属性（服务端 -> 客户端）
    IDAddVolumeEntity = 166  # 添加体积实体（服务端 -> 客户端）
    IDRemoveVolumeEntity = 167  # 移除体积实体（服务端 -> 客户端）
    IDSimulationType = 168  # 模拟类型（服务端 -> 客户端）
    IDNPCDialogue = 169  # NPC对话（服务端 -> 客户端）
    IDEducationResourceURI = 170  # 教育资源URI（服务端 -> 客户端）
    IDCreatePhoto = 171  # 创建照片（服务端 -> 客户端）
    IDUpdateSubChunkBlocks = 172  # 更新子区块方块（服务端 -> 客户端）
    IDPhotoInfoRequest = 173  # 照片信息请求（客户端 -> 服务端）
    IDSubChunk = 174  # 子区块（服务端 -> 客户端）
    IDSubChunkRequest = 175  # 子区块请求（客户端 -> 服务端）
    IDClientStartItemCooldown = 176  # 客户端开始物品冷却（客户端 -> 服务端）
    IDScriptMessage = 177  # 脚本消息（客户端 -> 服务端）
    IDCodeBuilderSource = 178  # 代码构建器源（客户端 -> 服务端）
    IDTickingAreasLoadStatus = 179  #  ticking 区域加载状态（服务端 -> 客户端）
    IDDimensionData = 180  # 维度数据（服务端 -> 客户端）
    IDAgentAction = 181  # 代理
    IDChangeMobProperty = 182  # 改变生物属性（服务端 -> 客户端）
    IDLessonProgress = 183  # 课程进度（客户端 -> 服务端）
    IDRequestAbility = 184  # 请求能力（客户端 -> 服务端）
    IDRequestPermissions = 185  # 请求权限（客户端 -> 服务端）
    IDToastRequest = 186  # 吐司请求（服务端 -> 客户端）
    IDUpdateAbilities = 187  # 更新能力（服务端 -> 客户端）
    IDUpdateAdventureSettings = 188  # 更新冒险设置（服务端 -> 客户端）
    IDDeathInfo = 189  # 死亡信息（服务端 -> 客户端）
    IDEditorNetwork = 190  # 编辑器网络（服务端 -> 客户端）
    IDFeatureRegistry = 191  # 特性注册表（服务端 -> 客户端）
    IDServerStats = 192  # 服务器统计（服务端 -> 客户端）
    IDRequestNetworkSettings = 193  # 请求网络设置（客户端 -> 服务端）
    IDGameTestRequest = 194  # 游戏测试请求（客户端 -> 服务端）
    IDGameTestResults = 195  # 游戏测试结果（服务端 -> 客户端）
    IDUpdateClientInputLocks = 196  # 更新客户端输入锁（服务端 -> 客户端）
    IDClientCheatAbility = 197  # 客户端作弊能力（客户端 -> 服务端）
    IDCameraPresets = 198  # 相机预设（服务端 -> 客户端）
    IDUnlockedRecipes = 199  # 已解锁配方（服务端 -> 客户端）
    IDPyRpc = 200  # Python远程过程调用（客户端 -> 服务端）
    IDChangeModel = 201  # 改变模型（服务端 -> 客户端）
    IDStoreBuySucc = 202  # 商店购买成功（服务端 -> 客户端）
    IDNeteaseJson = 203  # 网易 JSON（客户端 -> 服务端）
    IDChangeModelTexture = 204  # 改变模型纹理（服务端 -> 客户端）
    IDChangeModelOffset = 205  # 改变模型偏移（服务端 -> 客户端）
    IDChangeModelBind = 206  # 改变模型绑定（服务端 -> 客户端）
    IDHungerAttr = 207  # 饥饿属性（服务端 -> 客户端）
    IDSetDimensionLocalTime = 208  # 设置维度本地时间（服务端 -> 客户端）
    IDWithdrawFurnaceXp = 209  # 提取熔炉经验（客户端 -> 服务端）
    IDSetDimensionLocalWeather = 210  # 设置维度本地天气（服务端 -> 客户端）
    IDCustomV1 = 223  # 自定义 V1（服务端 -> 客户端）
    IDCombine = 224  # 组合（服务端 -> 客户端）
    IDVConnection = 225  # V 连接（服务端 -> 客户端）
    IDTransport = 226  # 传输（服务端 -> 客户端）
    IDCustomV2 = 227  # 自定义 V2（服务端 -> 客户端）
    IDConfirmSkin = 228  # 确认皮肤（服务端 -> 客户端）
    IDTransportNoCompress = 229  # 无压缩传输（服务端 -> 客户端）
    IDMobEffectV2 = 230  # 生物效果 V2（服务端 -> 客户端）
    IDMobBlockActorChanged = 231  # 生物方块实体改变（服务端 -> 客户端）
    IDChangeActorMotion = 232  # 改变实体运动（服务端 -> 客户端）
    IDAnimateEmoteEntity = 233  # 动画表情实体（服务端 -> 客户端）
    IDCameraInstruction = 300  # 相机指令（服务端 -> 客户端）
    IDCompressedBiomeDefinitionList = 301  # 压缩生物群系定义列表（服务端 -> 客户端）
    IDTrimData = 302  # 修剪数据（服务端 -> 客户端）
    IDOpenSign = 303  # 打开标志（服务端 -> 客户端）
    IDAgentAnimation = 304  # 代理动画（服务端 -> 客户端）


class ContainerType:
    ContainerTypeInventory = -1  # 物品栏
    ContainerTypeContainer = 0  # 容器
    ContainerTypeWorkbench = 1  # 工作台
    ContainerTypeFurnace = 2  # 熔炉
    ContainerTypeEnchantment = 3  # 附魔台
    ContainerTypeBrewingStand = 4  # 酿造台
    ContainerTypeAnvil = 5  # 铁砧
    ContainerTypeDispenser = 6  # 发射器
    ContainerTypeDropper = 7  # 投掷器
    ContainerTypeHopper = 8  # 漏斗
    ContainerTypeCauldron = 9  # 炼药锅
    ContainerTypeCartChest = 10  # 箱子矿车
    ContainerTypeCartHopper = 11  # 漏斗矿车
    ContainerTypeHorse = 12  # 马
    ContainerTypeBeacon = 13  # 信标
    ContainerTypeStructureEditor = 14  # 结构编辑器
    ContainerTypeTrade = 15  # 交易
    ContainerTypeCommandBlock = 16  # 命令方块
    ContainerTypeJukebox = 17  # 唱片机
    ContainerTypeArmour = 18  # 盔甲
    ContainerTypeHand = 19  # 手持
    ContainerTypeCompoundCreator = 20  # 化合物创建器
    ContainerTypeElementConstructor = 21  # 元素构造器
    ContainerTypeMaterialReducer = 22  # 材料分解器
    ContainerTypeLabTable = 23  # 实验台
    ContainerTypeLoom = 24  # 织布机
    ContainerTypeLectern = 25  # 讲台
    ContainerTypeGrindstone = 26  # 磨石
    ContainerTypeBlastFurnace = 27  # 高炉
    ContainerTypeSmoker = 28  # 烟熏炉
    ContainerTypeStonecutter = 29  # 切石机
    ContainerTypeCartography = 30  # 制图台
    ContainerTypeHUD = 31  # HUD
    ContainerTypeJigsawEditor = 32  # 拼图编辑器
    ContainerTypeSmithingTable = 33  # 锻造台
    ContainerTypeChestBoat = 34  # 箱子船
    ContainerTypeDecoratedPot = 35  # 装饰罐
    ContainerTypeCrafter = 36  # 工匠


class PlayerActionType:
    PlayerActionStartBreak = 0
    PlayerActionAbortBreak = 1
    PlayerActionStopBreak = 2
    PlayerActionGetUpdatedBlock = 3
    PlayerActionDropItem = 4
    PlayerActionStartSleeping = 5
    PlayerActionStopSleeping = 6
    PlayerActionRespawn = 7
    PlayerActionJump = 8
    PlayerActionStartSprint = 9
    PlayerActionStopSprint = 10
    PlayerActionStartSneak = 11
    PlayerActionStopSneak = 12
    PlayerActionCreativePlayerDestroyBlock = 13
    PlayerActionDimensionChangeDone = 14
    PlayerActionStartGlide = 15
    PlayerActionStopGlide = 16
    PlayerActionBuildDenied = 17
    PlayerActionCrackBreak = 18
    PlayerActionChangeSkin = 19
    PlayerActionSetEnchantmentSeed = 20
    PlayerActionStartSwimming = 21
    PlayerActionStopSwimming = 22
    PlayerActionStartSpinAttack = 23
    PlayerActionStopSpinAttack = 24
    PlayerActionStartBuildingBlock = 25
    PlayerActionPredictDestroyBlock = 26
    PlayerActionContinueDestroyBlock = 27
    PlayerActionStartItemUseOn = 28
    PlayerActionStopItemUseOn = 29
    PlayerActionHandledTeleport = 30
    PlayerActionMissedSwing = 31
    PlayerActionStartCrawling = 32
    PlayerActionStopCrawling = 33


class EffectIDS:
    EffectSpeed = "speed"  # 速度
    EffectSlowNess = "slowness"  # 缓慢
    EffectHaste = "haste"  # 急迫
    EffectMiningFatigue = "mining_fatigue"  # 挖掘疲劳
    EffectStrength = "strength"  # 力量
    EffectInstantHealth = "instant_health"  # 瞬间治疗
    EffectInstantDamage = "instant_damage"  # 瞬间伤害
    EffectJumpBoost = "jump_boost"  # 跳跃提升
    EffectNausea = "nausea"  # 反胃
    EffectRegenerAtion = "regeneration"  # 生命恢复
    EffectResistance = "resistance"  # 耐力
    EffectFireResistance = "fire_resistance"  # 火焰抗性
    EffectWaterBreathing = "water_breathing"  # 水下呼吸
    EffectInvisibility = "invisibility"  # 隐身
    EffectBlindness = "blindness"  # 致盲
    EffectNightVision = "night_vision"  # 夜视
    EffectHunger = "hunger"  # 饥饿
    EffectWeakness = "weakness"  # 虚弱
    EffectPoison = "poison"  # 中毒
    EffectWither = "wither"  # 凋零
    EffectHealthBoost = "health_boost"  # 生命提升
    EffectAbsorption = "absorption"  # 吸收
    EffectSaturation = "saturation"  # 饱和
    EffectLevitation = "levitation"  # 漂浮
    EffectFatalPoison = "fatal_poison"  # 中毒(致命)
    EffectConduitPower = "conduit_power"  # 潮涌能量
    EffectSlowFalling = "slow_falling"  # 缓慢落下
    EffectBadOmen = "bad_omen"  # 不详之兆
    EffectVillageHero = "village_hero"  # 村庄英雄
    EffectDarkNess = "darkness"  # 黑暗


class BuildStructureIDS:
    StructureBuriedTreasure = "buried_treasure"  # 埋藏宝藏
    StructureEndcity = "endcity"  # 末地城
    StructureFortress = "fortress"  # 下界要塞
    StructureMansion = "mansion"  # 林地府邸
    StructureMineShaft = "mineshaft"  # 废弃矿井
    StructureMonuMent = "monument"  # 海底遗迹
    StructurePillagerOutpost = "pillager_outpost"  # 掠夺者前哨站
    StructureRuins = "ruins"  # 水下遗迹
    StructureShipWreck = "shipwreck"  # 沉船
    StructureStrongHold = "stronghold"  # 要塞
    StructureTemple = "temple"  # 沙漠神殿/丛林神殿/沼泽小屋/雪屋
    StructureVillage = "village"  # 村庄


class ParticleIDS:
    ParticleArrowSpellEmitter = "arrow_spell_emitter"  # 从药箭上飘散的药水粒子
    ParticleBasicBubbleParticle = "basic_bubble_particle"  # 实体在水下产生的飞溅粒子，投射物在水下产生的轨迹粒子。该粒子只能在水中生成和存在。
    ParticleBasicBubbleParticleManual = "basic_bubble_particle_manual"  # 漂浮在水面上的实体产生的粒子，水下TNT被点燃时的气泡粒子。该粒子只能在水中生成和存在。
    ParticleBasicCritParticle = "basic_crit_particle"  # 用蓄力完成的弓或装填完成的弩射出的箭产生的轨迹粒子，尖牙进行攻击产生的粒子
    ParticleBasicFlameParticle = "basic_flame_particle"  # 火把；烧制物品的熔炉、高炉和烟熏炉；岩浆怪着地；刷怪笼工作
    ParticleBasicPortalParticle = "basic_portal_particle"  # 末影之眼的轨迹粒子
    ParticleBasicSmokeParticle = "basic_smoke_particle"  # 雨中的熔岩、岩浆块产生的粒子；伴随着lava_particle粒子产生的粒子；火、火把、灵魂火把的烟雾粒子；投掷器投掷物品；发射器发射物品；烈焰人；末地传送门；酿造台；正在工作的刷怪笼；烧制物品的熔炉、高炉、烟熏炉；点燃的蜡烛；凋灵；营火；凋零玫瑰；驯服生物失败；给棕色哞菇喂食小型花；使用末影之眼；试炼刷怪笼、宝库、实验台产出废物、制作加热块[仅教育版]；凋灵之首、火球的飞行轨迹粒子
    ParticleBlockDestruct = "block_destruct"  # 方块被摧毁；生物摔伤；玩家疾跑；羊吃草；兔子跳跃；嗅探兽刨挖；盔甲架被玩家破坏；使用刷子；实验台制作超级肥料[仅教育版]时的粒子；旋风人时的方块碎片粒子
    ParticleBlockSlide = "block_slide"  # 从蜂蜜块的侧面滑下的粒子
    ParticleBlueFlameParticle = "blue_flame_particle"  # 灵魂火把火苗粒子
    ParticleBreakingItemIcon = "breaking_item_icon"  # 玩家进食；狐狸进食；鸡蛋、喷溅药水、滞留药水、附魔之瓶、雪球和冰弹[仅教育版]破碎；史莱姆跳跃；海龟蛋孵化时的物品碎片粒子
    ParticleBreezeGroundParticle = "breeze_ground_particle"  # 旋风人产生的方块碎片粒子
    ParticleBreezeWindExplosionEmitter = "breeze_wind_explosion_emitter"  # 风弹爆炸粒子
    ParticleBubbleColumnBubble = "bubble_column_bubble"  # 气泡柱顶部的实体产生的气泡粒子。该粒子只能在水中生成和存在。
    # ------------------------------------> 待完成 <------------------------------------
