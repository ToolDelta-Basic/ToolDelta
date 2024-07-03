"数据包类构建器"

from dataclasses import dataclass


@dataclass
class PacketIDS:
    "数据包 ID 常量表"

    IDLogin = 1  # 登录
    IDPlayStatus = 2  # 播放地址
    IDServerToClientHandshake = 3  # 服务器到客户端握手
    IDClientToServerHandshake = 4  # 客户端到服务器握手
    IDDisconnect = 5  # 断开连接
    IDResourcePacksInfo = 6  # 资源包信息
    IDResourcePackStack = 7  # 资源包堆栈
    IDResourcePackClientResponse = 8  # 资源包客户端响应
    Text = 9  # 文本
    IDSetTime = 10  # 设置时间
    IDStartGame = 11  # 开始游戏
    AddPlayer = 12  # 添加玩家
    IDAddActor = 13  # 添加演员
    IDRemoveActor = 14  # 移除演员
    IDAddItemActor = 15  # 添加物品演员
    IDTakeItemActor = 17  # 拿取物品演员
    IDMoveActorAbsolute = 18  # 绝对移动演员
    IDMovePlayer = 19  # 移动玩家
    IDPassengerJump = 20  # 乘客跳跃
    IDUpdateBlock = 21  # 更新方块
    IDAddPainting = 22  # 添加绘画
    IDTickSync = 23  # 时序同步
    IDLevelEvent = 25  # 关卡事件
    IDBlockEvent = 26  # 方块事件
    IDActorEvent = 27  # 演员事件
    IDMobEffect = 28  # 生物效果
    IDUpdateAttributes = 29  # 更新属性
    IDInventoryTransaction = 30  # 库存交易
    IDMobEquipment = 31  # 生物装备
    IDMobArmourEquipment = 32  # 生物护甲装备
    IDInteract = 33  # 交互
    IDBlockPickRequest = 34  # 方块拾取请求
    IDActorPickRequest = 35  # 演员拾取请求
    IDPlayerAction = 36  # 玩家动作
    IDHurtArmour = 38  # 伤害护甲
    IDSetActorData = 39  # 设置演员数据
    IDSetActorMotion = 40  # 设置演员运动
    IDSetActorLink = 41  # 设置演员链接
    IDSetHealth = 42  # 设置生命值
    IDSetSpawnPosition = 43  # 设置生成位置
    IDAnimate = 44  # 动画
    IDRespawn = 45  # 重生
    IDContainerOpen = 46  # 容器打开
    IDContainerClose = 47  # 容器关闭
    IDPlayerHotBar = 48  # 玩家热键栏
    IDInventoryContent = 49  # 库存内容
    IDInventorySlot = 50  # 库存槽
    IDContainerSetData = 51  # 容器设置数据
    IDCraftingData = 52  # 合成数据
    IDCraftingEvent = 53  # 合成事件
    IDGUIDataPickItem = 54  # GUI 数据选择物品
    IDAdventureSettings = 55  # 冒险设置
    IDBlockActorData = 56  # 方块演员数据
    IDPlayerInput = 57  # 玩家输入
    IDLevelChunk = 58  # 关卡区块
    IDSetCommandsEnabled = 59  # 设置命令启用
    IDSetDifficulty = 60  # 设置难度
    IDChangeDimension = 61  # 改变维度
    IDSetPlayerGameType = 62  # 设置玩家游戏类型
    PlayerList = 63  # 玩家列表
    IDSimpleEvent = 64  # 简单事件
    IDEvent = 65  # 事件
    IDSpawnExperienceOrb = 66  # 生成经验球
    IDClientBoundMapItemData = 67  # 客户端限定地图物品数据
    IDMapInfoRequest = 68  # 地图信息请求
    IDRequestChunkRadius = 69  # 请求区块半径
    IDChunkRadiusUpdated = 70  # 区块半径更新
    IDItemFrameDropItem = 71  # 物品框丢弃物品
    IDGameRulesChanged = 72  # 游戏规则变更
    IDCamera = 73  # 摄像头
    IDBossEvent = 74  # 首领事件
    IDShowCredits = 75  # 展示信用
    IDAvailableCommands = 76  # 可用命令
    IDCommandRequest = 77  # 命令请求
    IDCommandBlockUpdate = 78  # 命令方块更新
    CommandOutput = 79  # 命令输出
    IDUpdateTrade = 80  # 更新交易
    IDUpdateEquip = 81  # 更新装备
    IDResourcePackDataInfo = 82  # 资源包数据信息
    IDResourcePackChunkData = 83  # 资源包块数据
    IDResourcePackChunkRequest = 84  # 资源包块请求
    IDTransfer = 85  # 传输
    IDPlaySound = 86  # 播放声音
    IDStopSound = 87  # 停止声音
    IDSetTitle = 88  # 设置标题
    IDAddBehaviourTree = 89  # 添加行为树
    IDStructureBlockUpdate = 90  # 结构块更新
    IDShowStoreOffer = 91  # 展示商店提供
    IDPurchaseReceipt = 92  # 购买凭据
    IDPlayerSkin = 93  # 玩家皮肤
    IDSubClientLogin = 94  # 子客户端登录
    IDAutomationClientConnect = 95  # 自动化客户端连接
    IDSetLastHurtBy = 96  # 设置最后受伤者
    IDBookEdit = 97  # 编辑书籍
    IDNPCRequest = 98  # NPC 请求
    IDPhotoTransfer = 99  # 照片传输
    IDModalFormRequest = 100  # 模态窗口请求
    IDModalFormResponse = 101  # 模态窗口响应
    IDServerSettingsRequest = 102  # 服务器设置请求
    IDServerSettingsResponse = 103  # 服务器设置响应
    IDShowProfile = 104  # 展示配置文件
    IDSetDefaultGameType = 105  # 设置默认游戏类型
    IDRemoveObjective = 106  # 移除目标
    IDSetDisplayObjective = 107  # 设置显示目标
    IDSetScore = 108  # 设置分数
    IDLabTable = 109  # 实验室桌
    IDUpdateBlockSynced = 110  # 更新同步方块
    IDMoveActorDelta = 111  # 移动演员增量
    IDSetScoreboardIdentity = 112  # 设置计分板标识
    IDSetLocalPlayerAsInitialised = 113  # 设置初始本地玩家
    IDUpdateSoftEnum = 114  # 更新软枚举
    IDNetworkStackLatency = 115  # 网络堆栈延迟
    IDScriptCustomEvent = 117  # 脚本自定义事件
    IDSpawnParticleEffects = 118  # 生成粒子效果
    IDAvailableActorIdentifiers = 119  # 可用演员标识
    IDNetworkChunKPublisherUpdate = 121  # 网络区块发布者更新
    IDBiomeDefinitionList = 122  # 生物群落定义列表
    IDLevelSoundEvent = 123  # 关卡声音事件
    IDLevelEventGeneric = 124  # 关卡通用事件
    IDLecternUpdate = 125  # 讲台更新
    IDAddEntity = 127  # 添加实体
    IDRemoveEntity = 128  # 移除实体
    IDClientCacheStatus = 129  # 客户端缓存状态
    IDMapCreateLockedCopy = 130  # 创建地图锁定副本
    IDOnScreenTextureAnimation = 131  # 屏幕上纹理动画
    IDStructureTemplateDataRequest = 132  # 结构模板数据请求
    IDStructureTemplateDataResponse = 133  # 结构模板数据响应
    IDClientCacheBlobStatus = 135  # 客户端缓存块状态
    IDClientCacheMissResponse = 136  # 客户端缓存未命中响应
    IDEducationSettings = 137  # 教育设置
    IDEmote = 138  # 表情
    IDMultiPlayerSettings = 139  # 多人游戏设置
    IDSettingsCommand = 140  # 设置命令
    IDAnvilDamage = 141  # 铁砧伤害
    IDCompletedUsingItem = 142  # 使用物品完成
    IDNetworkSettings = 143  # 网络设置
    IDPlayerAuthInput = 144  # 玩家认证输入
    IDCreativeContent = 145  # 创造性内容
    IDPlayerEnchantOptions = 146  # 玩家附魔选项
    IDItemStackRequest = 147  # 物品堆请求
    IDItemStackResponse = 148  # 物品堆响应
    IDPlayerArmourDamage = 149  # 玩家护甲伤害
    IDCodeBuilder = 150  # 代码构建
    IDUpdatePlayerGameType = 151  # 更新玩家游戏类型
    IDEmoteList = 152  # 表情列表
    IDPositionTrackingDBServerBroadcast = 153  # 位置追踪数据库服务器广播
    IDPositionTrackingDBClientRequest = 154  # 位置追踪数据库客户端请求
    IDDebugInfo = 155  # 调试信息
    IDPacketViolationWarning = 156  # 数据包违规警告
    IDMotionPredictionHints = 157  # 运动预测提示
    IDAnimateEntity = 158  # 动画实体
    IDCameraShake = 159  # 摄像头震动
    IDPlayerFog = 160  # 玩家迷雾
    IDCorrectPlayerMovePrediction = 161  # 纠正玩家移动预测
    IDItemComponent = 162  # 物品组件
    IDFilterText = 163  # 过滤文本
    IDClientBoundDebugRenderer = 164  # 客户端限定调试渲染器
    IDSyncActorProperty = 165  # 同步演员属性
    IDAddVolumeEntity = 166  # 添加体积实体
    IDRemoveVolumeEntity = 167  # 移除体积实体
    IDSimulationType = 168  # 模拟类型
    IDNPCDialogue = 169  # NPC 对话
    IDEducationResourceURI = 170  # 教育资源 URI
    IDCreatePhoto = 171  # 创建照片
    IDUpdateSubChunkBlocks = 172  # 更新子区块方块
    IDPhotoInfoRequest = 173  # 照片信息请求
    IDSubChunk = 174  # 子区块
    IDSubChunkRequest = 175  # 子区块请求
    IDClientStartItemCooldown = 176  # 客户端开始物品冷却
    IDScriptMessage = 177  # 脚本消息
    IDCodeBuilderSource = 178  # 代码构建源
    IDTickingAreasLoadStatus = 179  # 区域加载状态
    IDDimensionData = 180  # 维度数据
    IDAgentAction = 181  # 代理行动
    IDChangeMobProperty = 182  # 改变生物属性
    IDPyRpc = 183  # Python 远程过程调用


