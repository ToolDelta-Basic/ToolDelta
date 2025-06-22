"""
客户端启动器框架
提供与游戏进行交互的标准接口
"""

from .standard_launcher import StandardFrame
from .neomega_access_point import FrameNeOmgAccessPoint
from .neomega_access_point_remote import FrameNeOmgAccessPointRemote
from .neomega_launcher import FrameNeOmegaLauncher
from .eulogist_client import FrameEulogistLauncher
from .fateark_access_point import FrameFateArk
from .fateark_access_point_indirect import FrameFateArkIndirect

FrameNeOmg = FrameNeOmgAccessPoint
FrameNeOmgRemote = FrameNeOmgAccessPointRemote
FrameEulogist = FrameEulogistLauncher

FB_LIKE_LAUNCHERS = (
    FrameNeOmegaLauncher
    | FrameNeOmgAccessPoint
    | FrameNeOmgAccessPointRemote
    | FrameEulogistLauncher
    | FrameFateArk
    | FrameFateArkIndirect
)
"类FastBuilder启动器框架"

ACCESS_POINT_LAUNCHERS = (
    FrameNeOmgAccessPoint,
    FrameNeOmegaLauncher,
    FrameFateArk,
    FrameFateArkIndirect
)
"接入点类型的启动框架"

LAUNCHERS = FB_LIKE_LAUNCHERS
"所有类型的启动框架"

__all__ = [
    "FB_LIKE_LAUNCHERS",
    "LAUNCHERS",
    "FrameEulogistLauncher",
    "FrameFateArk",
    "FrameFateArkIndirect",
    "FrameNeOmegaLauncher",
    "FrameNeOmgAccessPoint",
    "FrameNeOmgAccessPointRemote",
    "StandardFrame"
]
