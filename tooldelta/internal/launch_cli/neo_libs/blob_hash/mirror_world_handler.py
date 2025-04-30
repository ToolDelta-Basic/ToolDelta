from typing import Callable
from tooldelta.internal.launch_cli.neo_libs.blob_hash.define import BaseBlobHashHolder
from tooldelta.internal.launch_cli.neo_libs.blob_hash.packet.define import (
    HashWithPosition,
    PayloadByHash,
)


class MirrorWorldHandler:
    """
    MirrorWorldHandler 指示镜像存档资源持有人所使用的处理函数，
    它们被用于处理来自客户端的 blob cache 查询和同步请求
    """

    base_blob_hash_holder: BaseBlobHashHolder
    f1: Callable[[list[HashWithPosition]], list[bool]] | None
    f2: Callable[[list[HashWithPosition]], list[PayloadByHash]] | None
    f3: Callable[[list[PayloadByHash]], None] | None
    f4: Callable[[list[HashWithPosition]], None] | None
    f5: Callable[[], None] | None

    def __init__(self, base_blob_hash_holder: BaseBlobHashHolder):
        """
        Args:
            base_blob_hash_holder (BaseBlobHashHolder): Blob hash holder 的底层实现
        """
        self.base_blob_hash_holder = base_blob_hash_holder
        self.f1 = None
        self.f2 = None
        self.f3 = None
        self.f4 = None
        self.f5 = None

    def set_handler(
        self,
        handle_query_disk_hash_exist: (
            Callable[[list[HashWithPosition]], list[bool]] | None
        ),
        handle_get_disk_hash_payload: (
            Callable[[list[HashWithPosition]], list[PayloadByHash]] | None
        ),
        handle_require_sync_hash_to_disk: Callable[[list[PayloadByHash]], None] | None,
        handle_clean_blob_hash_and_apply_to_world: (
            Callable[[list[HashWithPosition]], None] | None
        ),
        handle_server_disconnect: Callable[[], None] | None,
    ):
        """set_handler 根据给定的函数设置处理器，然后镜像存档的持有人便可作为资源中心处理来自服务者的资源请求

        Args:
            handle_query_disk_hash_exist (Callable[[list[HashWithPosition]], list[bool]] | None):
                handle_query_disk_hash_exist 处理来自服务者的 QueryDiskHashExist 请求。
                仅被镜像存档的持有人所使用。

                QueryDiskHashExist 用于向镜像存档持有人发起检索请求，
                目的仅在于检索 hashes 是否命中镜像存档中的存储。

                需要关注的是，handle_query_disk_hash_exist 的实现者需要确保底层实现确实是仅查询，
                这意味着 handle_query_disk_hash_exist 的具体实现不应该包含加载具体子区块的成分，
                而只是单纯的检查 blob hash 值是否可以与镜像存档中记录的值匹配

            handle_get_disk_hash_payload (Callable[[list[HashWithPosition]], list[PayloadByHash]] | None):
                handle_get_disk_hash_payload 处理来自服务者的 GetDiskHashPayload 请求
                仅被镜像存档的持有人所使用。

                GetDiskHashPayload 用于从镜像存档持有人请求 hashes 的二进制数据荷载。

                handle_get_disk_hash_payload 的实现者应当确保此函数返回的结果都满足 xxhash.Sum64(payload) = hash。
                如果镜像存档的持有人发现记录的 blob hash 值与传入 handle_get_disk_hash_payload 的 hashes 匹配，
                但相应的 payload 算出的 hash 值却不是给定的 blob hash 值时，说明这个子区块可能已经被更改。
                这种情况相当的罕见，例如发生在用户打开镜像存档并对这些子区块作出实际修改之后

            handle_require_sync_hash_to_disk (Callable[[list[PayloadByHash]], None] | None):
                handle_require_sync_hash_to_disk 处理来自服务者的 RequireSyncHashToDisk 请求
                仅被镜像存档的持有人所使用。

                RequireSyncHashToDisk 用于命令镜像存档持有人将 payload 指示的 (hash, payload) 储存到镜像存档中。

                可以保证 RequireSyncHashToDisk 只由服务者提出，并且服务者将尽可能少的提出命令，以减少造成的磁盘读写开销。
                这意味着，服务者通过一系列方法确定出了那些真正需要被更改的子区块，然后向镜像存档的持有人提出同步更改的命令

            handle_clean_blob_hash_and_apply_to_world (Callable[[list[HashWithPosition]], None] | None):
                handle_clean_blob_hash_and_apply_to_world 由镜像存档持有人的底层直接调用，
                底层将不断监听 packet.SubChunk，然后从中找到全部都是空气的子区块，
                并作为参数传入到 handle_clean_blob_hash_and_apply_to_world 之中。

                由于全为空气的子区块的 blob hash 是不存在的，所以传入的 pos 切片中，
                对于其中的每个元素 x 而言，x.Hash 是未被使用的字段（或者，x.Hash 总是 0）。
                基于此，我们需要这样一个函数来初始化那些全为空气的子区块
                （即，handleGetDiskHashPayload 只会同步非空子区块，而这个函数的功能则是补齐同步空气子区块的部分）。

                除了初始化以外，本函数还有另外一个目的，便是把原本在镜像存档中不非空的子区块
                变为非空，这可能发生在服务器内某个子区块从非空变为空的过程中。

                需要提醒的是，每个区块中完全是空气的子区块可能非常多，因为 Minecraft 中大多数地方都是空气。
                于是，这个函数在很大可能上被大量的调用并传入大量的应该被设置为空气的子区块条目。
                这意味着，如果机器人不断的走过相同的区块，然后就很可能得到相同的完全是空的子区块，
                然后重复地传入到 handle_clean_blob_hash_and_apply_to_world 之中。

                handle_clean_blob_hash_and_apply_to_world 的实现者需要确保相应的实现不会对磁盘造成大量读写，
                这意味着在真正设置一个子区块为空子区块前，应当通过一些手段确定这个子区块是否是空的。
                如果不是空的（或者这个子区块在镜像存档中不存在），再进行读写；反之，不进行任何操作。

                可以将空子区块的 blob hash 简单置为 0，因此对于非空子区块，它们的 blob hash 一定非 0。
                这意味着，如果一个子区块被要求设为空气，而这个子区块不存在 blob hash 或 blob hash 非 0，
                那么这一定这个子区块在镜像存档中的情况一定满足下面其中一个
                    - 这个子区块不存在于镜像存档
                    - 这个子区块在镜像存档中非空
                于是，可以安全的把这个镜像存档的这个子区块的 blob hash 置为 0，并将这个子区块置空

            handle_server_disconnect (Callable[[], None] | None):
                当 blob hash 缓存数据集的服务者撤销当前镜像存档持有人的持有身份时，
                底层实现将会尝试进行恢复（尝试重新取得我们作为持有人的身份）。

                当恢复工作失败后，handle_server_disconnect 将会被调用，
                以确保作为曾是持有人的自己可以进行一部分收尾工作。

                handle_server_disconnect 一般不会发生，除非服务者认为我们作为持有者已经死亡
        """
        self.f1 = handle_query_disk_hash_exist
        self.f2 = handle_get_disk_hash_payload
        self.f3 = handle_require_sync_hash_to_disk
        self.f4 = handle_clean_blob_hash_and_apply_to_world
        self.f5 = handle_server_disconnect