@dataclass
class ActorEventType:
    "演员事件常量表"

    ActorEventJump = 1  # 角色跳跃
    ActorEventHurt = 2  # 角色受伤
    ActorEventDeath = 3  # 角色死亡
    ActorEventStartAttacking = 4  # 开始攻击
    ActorEventStopAttacking = 5  # 停止攻击
    ActorEventTamingFailed = 6  # 驯服失败
    ActorEventTamingSucceeded = 7  # 驯服成功
    ActorEventShakeWetness = 8  # 摇动湿度
    ActorEventUseItem = 9  # 使用物品
    ActorEventEatGrass = 10  # 吃草
    ActorEventFishhookBubble = 11  # 鱼钩泡泡
    ActorEventFishhookFishPosition = 12  # 鱼钩鱼位置
    ActorEventFishhookHookTime = 13  # 鱼钩勾住时间
    ActorEventFishhookTease = 14  # 鱼钩逗弄
    ActorEventSquidFleeing = 15  # 乌贼逃离
    ActorEventZombieConverting = 16  # 僵尸转换
    ActorEventPlayAmbient = 17  # 播放环境音乐
    ActorEventSpawnAlive = 18  # 产生生物
    ActorEventStartOfferFlower = 19  # 开始献花
    ActorEventStopOfferFlower = 20  # 停止献花
    ActorEventLoveHearts = 21  # 爱心
    ActorEventVillagerAngry = 22  # 村民生气
    ActorEventVillagerHappy = 23  # 村民开心
    ActorEventWitchHatMagic = 24  # 女巫帽子魔法
    ActorEventFireworksExplode = 25  # 烟花爆炸
    ActorEventInLoveHearts = 26  # 爱心飞扬
    ActorEventSilverfishMergeAnimation = 27  # 银鱼合并动画
    ActorEventGuardianAttackSound = 28  # 守卫者攻击音效
    ActorEventDrinkPotion = 29  # 喝药水
    ActorEventThrowPotion = 30  # 扔药水
    ActorEventCartWithPrimeTNT = 31  # 载有 TNT 的车
    ActorEventPrimeCreeper = 32  # 充能的爬行者
    ActorEventAirSupply = 33  # 空气供应
    ActorEventAddPlayerLevels = 34  # 增加玩家等级
    ActorEventGuardianMiningFatigue = 35  # 守卫者挖掘疲劳
    ActorEventAgentSwingArm = 36  # 代理摆动手臂
    ActorEventDragonStartDeathAnim = 37  # 龙开始死亡动画
    ActorEventGroundDust = 38  # 地面灰尘
    ActorEventShake = 39  # 摇动
    ActorEventFeed = 57  # 喂养角色
    ActorEventBabyEat = 60  # 宝宝吃东西
    ActorEventInstantDeath = 61  # 瞬间死亡
    ActorEventNotifyTrade = 62  # 通知交易
    ActorEventLeashDestroyed = 63  # 绳索被销毁
    ActorEventCaravanUpdated = 64  # 更新马车
    ActorEventTalismanActivate = 65  # 法宝激活
    ActorEventUpdateStructureFeature = 66  # 更新结构特征
    ActorEventPlayerSpawnedMob = 67  # 玩家产生的生物
    ActorEventPuke = 68  # 呕吐
    ActorEventUpdateStackSize = 69  # 更新堆叠大小
    ActorEventStartSwimming = 70  # 开始游泳
    ActorEventBalloonPop = 71  # 气球爆破
    ActorEventTreasureHunt = 72  # 寻宝
    ActorEventSummonAgent = 73  # 召唤代理
    ActorEventFinishedChargingCrossbow = 74  # 弩完成充能
    ActorEventLandedOnGround = 75  # 降落在地面
    ActorEventActorGrowUp = 76  # 角色成长
    ActorEventVibrationDetected = 77  # 检测到振动


