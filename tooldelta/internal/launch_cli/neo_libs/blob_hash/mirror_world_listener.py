import numpy
from tooldelta.internal.launch_cli.neo_libs.blob_hash.define import (
    BLOCKING_DEADLINE_SECONDS,
    BaseBlobHashHolder,
)
from tooldelta.internal.launch_cli.neo_libs.blob_hash.mirror_world_handler import (
    MirrorWorldHandler,
)
from tooldelta.internal.launch_cli.neo_libs.blob_hash.packet.define import (
    HashWithPosition,
    SubChunkPos,
)
from tooldelta.internal.launch_cli.neo_libs.blob_hash.packet.server_and_client import (
    SetHolderRequest,
    SetHolderResponse,
)
from tooldelta.internal.launch_cli.neo_libs.blob_hash.packet.server_and_mirror_world import (
    GetDiskHashPayload,
    GetDiskHashPayloadResponse,
    QueryDiskHashExist,
    QueryDiskHashExistResponse,
    RequireSyncHashToDisk,
    ServerDisconnected,
)
from tooldelta.mc_bytes_packet.sub_chunk import (
    SUB_CHUNK_RESULT_SUCCESS_ALL_AIR,
    SubChunk,
)
from tooldelta.utils.tooldelta_thread import ToolDeltaThread


class MirrorWorldListener:
    """
    MirrorWorldListener 是基于 MirrorWorldHandler 实现的监听器，
    然后镜像存档的持有人便可作为资源中心处理来自服务者的资源请求
    """

    mirror_world_handler: MirrorWorldHandler
    _has_register: bool

    def __init__(self, mirror_world_handler: MirrorWorldHandler):
        """
        Args:
            mirror_world_handler (MirrorWorldHandler):
                镜像存档资源持有人所使用的处理函数，
                它们被用于处理来自客户端的 blob cache 查询和同步请求
        """
        self.mirror_world_handler = mirror_world_handler
        self._has_register = False

    def register_listener(self) -> bool:
        """
        register_listener 为镜像资源持有者注册其所使用的监听器，
        register_listener 应当最多被调用一次。

        如果已经注册了监听器，或当前结点不是镜像存档的持有人，
        则返回假；否则，返回真
        """
        if self._has_register or not self._base_blob_hash_holder().is_disk_holder:
            return False
        self._register_listener()
        self._has_register = True
        return True

    def _base_blob_hash_holder(self) -> BaseBlobHashHolder:
        return self.mirror_world_handler.base_blob_hash_holder

    def _register_listener(self):
        # MC Packet
        self._base_blob_hash_holder().omega.listen_packets(
            "SubChunk", self._on_sub_chunk, False
        )
        # Handle server keep alive and disconnected
        self._base_blob_hash_holder().omega.soft_reg(
            "blob-hash-keep-alive", True, self._handle_keep_alive
        )
        self._base_blob_hash_holder().omega.soft_listen(
            "blob-hash-server-disconnected", True, self._handle_server_disconnected
        )
        # Handle server request
        self._base_blob_hash_holder().omega.soft_reg(
            "blob-hash-query-disk-hash-exist", True, self._handle_query_disk_hash_exist
        )
        self._base_blob_hash_holder().omega.soft_reg(
            "blob-hash-get-disk-hash-payload", True, self._handle_get_disk_hash_payload
        )
        self._base_blob_hash_holder().omega.soft_reg(
            "blob-hash-require-sync-hash-to-disk",
            True,
            self._handle_require_sync_hash_to_disk,
        )

    def _on_sub_chunk(self, _: str, bs: bytes):
        if self.mirror_world_handler.f4 is None:
            return

        pos: list[HashWithPosition] = []

        s = SubChunk()
        s.decode(bs)

        for i in s.Entries:
            if i.Result == SUB_CHUNK_RESULT_SUCCESS_ALL_AIR:
                pos.append(
                    HashWithPosition(
                        0,
                        SubChunkPos(i.SubChunkPosX, i.SubChunkPosY, i.SubChunkPosZ),
                        s.Dimension,
                    )
                )

        if len(pos) > 0:
            self.mirror_world_handler.f4(pos)

    def _handle_keep_alive(self, packet: bytes) -> bytes:
        return packet

    def _handle_server_disconnected(self, packet: bytes):
        pk = ServerDisconnected()
        pk.decode(packet)

        if (
            pk.mirror_world_holder_name
            != self._base_blob_hash_holder().disk_holder_name
        ):
            return

        self._base_blob_hash_holder().disk_holder_name = ""
        self._base_blob_hash_holder().is_disk_holder = False

        # Server thought we were dead,
        # however, we are still alive,
        # so we try to re-set as holder
        # again.
        def recover():
            # If re-set request failed,
            # then we lost the status of
            # mirror world holder.
            recover_pk = SetHolderRequest()
            recover_states: bytes | None = (
                self._base_blob_hash_holder().omega.soft_call_with_bytes(
                    recover_pk.packet_name,
                    recover_pk.encode(),
                    timeout=BLOCKING_DEADLINE_SECONDS,
                )
            )

            if recover_states is None and self.mirror_world_handler.f5 is not None:
                self.mirror_world_handler.f5()

            resp = SetHolderResponse()
            resp.decode(recover_states)

            if resp.success_states:
                self._base_blob_hash_holder().disk_holder_name = resp.holder_name
                self._base_blob_hash_holder().is_disk_holder = True
            elif self.mirror_world_handler.f5 is not None:
                self.mirror_world_handler.f5()

        ToolDeltaThread(recover, usage="Mirror World Holder Recover Thread")

    def _handle_query_disk_hash_exist(self, packet: bytes) -> bytes | None:
        if (
            not self._base_blob_hash_holder().is_disk_holder
            or self.mirror_world_handler.f1 is None
        ):
            return

        pk = QueryDiskHashExist()
        pk.decode(packet)

        resp = QueryDiskHashExistResponse(
            self._base_blob_hash_holder().disk_holder_name,
            numpy.array(self.mirror_world_handler.f1(pk.hashes), dtype=numpy.bool),
        )
        return resp.encode()

    def _handle_get_disk_hash_payload(self, packet: bytes) -> bytes | None:
        if (
            not self._base_blob_hash_holder().is_disk_holder
            or self.mirror_world_handler.f2 is None
        ):
            return

        pk = GetDiskHashPayload()
        pk.decode(packet)

        resp = GetDiskHashPayloadResponse(
            self._base_blob_hash_holder().disk_holder_name,
            self.mirror_world_handler.f2(pk.hashes),
        )
        return resp.encode()

    def _handle_require_sync_hash_to_disk(self, packet: bytes) -> bytes | None:
        if (
            not self._base_blob_hash_holder().is_disk_holder
            or self.mirror_world_handler.f3 is None
        ):
            return

        pk = RequireSyncHashToDisk()
        pk.decode(packet)

        self.mirror_world_handler.f3(pk.payload)
        return b""
