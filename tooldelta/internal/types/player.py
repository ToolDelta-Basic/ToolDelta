from dataclasses import dataclass
from tooldelta import tooldelta, game_utils


@dataclass
class Player:
    name: str
    uuid: str
    unique_id: int
    runtime_id: int

    def show(self, text: str):
        """
        对玩家显示聊天栏消息
        Args:
            text: 消息文本
        """
        tooldelta.get_game_control().say_to(self.name, text)

    def set_title(self, title: str, sub_title: str = ""):
        """
        设置玩家标题
        Args:
            text: 标题文本
        """
        tooldelta.get_game_control().player_title(self.name, title)
        if sub_title.strip():
            tooldelta.get_game_control().player_subtitle(self.name, sub_title)

    def set_actionbar(self, text: str):
        """
        设置玩家行动栏文本
        Args:
            text: 动作条文本
        """
        tooldelta.get_game_control().player_actionbar(self.name, text)

    def get_selector(self):
        """
        获取玩家选择器
        Returns:
            str: 选择器
        """
        return f'"{self.name}"'

    def get_pos(self, timeout: float = 5) -> tuple[int, float, float, float]:
        """
        获取玩家坐标
        Args:
            timeout: 超时时间
        Returns:
            tuple[int, float, float, float]: 维度ID, x, y, z
        """
        data = game_utils.getPos(self.name, timeout)
        dim = data["dimension"]
        pos = data["position"]
        x, y, z = pos["x"], pos["y"], pos["z"]
        return dim, x, y, z

    def get_item_count(self, item_id: str, item_data: int = -1):
        """
        获取玩家物品数量
        Args:
            item_id: 物品ID
            item_data: 物品数据值
        Returns:
            int: 物品数量
        """
        return game_utils.getItem(self.name, item_id, item_data)

    def input(self, prompt: str = "", timeout: float = 30):
        """
        获取玩家输入
        Args:
            prompt: 提示文本
            timeout: 超时时间
        Returns:
            str: 玩家输入
        """
        if prompt.strip():
            self.show(prompt)
        return game_utils.waitMsg(self.name, timeout)
