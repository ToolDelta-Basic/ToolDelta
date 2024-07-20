"数据包类构建器"

class PacketIDS:
	"数据包 ID 常量表"
	IDLogin = 1 # 客户端登陆(本地)
	IDPlayStatus = 2 # 玩家状态
	IDServerToClientHandshake = 3 # 服务端到客户端握手
	IDClientToServerHandshake = 4 # 客户端到服务端握手
	IDDisconnect = 5 # 断开连接
	IDResourcePacksInfo = 6 # 资源包信息(非常用)
	IDResourcePackStack = 7 # 资源包堆叠(非常用)
	IDResourcePackClientResponse = 8 # 资源包客户端响应(非常用)
	IDText = 9 # 文本消息
	IDSetTime = 10 # 更新客户端时间(服务端 -> 客户端)
	IDStartGame = 11 # 开始游戏
	IDAddPlayer = 112 # 添加玩家实体
	IDAddActor = 13 # 添加实体
	IDRemoveActor = 14 # 添加实体
	IDAddItemActor = 15 # 添加物品实体
	IDTakeItemActor = 17 # 捡起物品实体(动画)
	IDMoveActorAbsolute = 18 # 移动实体到绝对位置
	IDMovePlayer = 19 # 玩家移动(服务端 <-> 客户端)
	IDPassengerJump = 20 # 乘骑跳跃(客户端 -> 服务端)
	IDUpdateBlock = 21 # 更新方块(单方块修改)
	IDAddPainting = 22 # 添加绘画实体
	IDTickSync = 23 # 同步Tick(服务端 <-> 客户端)
	IDLevelSoundEventV1 = 24 # ???
	IDLevelEvent = 25 # 世界事件(服务端 -> 客户端)
	IDBlockEvent = 26 # 方块事件(服务端 -> 客户端)[打开箱子./././...]
	IDActorEvent = 27 # 实体事件(服务端 -> 客户端)[狼抖干自己./././...]
	IDMobEffect = 28 # 生物效果(服务端 -> 客户端)
	IDUpdateAttributes = 29 # 更新实体属性(服务端 -> 客户端)[移动速度./健康状况./...]
	IDInventoryTransaction = 30 # 物品交易(服务端 <- 客户端)
	IDMobEquipment = 31 # 实体物品持有(服务端 <-> 客户端)[僵尸手持石剑././...]
	IDMobArmourEquipment = 32 # 装备穿戴(服务端 -> 客户端)[玩家./僵尸./其他实体./...]
	IDInteract = 33 # 实体交互(弃用)
	IDBlockPickRequest = 34 # 拾取物品请求(客户端 -> 服务端)
	IDActorPickRequest = 35 # 拾取实体请求(客户端 -> 服务端)
	IDPlayerAction = 36 # 玩家行为(客户端 -> 服务端)
	IDHurtArmour = 38
	IDSetActorData = 39
	IDSetActorMotion = 40
	IDSetActorLink = 41
	IDSetHealth = 42
	IDSetSpawnPosition = 43
	IDAnimate = 44
	IDRespawn = 45
	IDContainerOpen = 46
	IDContainerClose = 47
	IDPlayerHotBar = 48
	IDInventoryContent = 49
	IDInventorySlot = 50
	IDContainerSetData = 51
	IDCraftingData = 52
	IDCraftingEvent = 53
	IDGUIDataPickItem = 54
	IDAdventureSettings = 55
	IDBlockActorData = 56
	IDPlayerInput = 57
	IDLevelChunk = 58
	IDSetCommandsEnabled = 59
	IDSetDifficulty = 60
	IDChangeDimension = 61
	IDSetPlayerGameType = 62
	IDPlayerList = 63
	IDSimpleEvent = 64
	IDEvent = 65
	IDSpawnExperienceOrb = 66 
	IDClientBoundMapItemData = 67
	IDMapInfoRequest = 68
	IDRequestChunkRadius = 69
	IDChunkRadiusUpdated = 70 
	IDItemFrameDropItem = 71 
	IDGameRulesChanged = 72 
	IDCamera = 73 
	IDBossEvent = 74 
	IDShowCredits = 75 
	IDAvailableCommands = 76 
	IDCommandRequest = 77 
	IDCommandBlockUpdate = 78 
	IDCommandOutput = 79 
	IDUpdateTrade = 80 
	IDUpdateEquip = 81 
	IDResourcePackDataInfo = 82 
	IDResourcePackChunkData = 83 
	IDResourcePackChunkRequest = 84 
	IDTransfer = 85 
	IDPlaySound = 86 
	IDStopSound = 87 
	IDSetTitle = 88 
	IDAddBehaviourTree = 89 
	IDStructureBlockUpdate = 90 
	IDShowStoreOffer = 91 
	IDPurchaseReceipt = 92
	IDPlayerSkin = 93 
	IDSubClientLogin = 94 
	IDAutomationClientConnect = 95 
	IDSetLastHurtBy = 96 
	IDBookEdit = 97 
	IDNPCRequest = 98 
	IDPhotoTransfer = 99 
	IDModalFormRequest = 100 
	IDModalFormResponse = 101 
	IDServerSettingsRequest = 102 
	IDServerSettingsResponse = 103 
	IDShowProfile = 104 
	IDSetDefaultGameType = 105 
	IDRemoveObjective = 106 
	IDSetDisplayObjective = 107 
	IDSetScore = 108 
	IDLabTable = 109 
	IDUpdateBlockSynced = 110 
	IDMoveActorDelta = 111 
	IDSetScoreboardIdentity = 112 
	IDSetLocalPlayerAsInitialised = 113 
	IDUpdateSoftEnum = 114 
	IDNetworkStackLatency = 115 
	IDScriptCustomEvent = 117 
	IDSpawnParticleEffect = 118 
	IDAvailableActorIdentifiers = 119 
	IDLevelSoundEventV2 = 120 
	IDNetworkChunkPublisherUpdate = 121 
	IDBiomeDefinitionList = 122 
	IDLevelSoundEvent = 123 
	IDLevelEventGeneric = 124 
	IDLecternUpdate = 125 
	IDAddEntity = 127 
	IDRemoveEntity = 128 
	IDClientCacheStatus = 129 
	IDOnScreenTextureAnimation = 130 
	IDMapCreateLockedCopy = 131 
	IDStructureTemplateDataRequest = 132 
	IDStructureTemplateDataResponse = 133 
	IDClientCacheBlobStatus = 135 
	IDClientCacheMissResponse = 136 
	IDEducationSettings = 137 
	IDEmote = 138 
	IDMultiPlayerSettings = 139 
	IDSettingsCommand = 140 
	IDAnvilDamage = 141 
	IDCompletedUsingItem = 142 
	IDNetworkSettings = 143 
	IDPlayerAuthInput = 144 
	IDCreativeContent = 145 
	IDPlayerEnchantOptions = 146 
	IDItemStackRequest = 147 
	IDItemStackResponse = 148 
	IDPlayerArmourDamage = 149 
	IDCodeBuilder = 150 
	IDUpdatePlayerGameType = 151 
	IDEmoteList = 152 
	IDPositionTrackingDBServerBroadcast = 153 
	IDPositionTrackingDBClientRequest = 154 
	IDDebugInfo = 155 
	IDPacketViolationWarning = 156 
	IDMotionPredictionHints = 157 
	IDAnimateEntity = 158 
	IDCameraShake = 159 
	IDPlayerFog = 160 
	IDCorrectPlayerMovePrediction = 161 
	IDItemComponent = 162 
	IDFilterText = 163 
	IDClientBoundDebugRenderer = 164 
	IDSyncActorProperty = 165 
	IDAddVolumeEntity = 166 
	IDRemoveVolumeEntity = 167 
	IDSimulationType = 168 
	IDNPCDialogue = 169 
	IDEducationResourceURI = 170 
	IDCreatePhoto = 171 
	IDUpdateSubChunkBlocks = 172 
	IDPhotoInfoRequest = 173 
	IDSubChunk = 174 
	IDSubChunkRequest = 175 
	IDClientStartItemCooldown = 176 
	IDScriptMessage = 177 
	IDCodeBuilderSource = 178 
	IDTickingAreasLoadStatus = 179 
	IDDimensionData = 180 
	IDAgentAction = 181 
	IDChangeMobProperty = 182 
	IDLessonProgress = 183 
	IDRequestAbility = 184 
	IDRequestPermissions = 185 
	IDToastRequest = 186 
	IDUpdateAbilities = 187 
	IDUpdateAdventureSettings = 188 
	IDDeathInfo = 189 
	IDEditorNetwork = 190 
	IDFeatureRegistry = 191 
	IDServerStats = 192 
	IDRequestNetworkSettings = 193 
	IDGameTestRequest = 194 
	IDGameTestResults = 195 
	IDUpdateClientInputLocks = 196 
	IDClientCheatAbility = 197 
	IDCameraPresets = 198 
	IDUnlockedRecipes = 199 
	IDPyRpc = 200 
	IDChangeModel = 201 
	IDStoreBuySucc = 202 
	IDNeteaseJson = 203 
	IDChangeModelTexture = 204 
	IDChangeModelOffset = 205 
	IDChangeModelBind = 206 
	IDHungerAttr = 207 
	IDSetDimensionLocalTime = 208 
	IDWithdrawFurnaceXp = 209 
	IDSetDimensionLocalWeather = 210 
	IDCustomV1 = 223
	IDCombine = 224
	IDVConnection = 225
	IDTransport = 226
	IDCustomV2 = 227
	IDConfirmSkin = 228
	IDTransportNoCompress = 229
	IDMobEffectV2 = 230
	IDMobBlockActorChanged = 231
	IDChangeActorMotion = 232
	IDAnimateEmoteEntity = 233
	IDCameraInstruction = 300
	IDCompressedBiomeDefinitionList = 301
	IDTrimData = 302
	IDOpenSign = 303
	IDAgentAnimation = 304

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
