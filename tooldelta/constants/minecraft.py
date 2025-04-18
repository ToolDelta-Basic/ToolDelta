"ToolDelta 常量定义"

from enum import IntEnum, Enum

class TextType(IntEnum):
    TextTypeRaw = 0
    TextTypeChat = 1
    TextTypeTranslation = 2
    TextTypePopup = 3
    TextTypeJukeboxPopup = 4
    TextTypeTip = 5
    TextTypeSystem = 6
    TextTypeWhisper = 7
    TextTypeAnnouncement = 8
    TextTypeObjectWhisper = 9
    TextTypeObject = 10
    TextTypeObjectAnnouncement = 11


class ContainerType(IntEnum):
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


class PlayerActionType(IntEnum):
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


class EffectIDS(str, Enum):
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


class BuildStructureIDS(str, Enum):
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
