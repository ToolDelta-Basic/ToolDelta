from tooldelta import *
    # Builtins 里有许多实用的方法

import json

from tooldelta.Frame import Builtins, Config, Frame

# 注册插件主类
@plugins.add_plugin
# 创建一个插件主类, 其一定要继承Plugin类
class MyPluginExample(Plugin):
    # 插件名
    name = "示范插件"
    # 插件作者
    author = "ToolDelta"
    # 插件版本
    version = (0, 0, 1)
    # 初始化
    def __init__(self, frame: Frame):
        # 接收 ToolDelta 的框架 Frame
        self.frame = frame
        # 接收 用于游戏交互的框架 GameControl(GameManager)
        self.game_ctrl = frame.get_game_control()
        # 加载组件的配置文件(最后再看这里)
        self.config = self.check_and_get_config()

    def on_def(self):
        # 所有插件主类和插件API类都实例化后执行的方法
        "这里是用来获取其他插件提供的API的地方, 当然你也可以不使用这个方法"
        # self.other_plugins_api = plugins.get_plugin_api("api_name")

    def on_inject(self):
        # 机器人进入游戏且ToolDelta初始化完成后加载的方法
        Print.print_suc("系统启动成功!")
        # 往控制台里添加一个菜单项, 系统启动后在控制台输入help可查看, 输入 示例插件触发词1 [...参数] 或 示例插件触发词2 [...参数] 触发菜单
        self.frame.add_console_cmd_trigger(
             ["示例插件触发词1", "示例插件触发词2"],
             "[<参数提示>]",
             "菜单项说明",
             lambda args: Print.print_inf("你输入了:" + " ".join(args))
        )

    def on_player_join(self, player):
        # 玩家加入游戏.
        # game_ctrl 派上用场, 使用它的say_to方法来向游戏里的@a对象发送信息.
        self.game_ctrl.say_to("@a", f"{player} 加入游戏")

    def on_player_death(self, player, killer):
        # 玩家死亡, 若是被击杀, 则killer为String(击杀者), 否则为None
        if killer is not None:
            # 发送一条指令
            self.game_ctrl.sendcmd(f"/scoreboard players add {killer} kill_score 1")

    def on_player_join(self, player):
        # 玩家退出游戏.
        self.game_ctrl.say_to("@a", f"{player} 退出游戏")

    def on_player_message(self, player, msg):
        # 玩家发言. 注意! 私聊发言和say也算在内, 命令方块/say发言也包括在内!
        Print.print_inf(f"{player}: {msg}")
        # 如果玩家发言为"我的钻石", 则触发一个简易触发词项
        if msg == "我的钻石":
            # 创建一个专门的玩家会话线程, 防止玩家同时处在两个会话中
            Builtins.create_dialogue_threading(
                player, self.check_my_diamond_count,
                exc_cb = lambda player: self.game_ctrl.say_to(player, "§c你已经在一个对话中了, 请先退出对话"),
                args = (player,)
            )

    def check_my_diamond_count(self, player):
        # 检测玩家背包里有多少钻石
        # sendcmd的后两个参数: 获取指令返回值=True, 超时时长=30秒
        result = self.game_ctrl.sendcmd(f"/clear @a[name={player}] diamond 0 0", True, 30)
        # 检测方式1
        Success = result.OutputMessages[0].Success
        if Success:
            count = int(result.OutputMessages[0].Parameters[1])
        else:
            count = 0
        # 检测方式2
        Success = result.as_dict["OutputMessages"][0]["Success"]
        if Success:
            count = int(result.as_dict["OutputMessages"][0]["Parameters"][1])
        else:
            count = 0
        self.game_ctrl.say_to(player, f"你有{count}个钻石")

    # 监听机器人收到的数据包(这里的示例是9号数据包)
    @plugins.add_packet_listener(9)
    def on_pkt(self, packet: dict):
        Print.print_inf("收到数据包, 内容:")
        Print.print_inf(json.dumps(packet, indent = 4, ensure_ascii = False))
        # 这样的Print会自动对换行符号进行处理, 优雅的输出

    # 好了, 最基本的组件教学就可以到此为止咯

    def check_and_get_config(self):
            # 描述一个JSON配置文件的标准形式
            CONFIG_STANDARD_TYPE = {
                "Key1": int, # Key1对应的值必须为整数
                "Key2": str, # Key2对应的值必须为字符串
                "Key3": Config.PInt, # Key3对应的值必须为正整数
                "Key4": [int, str, bool], # Key4对应的值可以是整数, 字符串, 也可以是布尔值
                # 配置文件中JSON键 Key4, Key5必须出现其中的一个或多个, 且值必须为非负浮点小数
                Config.Group("Key5", "Key6"): Config.NNFloat,
                # 配置文件中非必须的JSON键Key5, 可有可无
                Config.UnneccessaryKey("Key7"): bool,
                # 当然json里也可以套json
                "Key8": {
                    "sub_key1": int,
                    "sub_key2": str,
                    "sub_key3": {
                        "sub2_key1": Config.PFloat # 正浮点小数
                    },
                    "sub_key4": Config.PInt
                },
                "Key9": [r"%list", str], # Key9对应的值是一个每个成员都是字符串的列表
                "Key10": [r"%list11", int], # Key10对应的值是包含11个整数的列表
                "Key11": {
                    r"%any": int # Key11对应的是一个键名任意, 但是值必须为整数的json对象
                },
                # Key12是对以上方法的综合运用
                "Key12": {
                    r"%any": [
                        type(None),
                        {
                            "sub_key1": Config.PFloat,
                            Config.UnneccessaryKey("sub_key2"): [r"%list", {"sub2_key1": str}],
                            Config.Group("sub_key3", "sub_key4", "sub_key5"): [r"%list2", Config.PInt]
                        }
                    ]
                }
            }
            # 默认的配置文件(头大了?别急)
            DEFAULT_CONFIG = {
                "Key1": -1145,
                "Key2": "string",
                "Key3": 1,
                "Key4": True,
                "Key6": 1.42857,
                "Key8": {
                    "sub_key1": 12345,
                    "sub_key2": "abcde",
                    "sub_key3": {
                        "sub2_key1": 1.2345
                    },
                    "sub_key4": 10010,
                },
                "Key9": ["a", "c", "e", "g", "i"],
                "Key10": [1, 2, 3, 4, 5, -6, 7, 8, 9, 11, -12],
                "Key11": {
                    "ToolDelta": 11,
                    "FastBuilder": 14
                },
                "Key12": {
                    "香菜": None,
                    "青菜": {
                        "sub_key1": 1.1,
                        "suub_key2": [{"sub2_key1": "a"}, {"sub2_key1": "b"}],
                        "sub_key4": [11, 12]
                    }
                }
            }
            # 获取/写入默认配置, 并检测合法性
            config, config_version = Config.getPluginConfigAndVersion(
                # 参数: 插件文件的名字(生成在 插件配置文件/name.json), 配置文件的标准格式, 默认配置文件, 默认配置文件版本
                self.name, CONFIG_STANDARD_TYPE, DEFAULT_CONFIG, self.version
            ) # 返回: 配置文件的配置项转为字典形式, 配置文件中配置的版本
            # print(config["Key11"]) -> {"ToolDelta": 11, "FastBuiler": 14}
            return config
