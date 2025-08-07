from tooldelta.internal.launch_cli.neo_libs.blob_hash.client_function import (
    ClientFunction,
)
from tooldelta.internal.launch_cli.neo_libs.blob_hash.define import BaseBlobHashHolder
from tooldelta.internal.launch_cli.neo_libs.blob_hash.mirror_world_handler import (
    MirrorWorldHandler,
)
from tooldelta.internal.launch_cli.neo_libs.blob_hash.mirror_world_listener import (
    MirrorWorldListener,
)
from tooldelta.internal.launch_cli.neo_libs.neo_conn import ThreadOmega


class BlobHashHolder:
    """
    BlobHashHolder 是基于 BaseBlobHashHolder, ClientFunction, MirrorWorldHandler 和 MirrorWorldListener
    实现的，具有与 neomega-core 所拥有的 Blob hash holder 相同接口的 Blob hash cache 缓存数据集持有实现
    """

    _base_blob_hash_holder: BaseBlobHashHolder
    _client_function: ClientFunction
    _mirror_world_handler: MirrorWorldHandler
    _mirror_world_listener: MirrorWorldListener

    def __init__(self, omega: ThreadOmega) -> None:
        self._base_blob_hash_holder = BaseBlobHashHolder(omega, False, "")
        self._client_function = ClientFunction(self._base_blob_hash_holder)
        self._mirror_world_handler = MirrorWorldHandler(self._base_blob_hash_holder)
        self._mirror_world_listener = MirrorWorldListener(self._mirror_world_handler)

    def is_server(self) -> bool:
        """
        is_server 返回自身是否是 blob cache 缓存数据集的权威持有人(服务者)。
        这在 ToolDelta 中是不可能的，因此总是返回假
        """
        return False

    def is_disk_holder(self) -> bool:
        """is_disk_holder 返回当前是否是镜像存档资源的持有人"""
        return self._base_blob_hash_holder.is_disk_holder

    def wait_login_sequence_down(self):
        """
        wait_login_sequence_down 阻塞并等待登录序列完成。
        由于这是服务者所使用的函数，而这对于 ToolDelta 是不可能的，
        因此我们总是理解返回值而不进行任何操作
        """
        return

    def load_blob_cache(self, hash: int) -> bytes:
        """
        load_blob_cache 从底层缓存数据集检索 hash 所指示的数据负载。
        如果不存在，则返回空 bytes
        """
        return self._base_blob_hash_holder.omega.load_blob_cache(hash)

    def update_blob_cache(self, hash: int, payload: bytes) -> bool:
        """
        update_blob_cache 向底层缓存数据集写入 hash 所指示的二进制负载 payload。
        如果提供的 hash 并非 payload 的真实哈希，则写入将被拒绝，并返回假
        """
        return self._base_blob_hash_holder.omega.update_blob_cache(hash, payload)

    def as_server_side(self) -> None:
        """
        as_server_side 返回针对服务者实现的函数。
        非服务者调用 as_server_side 将得到空值。
        可以使用 b.IsServer() 确定当前结点是否是服务者。

        由于 ToolDelta 不可能成为服务者，所以该函数将立即返回值
        """
        return

    def as_mirror_world_side(self) -> MirrorWorldListener:
        """
        as_mirror_world_side 返回针对镜像存档资源持有者实现的 MirrorWorldListener，
        无论当前的使用者是否是镜像存档的持有人。

        通过 MirrorWorldListener.mirror_world_handler.set_handler 来设置处理函数，
        通过 MirrorWorldListener.register_listener 来启动监听
        """
        return self._mirror_world_listener

    def get_client_function(self) -> ClientFunction:
        """
        get_client_function 用于获取针对 Blob hash 客户端而实现的一系列函数，
        它是同时可被 服务者/客户端/镜像存档持有人 所共同使用的公共实现
        """
        return self._client_function
