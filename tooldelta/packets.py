"数据包类构建器"

class PacketIDS:
    "数据包 ID 常量表"
    IDLogin = 1
    IDPlayAddress = 2
    IDServerToClientHandshake = 3
    IDClientToServerHandshake = 4
    IDDisconnect = 5
    IDResourcePacksInfo = 6
    IDResourcePackStack = 7
    IDResourcePackClientResponse = 8
    Text = 9
    IDSetTime = 10
    IDStartGame = 11
    AddPlayer = 12
    IDAddActor = 13
    IDRemoveActor = 14
    IDAddItemActor = 15
    IDTakeItemActor = 17
    IDMoveActorAbsolute = 18
    IDMovePlayer = 19
    IDPassengerJump = 20
    IDUpdateBlock = 21
    IDAddPainting = 22
    IDTickSync = 23
    IDLevelEvent = 25
    IDBlockEvent = 26
    IDActorEvent = 27
    IDMobEffect = 28
    IDUpdateAttributes = 29
    IDInventoryTransaction = 30
    IDMobEquipment = 31
    IDMobArmourEquipment = 32
    IDInteract = 33
    IDBlockPickRequest = 34
    IDActorPickRequest = 35
    IDPlayerAction = 36
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
    PlayerList = 63
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
    CommandOutput = 79
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
    IDSpawnParticleEffects = 118
    IDAvailableActorIdentifiers = 119
    IDNetworkChunKPublisherUpdate = 121
    IDBiomeDefinitionList = 122
    IDLevelSoundEvent = 123
    IDLevelEventGeneric = 124
    IDLecternUpdate = 125
    IDAddEntity = 127
    IDRemoveEntity = 128
    IDClientCacheStatus = 129
    IDMapCreateLockedCopy = 130
    IDOnScreenTextureAnimation = 131
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
    IDPyRpc = 183
