from dataclasses import dataclass
from tooldelta.internal.launch_cli.neo_libs.neo_conn import ThreadOmega


BLOCKING_DEADLINE_SECONDS = 30


@dataclass
class BaseBlobHashHolder:
    """BaseBlobHashHolder 是 Blob hash holder 的底层实现。

    Args:
        omega (ThreadOmega): omega ..
        is_disk_holder (bool): is_disk_holder 指示自身是否是镜像存档的持有人
        disk_holder_name (str): disk_holder_name 指示当前结点作为镜像存档的持有人的名字
    """

    omega: ThreadOmega
    is_disk_holder: bool
    disk_holder_name: str
