from typing import TYPE_CHECKING
from dataclasses import dataclass
from tooldelta import game_utils
from .player_abilities import Abilities, update_player_abilities

if TYPE_CHECKING:
    from ..maintainers import PlayerInfoMaintainer


@dataclass
class UnreadyPlayer:
    uuid: str
    unique_id: int
    name: str
    xuid: str
    platform_chat_id: str
    build_platform: int
    online: bool = True
    abilities: Abilities | None = None

    def ready(self, _parent: "PlayerInfoMaintainer"):
        p = Player(
            _parent,
            self.uuid,
            self.unique_id,
            self.name,
            self.xuid,
            self.platform_chat_id,
            self.build_platform,
            self.online,
        )
        if self.abilities:
            p.setAbilities(self.abilities, upload=False)
        return p


@dataclass
class Player:
    _parent: "PlayerInfoMaintainer"
    uuid: str
    unique_id: int
    name: str
    xuid: str
    platform_chat_id: str
    build_platform: int
    online: bool = True

    def show(self, text: str):
        """
        对玩家显示聊天栏消息
        Args:
            text: 消息文本
        """
        self._parent.frame.get_game_control().say_to(self.name, text)

    def setTitle(self, title: str, sub_title: str = ""):
        """
        设置玩家标题
        Args:
            text: 标题文本
        """
        self._parent.frame.get_game_control().player_title(self.name, title)
        if sub_title.strip():
            self._parent.frame.get_game_control().player_subtitle(self.name, sub_title)

    def setActionbar(self, text: str):
        """
        设置玩家行动栏文本
        Args:
            text: 动作条文本
        """
        self._parent.frame.get_game_control().player_actionbar(self.name, text)

    def getSelector(self):
        """
        获取玩家选择器
        Returns:
            str: 选择器
        """
        return f'@a[name="{self.name}"]'

    def getPos(self, timeout: float = 5) -> tuple[int, float, float, float]:
        """
        获取玩家坐标
        Args:
            timeout: 超时时间, 默认 5 秒
        Returns:
            tuple[int, float, float, float]: 维度ID, x, y, z
        """
        data = game_utils.getPos(self.name, timeout)
        dim = data["dimension"]
        pos = data["position"]
        x, y, z = pos["x"], pos["y"], pos["z"]
        return dim, x, y, z

    def getItemCount(self, item_id: str, item_data: int = -1, timeout: float = 5):
        """
        获取玩家物品数量
        Args:
            item_id: 物品ID
            item_data: 物品数据值
            timeout: 超时时间, 默认 5 秒
        Returns:
            int: 物品数量
        """
        return game_utils.getItem(self.name, item_id, item_data)

    def getScore(self, scoreboard_name: str, timeout: float = 5):
        """
        获取玩家计分板分数
        Args:
            scoreboard_name: 计分板名称
            timeout: 超时时间, 默认 5 秒
        Returns:
            int: 计分板分数
        """
        return game_utils.getScore(scoreboard_name, self.getSelector(), timeout)

    def input(self, prompt: str = "", timeout: float = 30):
        """
        获取玩家输入
        Args:
            prompt: 提示文本
            timeout: 超时时间, 默认 30 秒
        Returns:
            str: 玩家输入
        """
        if prompt.strip():
            self.show(prompt)
        return game_utils.waitMsg(self.name, timeout)

    @property
    def abilities(self):
        """
        获取玩家能力
        Returns:
            Abilities: 玩家能力
        """
        ab = self._parent.player_abilities.get(self.unique_id)
        if ab is None:
            raise ValueError(f"玩家 {self.name} 的能力还没有初始化")
        return ab

    def setAbilities(self, abilities: Abilities, upload=True):
        """
        设置玩家能力
        Args:
            abilities: 玩家能力
        """
        self._parent.player_abilities[self.unique_id] = abilities
        if upload:
            update_player_abilities(
                self._parent.frame.get_game_control(), self.unique_id, abilities
            )

    def is_op(self):
        return self.abilities.command_permissions >= 3