@dataclass
class EventType:
    "事件类型常量表"

    EventTypeAchievementAwarded = 0  # 成就奖励
    EventTypeEntityInteract = 1  # 实体交互
    EventTypePortalBuilt = 2  # 传送门建立
    EventTypePortalUsed = 3  # 传送门使用
    EventTypeMobKilled = 4  # 生物被杀
    EventTypeCauldronUsed = 5  # 釜子使用
    EventTypePlayerDied = 6  # 玩家死亡
    EventTypeBossKilled = 7  # Boss 被杀
    EventTypeAgentCommand = 8  # 代理命令
    EventTypeAgentCreated = 9  # 代理创建（目前无用？）
    EventTypePatternRemoved = 10  # 模式移除
    EventTypeSlashCommandExecuted = 11  # 斜杠命令执行
    EventTypeFishBucketed = 12  # 鱼桶
    EventTypeMobBorn = 13  # 生物出生
    EventTypePetDied = 14  # 宠物死亡
    EventTypeCauldronInteract = 15  # 釜子交互
    EventTypeComposterInteract = 16  # 堆肥桶交互
    EventTypeBellUsed = 17  # 钟声
    EventTypeEntityDefinitionTrigger = 18  # 实体定义触发
    EventTypeRaidUpdate = 19  # 袭击更新
    EventTypeMovementAnomaly = 20  # 移动异常
    EventTypeMovementCorrected = 21  # 移动校正
    EventTypeExtractHoney = 22  # 提取蜂蜜
    EventTypeTargetBlockHit = 23  # 目标方块被击中
    EventTypePiglinBarter = 24  # 畏怯者交易
    EventTypePlayerWaxedOrUnwaxedCopper = 25  # 玩家给覆蜡/未覆蜡铜
    EventTypeCodeBuilderRuntimeAction = 26  # 代码构建器运行时动作
    EventTypeCodeBuilderScoreboard = 27  # 代码构建器计分板
    EventTypeStriderRiddenInLavaInOverworld = 28  # 熔岩中骑猪灵
    EventTypeSneakCloseToSculkSensor = 29  # 靠近鸾石感应器潜行