# 以下是对数据包名称的机翻内容, 仅供参考
# 数据包名称来源于Go-Mc的ID表
# 1-ID 登录
# 2-ID 游戏地址
# 3-ID 服务器到客户端握手
# 4-ID 客户端到服务器握手
# 5-ID 断开连接
# 6-ID 资源包信息
# 7-ID 资源包堆栈
# 8-ID 资源包客户端响应
# 9-ID 文本
# 10-ID 设置时间
# 11-ID 开始游戏
# 12-ID 添加玩家
# 13-ID 添加角色
# 14-ID 移除角色
# 15-ID 添加物品角色
# 16-_
# 17-ID 移除物品角色
# 18-ID 绝对移动角色
# 19-ID 移动玩家
# 20-ID 乘客跳跃
# 21-ID 更新方块
# 22-ID 添加绘画
# 23-ID 同步计时器
# 24-_
# 25-ID 级别事件
# 26-ID 方块事件
# 27-ID 角色事件
# 28-ID 生物效果
# 29-ID 更新属性
# 30-ID 物品交易
# 31-ID 生物装备
# 32-ID 生物装甲装备
# 33-ID 交互
# 34-ID 方块拾取请求
# 35-ID 角色拾取请求
# 36-ID 玩家动作
# 37-_
# 38-ID 伤害装甲
# 39-ID 设置角色数据
# 40-ID 设置角色动作
# 41-ID 设置角色链接
# 42-ID 设置健康
# 43-ID 设置出生位置
# 44-ID 动画
# 45-ID 重生
# 46-ID 容器打开
# 47-ID 容器关闭
# 48-ID 玩家热条
# 49-ID 物品内容
# 50-ID 物品槽
# 51-ID 容器设置数据
# 52-ID 制作数据
# 53-ID 制作事件
# 54-ID GUI 数据（拾取物品）
# 55-ID 冒险设置
# 56-ID 方块角色数据
# 57-ID 玩家输入
# 58-ID 级别方块
# 59-ID 设置命令启用状态
# 60-ID 设置难度
# 61-ID 改变维度
# 62-ID 设置玩家游戏类型
# 63-ID 玩家列表
# 64-ID 简单事件
# 65-ID 事件
# 66-ID 生成经验球
# 67-ID 客户端绑定地图物品数据
# 68-ID 地图信息请求ID 请求 Chunk 半径
# 69-ID Chunk 半径更新
# 70-ID 项目框架掉落物品
# 71-ID 游戏规则更改
# 72-ID 摄像头
# 73-ID 老板事件
# 74-ID 显示版权信息
# 75-ID 可用命令
# 76-ID 命令请求
# 77-ID 命令块更新
# 78-ID 命令输出
# 79-ID 更新贸易
# 80-ID 更新装备
# 81-ID 资源包数据信息
# 82-ID 资源包 Chunk 数据
# 83-ID 资源包 Chunk 请求
# 84-ID 传输
# 85-ID 播放声音
# 86-ID 停止声音
# 87-ID 设置标题
# 88-ID 添加行为树
# 89-ID 结构块更新
# 90-ID 显示商店促销
# 91-ID 购买收据
# 92-ID 玩家皮肤
# 93-ID 子客户端登录
# 94-ID 自动化客户端连接
# 95-ID 设置最后伤害来源
# 96-ID 书籍编辑
# 97-ID NPC 请求
# 98-ID 照片传输
# 99-ID 模态表单请求
# 100-ID 模态表单响应
# 101-ID 服务器设置请求
# 102-ID 服务器设置响应
# 103-ID 显示个人资料
# 104-ID 设置默认游戏类型
# 105-ID 移除目标
# 106-ID 设置显示目标
# 107-ID 设置得分
# 108-ID 实验室表格
# 109-ID 更新块同步
# 110-ID 移动演员 Delta
# 111-ID 设置得分板身份
# 112-ID 设置本地玩家为初始化状态
# 113-ID 更新软枚举
# 114-ID 网络栈延迟
# 115-_
# 116-ID 脚本自定义事件
# 117-ID 生成粒子特效
# 118-ID 可用演员标识符
# 119-_
# 120-ID 网络 Chunk 发布者更新
# 121-ID 生物群系定义列表
# 122-ID 水平声音事件
# 123-ID 水平事件通用
# 124-ID 讲台更新
# 125-_
# 126-ID 添加实体ID 移除实体
# 127-ID 客户端缓存状态
# 128-ID 地图创建锁定副本
# 129-ID 屏幕纹理动画
# 130-ID 结构模板数据请求
# 131-ID 结构模板数据响应
# 132-_
# 133-ID 客户端缓存blob状态
# 134-ID 客户端缓存缺失响应
# 135-ID 教育设置
# 136-ID 表情
# 137-ID 多人游戏设置
# 138-ID 设置命令
# 139-ID 锻造伤害
# 140-ID 使用物品完成
# 141-ID 网络设置
# 142-ID 玩家身份验证输入
# 143-ID 创意内容
# 144-ID 玩家附魔选项
# 145-ID 物品堆叠请求
# 146-ID 物品堆叠响应
# 147-ID 玩家护甲伤害
# 148-ID 代码构建器
# 149-ID 更新玩家游戏类型
# 150-ID 表情列表
# 151-ID 位置跟踪DB服务器广播
# 152-ID 位置跟踪DB客户端请求
# 153-ID 调试信息
# 154-ID 包违规警告
# 155-ID 运动预测提示
# 156-ID 动画实体
# 157-ID 摄像机震动
# 158-ID 玩家雾
# 159-ID 纠正玩家运动预测
# 160-ID 物品组件
# 161-ID 过滤文本
# 162-ID 客户端边界调试渲染器
# 163-ID 同步演员属性
# 164-ID 添加体积实体
# 165-ID 移除体积实体
# 166-ID 模拟类型
# 167-ID NPC对话
# 168-ID 教育资源URI
# 169-ID 创建照片
# 170-ID 更新子方块块
# 171-ID 照片信息请求
# 172-ID 子方块
# 173-ID 子方块请求
# 174-ID 客户端开始物品冷却
# 175-ID 脚本消息
# 176-ID 代码构建器源
# 177-ID 计时区域加载状态
# 178-ID 维度数据ID 代理动作：
# 179-ID 变更移动财产：
# 180-ID PyRpc

class SubPacket_CmdOutputMsg:
    """命令输出消息子包构建"""
    Success: bool
    Message: str
    Parameters: list[str]

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
