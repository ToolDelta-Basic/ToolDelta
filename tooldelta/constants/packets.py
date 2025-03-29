from enum import IntEnum


class PacketIDs(IntEnum):
    "数据包 ID 常量表"

    # https://prismarinejs.github.io/minecraft-data/protocol/bedrock/1.21.42/#Action

    IDLogin = Login = 1  # 客户端登录（本地）
    IDPlayStatus = PlayStatus = 2  # 玩家状态
    IDServerToClientHandshake = ServerToClientHandshake = 3  # 服务端到客户端握手
    IDClientToServerHandshake = ClientToServerHandshake = 4  # 客户端到服务端握手
    IDDisconnect = Disconnect = 5  # 断开连接
    IDResourcePacksInfo = ResourcePacksInfo = 6  # 资源包信息（非常用）
    IDResourcePackStack = ResourcePackStack = 7  # 资源包堆叠（非常用）
    IDResourcePackClientResponse = ResourcePackClientResponse = (
        8  # 资源包客户端响应（非常用）
    )
    IDText = Text = 9  # 文本消息
    IDSetTime = SetTime = 10  # 更新客户端时间（服务端 -> 客户端）
    IDStartGame = StartGame = 11  # 开始游戏
    IDAddPlayer = AddPlayer = 12  # 添加玩家实体
    IDAddActor = AddActor = 13  # 添加实体
    IDRemoveActor = RemoveActor = 14  # 添加实体
    IDAddItemActor = AddItemActor = 15  # 添加物品实体
    IDTakeItemActor = TakeItemActor = 17  # 捡起物品实体（动画）
    IDMoveActorAbsolute = MoveActorAbsolute = 18  # 移动实体到绝对位置
    IDMovePlayer = MovePlayer = 19  # 玩家移动（服务端 <-> 客户端）
    IDPassengerJump = PassengerJump = 20  # 乘骑跳跃（客户端 -> 服务端）
    IDUpdateBlock = UpdateBlock = 21  # 更新方块（单方块修改）
    IDAddPainting = AddPainting = 22  # 添加绘画实体
    IDTickSync = TickSync = 23  # 同步Tick（服务端 <-> 客户端）
    IDLevelSoundEventV1 = LevelSoundEventV1 = 24  # ???
    IDLevelEvent = LevelEvent = 25  # 世界事件（服务端 -> 客户端）
    IDBlockEvent = BlockEvent = 26  # 方块事件（服务端 -> 客户端）[打开箱子./././...]
    IDActorEvent = ActorEvent = 27  # 实体事件（服务端 -> 客户端）[狼抖干自己./././...]
    IDMobEffect = MobEffect = 28  # 生物效果（服务端 -> 客户端）
    IDUpdateAttributes = UpdateAttributes = (
        29  # 更新实体属性（服务端 -> 客户端）[移动速度./健康状况./...]
    )
    IDInventoryTransaction = InventoryTransaction = 30  # 物品交易（服务端 <- 客户端）
    IDMobEquipment = MobEquipment = (
        31  # 实体物品持有（服务端 <-> 客户端）[僵尸手持石剑././...]
    )
    IDMobArmourEquipment = MobArmourEquipment = (
        32  # 装备穿戴（服务端 -> 客户端）[玩家./僵尸./其他实体./...]
    )
    IDInteract = Interact = 33  # 实体交互（弃用）
    IDBlockPickRequest = BlockPickRequest = 34  # 拾取物品请求（客户端 -> 服务端）
    IDActorPickRequest = ActorPickRequest = 35  # 拾取实体请求（客户端 -> 服务端）
    IDPlayerAction = PlayerAction = 36  # 玩家行为（客户端 -> 服务端）
    IDHurtArmour = HurtArmour = 38  # 盔甲损害（服务端 -> 客户端）
    IDSetActorData = SetActorData = (
        39  # 实体元数据（服务端 -> 客户端）[实体是否着火././...]
    )
    IDSetActorMotion = SetActorMotion = 40  # 设置客户端速度（服务端 -> 客户端）
    IDSetActorLink = SetActorLink = 41  # 设置实体乘骑（服务端 -> 客户端）
    IDSetHealth = SetHealth = 42  # 设置玩家血量（服务端 -> 客户端）
    IDSetSpawnPosition = SetSpawnPosition = 43  # 设置玩家出生点位置（服务端 -> 客户端）
    IDAnimate = Animate = 44  # 动画效果（服务端 -> 客户端）
    IDRespawn = Respawn = 45  # 重生（服务端 <-> 客户端）
    IDContainerOpen = ContainerOpen = 46  # 打开容器（服务端 -> 客户端）
    IDContainerClose = ContainerClose = 47  # 关闭容器（服务端 -> 客户端）
    IDPlayerHotBar = PlayerHotBar = 48  # 玩家快捷栏槽位（服务端 -> 客户端）
    IDInventoryContent = InventoryContent = 49  # 更新玩家背包（服务端 -> 客户端）
    IDInventorySlot = InventorySlot = 50  # 玩家背包单槽位更新（服务端 -> 客户端）
    IDContainerSetData = ContainerSetData = 51  # 容器设置数据（服务端 -> 客户端）
    IDCraftingData = CraftingData = 52  # 合成数据（服务端 -> 客户端）
    IDCraftingEvent = CraftingEvent = 53  # 合成事件（客户端 -> 服务端）
    IDGUIDataPickItem = GUIDataPickItem = 54  # GUI数据拾取物品（客户端 -> 服务端）
    IDAdventureSettings = AdventureSettings = 55  # 冒险设置（服务端 -> 客户端）
    IDBlockActorData = BlockActorData = 56  # 方块实体数据（服务端 -> 客户端）
    IDPlayerInput = PlayerInput = 57  # 玩家输入（客户端 -> 服务端）
    IDLevelChunk = LevelChunk = 58  # 区块数据（服务端 -> 客户端）
    IDSetCommandsEnabled = SetCommandsEnabled = 59  # 设置命令启用（服务端 -> 客户端）
    IDSetDifficulty = SetDifficulty = 60  # 设置难度（服务端 -> 客户端）
    IDChangeDimension = ChangeDimension = 61  # 改变维度（服务端 -> 客户端）
    IDSetPlayerGameType = SetPlayerGameType = 62  # 设置玩家游戏类型（服务端 -> 客户端）
    IDPlayerList = PlayerList = 63  # 玩家列表（服务端 -> 客户端）
    IDSimpleEvent = SimpleEvent = 64  # 简单事件（服务端 -> 客户端）
    IDEvent = Event = 65  # 事件（服务端 -> 客户端）
    IDSpawnExperienceOrb = SpawnExperienceOrb = 66  # 生成经验球（服务端 -> 客户端）
    IDClientBoundMapItemData = ClientBoundMapItemData = (
        67  # 客户端绑定地图物品数据（服务端 -> 客户端）
    )
    IDMapInfoRequest = MapInfoRequest = 68  # 地图信息请求（客户端 -> 服务端）
    IDRequestChunkRadius = RequestChunkRadius = 69  # 请求区块半径（客户端 -> 服务端）
    IDChunkRadiusUpdated = ChunkRadiusUpdated = 70  # 区块半径更新（服务端 -> 客户端）
    IDItemFrameDropItem = ItemFrameDropItem = (
        71  # 物品展示框掉落物品（服务端 -> 客户端）
    )
    IDGameRulesChanged = GameRulesChanged = 72  # 游戏规则改变（服务端 -> 客户端）
    IDCamera = Camera = 73  # 相机（服务端 -> 客户端）
    IDBossEvent = BossEvent = 74  # Boss事件（服务端 -> 客户端）
    IDShowCredits = ShowCredits = 75  # 显示 credits（服务端 -> 客户端）
    IDAvailableCommands = AvailableCommands = 76  # 可用命令（服务端 -> 客户端）
    IDCommandRequest = CommandRequest = 77  # 命令请求（客户端 -> 服务端）
    IDCommandBlockUpdate = CommandBlockUpdate = 78  # 命令块更新（客户端 -> 服务端）
    IDCommandOutput = CommandOutput = 79  # 命令输出（服务端 -> 客户端）
    IDUpdateTrade = UpdateTrade = 80  # 更新交易（服务端 -> 客户端）
    IDUpdateEquip = UpdateEquip = 81  # 更新装备（服务端 -> 客户端）
    IDResourcePackDataInfo = ResourcePackDataInfo = (
        82  # 资源包数据信息（服务端 -> 客户端）
    )
    IDResourcePackChunkData = ResourcePackChunkData = (
        83  # 资源包块数据（服务端 -> 客户端）
    )
    IDResourcePackChunkRequest = ResourcePackChunkRequest = (
        84  # 资源包块请求（客户端 -> 服务端）
    )
    IDTransfer = Transfer = 85  # 传输（服务端 -> 客户端）
    IDPlaySound = PlaySound = 86  # 播放声音（服务端 -> 客户端）
    IDStopSound = StopSound = 87  # 停止声音（服务端 -> 客户端）
    IDSetTitle = SetTitle = 88  # 设置标题（服务端 -> 客户端）
    IDAddBehaviourTree = AddBehaviourTree = 89  # 添加行为树（服务端 -> 客户端）
    IDStructureBlockUpdate = StructureBlockUpdate = (
        90  # 结构方块更新（客户端 -> 服务端）
    )
    IDShowStoreOffer = ShowStoreOffer = 91  # 显示商店优惠（服务端 -> 客户端）
    IDPurchaseReceipt = PurchaseReceipt = 92  # 购买收据（客户端 -> 服务端）
    IDPlayerSkin = PlayerSkin = 93  # 玩家皮肤（客户端 -> 服务端）
    IDSubClientLogin = SubClientLogin = 94  # 子客户端登录（客户端 -> 服务端）
    IDAutomationClientConnect = AutomationClientConnect = (
        95  # 自动化客户端连接（客户端 -> 服务端）
    )
    IDSetLastHurtBy = SetLastHurtBy = 96  # 设置最后受伤来源（服务端 -> 客户端）
    IDBookEdit = BookEdit = 97  # 书本编辑（客户端 -> 服务端）
    IDNPCRequest = NPCRequest = 98  # NPC请求（客户端 -> 服务端）
    IDPhotoTransfer = PhotoTransfer = 99  # 照片传输（客户端 -> 服务端）
    IDModalFormRequest = ModalFormRequest = 100  # 模态表单请求（服务端 -> 客户端）
    IDModalFormResponse = ModalFormResponse = 101  # 模态表单响应（客户端 -> 服务端）
    IDServerSettingsRequest = ServerSettingsRequest = (
        102  # 服务器设置请求（客户端 -> 服务端）
    )
    IDServerSettingsResponse = ServerSettingsResponse = (
        103  # 服务器设置响应（服务端 -> 客户端）
    )
    IDShowProfile = ShowProfile = 104  # 显示资料（客户端 -> 服务端）
    IDSetDefaultGameType = SetDefaultGameType = (
        105  # 设置默认游戏类型（服务端 -> 客户端）
    )
    IDRemoveObjective = RemoveObjective = 106  # 移除目标（服务端 -> 客户端）
    IDSetDisplayObjective = SetDisplayObjective = (
        107  # 设置显示目标（服务端 -> 客户端）
    )
    IDSetScore = SetScore = 108  # 设置分数（服务端 -> 客户端）
    IDLabTable = LabTable = 109  # 实验室表（服务端 -> 客户端）
    IDUpdateBlockSynced = UpdateBlockSynced = 110  # 同步更新方块（服务端 -> 客户端）
    IDMoveActorDelta = MoveActorDelta = 111  # 移动实体增量（服务端 -> 客户端）
    IDSetScoreboardIdentity = SetScoreboardIdentity = (
        112  # 设置计分板身份（服务端 -> 客户端）
    )
    IDSetLocalPlayerAsInitialised = SetLocalPlayerAsInitialised = (
        113  # 设置本地玩家为已初始化（服务端 -> 客户端）
    )
    IDUpdateSoftEnum = UpdateSoftEnum = 114  # 更新软枚举（服务端 -> 客户端）
    IDNetworkStackLatency = NetworkStackLatency = (
        115  # 网络堆栈延迟（服务端 -> 客户端）
    )
    IDScriptCustomEvent = ScriptCustomEvent = 117  # 脚本自定义事件（客户端 -> 服务端）
    IDSpawnParticleEffect = SpawnParticleEffect = (
        118  # 生成粒子效果（服务端 -> 客户端）
    )
    IDAvailableActorIdentifiers = AvailableActorIdentifiers = (
        119  # 可用实体标识符（服务端 -> 客户端）
    )
    IDLevelSoundEventV2 = LevelSoundEventV2 = 120  # 世界声音事件 V2（服务端 -> 客户端）
    IDNetworkChunkPublisherUpdate = NetworkChunkPublisherUpdate = (
        121  # 网络区块发布者更新（服务端 -> 客户端）
    )
    IDBiomeDefinitionList = BiomeDefinitionList = (
        122  # 生物群系定义列表（服务端 -> 客户端）
    )
    IDLevelSoundEvent = LevelSoundEvent = 123  # 世界声音事件（服务端 -> 客户端）
    IDLevelEventGeneric = LevelEventGeneric = 124  # 世界事件通用（服务端 -> 客户端）
    IDLecternUpdate = LecternUpdate = 125  # 讲台更新（客户端 -> 服务端）
    IDAddEntity = AddEntity = 127  # 添加实体（服务端 -> 客户端）
    IDRemoveEntity = RemoveEntity = 128  # 移除实体（服务端 -> 客户端）
    IDClientCacheStatus = ClientCacheStatus = 129  # 客户端缓存状态（客户端 -> 服务端）
    IDOnScreenTextureAnimation = OnScreenTextureAnimation = (
        130  # 屏幕纹理动画（服务端 -> 客户端）
    )
    IDMapCreateLockedCopy = MapCreateLockedCopy = (
        131  # 地图创建锁定副本（服务端 -> 客户端）
    )
    IDStructureTemplateDataRequest = StructureTemplateDataRequest = (
        132  # 结构模板数据请求（客户端 -> 服务端）
    )
    IDStructureTemplateDataResponse = StructureTemplateDataResponse = (
        133  # 结构模板数据响应（服务端 -> 客户端）
    )
    IDClientCacheBlobStatus = ClientCacheBlobStatus = (
        135  # 客户端缓存块状态（客户端 -> 服务端）
    )
    IDClientCacheMissResponse = ClientCacheMissResponse = (
        136  # 客户端缓存未命中响应（服务端 -> 客户端）
    )
    IDEducationSettings = EducationSettings = 137  # 教育设置（服务端 -> 客户端）
    IDEmote = Emote = 138  # 表情（客户端 -> 服务端）
    IDMultiPlayerSettings = MultiPlayerSettings = (
        139  # 多人游戏设置（客户端 -> 服务端）
    )
    IDSettingsCommand = SettingsCommand = 140  # 设置命令（客户端 -> 服务端）
    IDAnvilDamage = AnvilDamage = 141  # 铁砧损坏（服务端 -> 客户端）
    IDCompletedUsingItem = CompletedUsingItem = 142  # 完成使用物品（客户端 -> 服务端）
    IDNetworkSettings = NetworkSettings = 143  # 网络设置（服务端 -> 客户端）
    IDPlayerAuthInput = PlayerAuthInput = 144  # 玩家认证输入（客户端 -> 服务端）
    IDCreativeContent = CreativeContent = 145  # 创造内容（服务端 -> 客户端）
    IDPlayerEnchantOptions = PlayerEnchantOptions = (
        146  # 玩家附魔选项（服务端 -> 客户端）
    )
    IDItemStackRequest = ItemStackRequest = 147  # 物品堆栈请求（客户端 -> 服务端）
    IDItemStackResponse = ItemStackResponse = 148  # 物品堆栈响应（服务端 -> 客户端）
    IDPlayerArmourDamage = PlayerArmourDamage = 149  # 玩家盔甲损坏（服务端 -> 客户端）
    IDCodeBuilder = CodeBuilder = 150  # 代码构建器（客户端 -> 服务端）
    IDUpdatePlayerGameType = UpdatePlayerGameType = (
        151  # 更新玩家游戏类型（服务端 -> 客户端）
    )
    IDEmoteList = EmoteList = 152  # 表情列表（服务端 -> 客户端）
    IDPositionTrackingDBServerBroadcast = (
        153  # 位置跟踪数据库服务器广播（服务端 -> 客户端）
    )
    IDPositionTrackingDBClientRequest = (
        154  # 位置跟踪数据库客户端请求（客户端 -> 服务端）
    )
    IDDebugInfo = DebugInfo = 155  # 调试信息（服务端 -> 客户端）
    IDPacketViolationWarning = PacketViolationWarning = (
        156  # 数据包违规警告（服务端 -> 客户端）
    )
    IDMotionPredictionHints = MotionPredictionHints = (
        157  # 运动预测提示（服务端 -> 客户端）
    )
    IDAnimateEntity = AnimateEntity = 158  # 动画实体（服务端 -> 客户端）
    IDCameraShake = CameraShake = 159  # 相机震动（服务端 -> 客户端）
    IDPlayerFog = PlayerFog = 160  # 玩家迷雾（服务端 -> 客户端）
    IDCorrectPlayerMovePrediction = CorrectPlayerMovePrediction = (
        161  # 纠正玩家移动预测（服务端 -> 客户端）
    )
    IDItemComponent = ItemComponent = 162  # 物品组件（服务端 -> 客户端）
    IDFilterText = FilterText = 163  # 过滤文本（客户端 -> 服务端）
    IDClientBoundDebugRenderer = ClientBoundDebugRenderer = (
        164  # 客户端绑定调试渲染器（服务端 -> 客户端）
    )
    IDSyncActorProperty = SyncActorProperty = 165  # 同步实体属性（服务端 -> 客户端）
    IDAddVolumeEntity = AddVolumeEntity = 166  # 添加体积实体（服务端 -> 客户端）
    IDRemoveVolumeEntity = RemoveVolumeEntity = 167  # 移除体积实体（服务端 -> 客户端）
    IDSimulationType = SimulationType = 168  # 模拟类型（服务端 -> 客户端）
    IDNPCDialogue = NPCDialogue = 169  # NPC对话（服务端 -> 客户端）
    IDEducationResourceURI = EducationResourceURI = (
        170  # 教育资源URI（服务端 -> 客户端）
    )
    IDCreatePhoto = CreatePhoto = 171  # 创建照片（服务端 -> 客户端）
    IDUpdateSubChunkBlocks = UpdateSubChunkBlocks = (
        172  # 更新子区块方块（服务端 -> 客户端）
    )
    IDPhotoInfoRequest = PhotoInfoRequest = 173  # 照片信息请求（客户端 -> 服务端）
    IDSubChunk = SubChunk = 174  # 子区块（服务端 -> 客户端）
    IDSubChunkRequest = SubChunkRequest = 175  # 子区块请求（客户端 -> 服务端）
    IDClientStartItemCooldown = ClientStartItemCooldown = (
        176  # 客户端开始物品冷却（客户端 -> 服务端）
    )
    IDScriptMessage = ScriptMessage = 177  # 脚本消息（客户端 -> 服务端）
    IDCodeBuilderSource = CodeBuilderSource = 178  # 代码构建器源（客户端 -> 服务端）
    IDTickingAreasLoadStatus = TickingAreasLoadStatus = (
        179  #  ticking 区域加载状态（服务端 -> 客户端）
    )
    IDDimensionData = DimensionData = 180  # 维度数据（服务端 -> 客户端）
    IDAgentAction = AgentAction = 181  # 代理
    IDChangeMobProperty = ChangeMobProperty = 182  # 改变生物属性（服务端 -> 客户端）
    IDLessonProgress = LessonProgress = 183  # 课程进度（客户端 -> 服务端）
    IDRequestAbility = RequestAbility = 184  # 请求能力（客户端 -> 服务端）
    IDRequestPermissions = RequestPermissions = 185  # 请求权限（客户端 -> 服务端）
    IDToastRequest = ToastRequest = 186  # 吐司请求（服务端 -> 客户端）
    IDUpdateAbilities = UpdateAbilities = 187  # 更新能力（服务端 -> 客户端）
    IDUpdateAdventureSettings = UpdateAdventureSettings = (
        188  # 更新冒险设置（服务端 -> 客户端）
    )
    IDDeathInfo = DeathInfo = 189  # 死亡信息（服务端 -> 客户端）
    IDEditorNetwork = EditorNetwork = 190  # 编辑器网络（服务端 -> 客户端）
    IDFeatureRegistry = FeatureRegistry = 191  # 特性注册表（服务端 -> 客户端）
    IDServerStats = ServerStats = 192  # 服务器统计（服务端 -> 客户端）
    IDRequestNetworkSettings = RequestNetworkSettings = (
        193  # 请求网络设置（客户端 -> 服务端）
    )
    IDGameTestRequest = GameTestRequest = 194  # 游戏测试请求（客户端 -> 服务端）
    IDGameTestResults = GameTestResults = 195  # 游戏测试结果（服务端 -> 客户端）
    IDUpdateClientInputLocks = UpdateClientInputLocks = (
        196  # 更新客户端输入锁（服务端 -> 客户端）
    )
    IDClientCheatAbility = ClientCheatAbility = (
        197  # 客户端作弊能力（客户端 -> 服务端）
    )
    IDCameraPresets = CameraPresets = 198  # 相机预设（服务端 -> 客户端）
    IDUnlockedRecipes = UnlockedRecipes = 199  # 已解锁配方（服务端 -> 客户端）
    IDPyRpc = PyRpc = 200  # Python远程过程调用（客户端 -> 服务端）
    IDChangeModel = ChangeModel = 201  # 改变模型（服务端 -> 客户端）
    IDStoreBuySucc = StoreBuySucc = 202  # 商店购买成功（服务端 -> 客户端）
    IDNeteaseJson = NeteaseJson = 203  # 网易 JSON（客户端 -> 服务端）
    IDChangeModelTexture = ChangeModelTexture = 204  # 改变模型纹理（服务端 -> 客户端）
    IDChangeModelOffset = ChangeModelOffset = 205  # 改变模型偏移（服务端 -> 客户端）
    IDChangeModelBind = ChangeModelBind = 206  # 改变模型绑定（服务端 -> 客户端）
    IDHungerAttr = HungerAttr = 207  # 饥饿属性（服务端 -> 客户端）
    IDSetDimensionLocalTime = SetDimensionLocalTime = (
        208  # 设置维度本地时间（服务端 -> 客户端）
    )
    IDWithdrawFurnaceXp = WithdrawFurnaceXp = 209  # 提取熔炉经验（客户端 -> 服务端）
    IDSetDimensionLocalWeather = SetDimensionLocalWeather = (
        210  # 设置维度本地天气（服务端 -> 客户端）
    )
    IDCustomV1 = CustomV1 = 223  # 自定义 V1（服务端 -> 客户端）
    IDCombine = Combine = 224  # 组合（服务端 -> 客户端）
    IDVConnection = VConnection = 225  # V 连接（服务端 -> 客户端）
    IDTransport = Transport = 226  # 传输（服务端 -> 客户端）
    IDCustomV2 = CustomV2 = 227  # 自定义 V2（服务端 -> 客户端）
    IDConfirmSkin = ConfirmSkin = 228  # 确认皮肤（服务端 -> 客户端）
    IDTransportNoCompress = TransportNoCompress = 229  # 无压缩传输（服务端 -> 客户端）
    IDMobEffectV2 = MobEffectV2 = 230  # 生物效果 V2（服务端 -> 客户端）
    IDMobBlockActorChanged = MobBlockActorChanged = (
        231  # 生物方块实体改变（服务端 -> 客户端）
    )
    IDChangeActorMotion = ChangeActorMotion = 232  # 改变实体运动（服务端 -> 客户端）
    IDAnimateEmoteEntity = AnimateEmoteEntity = 233  # 动画表情实体（服务端 -> 客户端）
    IDCameraInstruction = CameraInstruction = 300  # 相机指令（服务端 -> 客户端）
    IDCompressedBiomeDefinitionList = CompressedBiomeDefinitionList = (
        301  # 压缩生物群系定义列表（服务端 -> 客户端）
    )
    IDTrimData = TrimData = 302  # 修剪数据（服务端 -> 客户端）
    IDOpenSign = OpenSign = 303  # 打开标志（服务端 -> 客户端）
    IDAgentAnimation = AgentAnimation = 304  # 代理动画（服务端 -> 客户端）


PacketIDS = PacketIDs