@dataclass
class PlayerActionType:
    PlayerActionStartBreak = 0  # 玩家开始破坏
    PlayerActionAbortBreak = 1  # 取消破坏
    PlayerActionStopBreak = 2  # 停止破坏
    PlayerActionGetUpdatedBlock = 3  # 获取更新的方块
    PlayerActionDropItem = 4  # 丢弃物品
    PlayerActionStartSleeping = 5  # 开始睡觉
    PlayerActionStopSleeping = 6  # 停止睡觉
    PlayerActionRespawn = 7  # 重生
    PlayerActionJump = 8  # 跳跃
    PlayerActionStartSprint = 9  # 开始冲刺
    PlayerActionStopSprint = 10  # 停止冲刺
    PlayerActionStartSneak = 11  # 开始潜行
    PlayerActionStopSneak = 12  # 停止潜行
    PlayerActionCreativePlayerDestroyBlock = 13  # 创造模式下玩家摧毁方块
    PlayerActionDimensionChangeDone = 14  # 维度切换完成
    PlayerActionStartGlide = 15  # 开始滑翔
    PlayerActionStopGlide = 16  # 停止滑翔
    PlayerActionBuildDenied = 17  # 建造被拒绝
    PlayerActionCrackBreak = 18  # 破坏进度
    PlayerActionChangeSkin = 19  # 更换皮肤
    PlayerActionSetEnchantmentSeed = 20  # 设置附魔种子
    PlayerActionStartSwimming = 21  # 开始游泳
    PlayerActionStopSwimming = 22  # 停止游泳
    PlayerActionStartSpinAttack = 23  # 开始旋转攻击
    PlayerActionStopSpinAttack = 24  # 停止旋转攻击
    PlayerActionStartBuildingBlock = 25  # 开始建造方块
    PlayerActionPredictDestroyBlock = 26  # 预测破坏方块
    PlayerActionContinueDestroyBlock = 27  # 继续破坏方块
    PlayerActionStartItemUseOn = 28  # 开始使用物品
    PlayerActionStopItemUseOn = 29  # 停止使用物品


class SubPacket_CmdOutputMsg:
    """命令输出消息子包构建"""

    Success: bool
    Message: str
    Parameters: list

    def __init__(self, pkt: dict):
        self.Success = pkt["Success"]
        self.Parameters = pkt["Parameters"]
        self.Message = pkt["Message"]


class SubPacket_CmdOrigin:
    "命令来源子包构建"

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
    "命令输出包构建"

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
