from tooldelta.internal.launch_cli.neo_libs.blob_hash.define import (
    BLOCKING_DEADLINE_SECONDS,
    BaseBlobHashHolder,
)
from tooldelta.internal.launch_cli.neo_libs.blob_hash.packet.define import (
    HashWithPosition,
    PayloadByHash,
)
from tooldelta.internal.launch_cli.neo_libs.blob_hash.packet.server_and_client import (
    ClientGetDiskHashPayload,
    ClientGetDiskHashPayloadResponse,
    ClientQueryDiskHashExist,
    ClientQueryDiskHashExistResponse,
    GetHashPayload,
    GetHashPayloadResponse,
    SetHolderRequest,
    SetHolderResponse,
)


class ClientFunction:
    """ClientFunction 基于 BaseBlobHashHolder 实现，为 Blob hash 客户端提供功能"""

    base_blob_hash_holder: BaseBlobHashHolder

    def __init__(self, base_blob_hash_holder: BaseBlobHashHolder):
        """
        Args:
            base_blob_hash_holder (BaseBlobHashHolder): Blob hash holder 的底层实现
        """
        self.base_blob_hash_holder = base_blob_hash_holder

    def set_holder_request(self) -> bool:
        """
        set_holder_request 请求服务者将客户端设置为镜像存档的持有人。
        一旦成功便不可撤销，持有人必须伴随服务者的存在而始终存在
        """
        request = SetHolderRequest()
        resp_bytes: bytes = self.base_blob_hash_holder.omega.soft_call_with_bytes(
            request.packet_name, request.encode(), timeout=BLOCKING_DEADLINE_SECONDS
        )  # type: ignore

        resp = SetHolderResponse()
        resp.decode(resp_bytes)

        if resp.success_states:
            self.base_blob_hash_holder.disk_holder_name = resp.holder_name
            self.base_blob_hash_holder.is_disk_holder = True
        return resp.success_states

    def get_hash_payload(
        self, hashes: list[HashWithPosition]
    ) -> dict[HashWithPosition, bytes]:
        """
        get_hash_payload 从服务者获取 hashes 对应的数据荷载。
        底层缓存集合会因此同时更新
        """
        mapping: dict[HashWithPosition, bytes] = {}

        reqeust = GetHashPayload(hashes)
        resp_bytes: bytes = self.base_blob_hash_holder.omega.soft_call_with_bytes(
            reqeust.packet_name, reqeust.encode(), timeout=BLOCKING_DEADLINE_SECONDS
        )  # type: ignore

        resp = GetHashPayloadResponse()
        resp.decode(resp_bytes)

        for i in resp.payload:
            payload = i.payload.tobytes()
            if self.base_blob_hash_holder.omega.update_blob_cache(i.hash.hash, payload):
                mapping[i.hash] = payload

        return mapping

    def query_disk_hash_exist(
        self, hashes: list[HashWithPosition]
    ) -> tuple[list[HashWithPosition], list[HashWithPosition]]:
        """
        query_disk_hash_exist 向镜像存档持有人发起检索请求，
        目的仅在于检索 hashes 是否命中镜像存档中的存储。

        返回的元组中的每个元素从左到右依次代表命中的缓存和
        未被命中的缓存
        """
        request = ClientQueryDiskHashExist(hashes)
        resp_bytes: bytes = self.base_blob_hash_holder.omega.soft_call_with_bytes(
            request.packet_name, request.encode(), timeout=BLOCKING_DEADLINE_SECONDS
        )  # type: ignore

        resp = ClientQueryDiskHashExistResponse()
        resp.decode(resp_bytes)

        hit: list[HashWithPosition] = []
        miss: list[HashWithPosition] = []

        for i in range(len(hashes)):
            if resp.states[i]:
                hit.append(hashes[i])
            else:
                miss.append(hashes[i])

        return hit, miss

    def get_disk_hash_payload(
        self, hashes: list[HashWithPosition]
    ) -> tuple[list[PayloadByHash], list[HashWithPosition]]:
        """
        get_disk_hash_payload 从镜像存档持有人请求 hashes 的二进制数据荷载。
        返回的元组中的每个元素从左到右依次代表命中的缓存和未被命中的缓存
        """
        request = ClientGetDiskHashPayload(hashes)
        resp_bytes: bytes = self.base_blob_hash_holder.omega.soft_call_with_bytes(
            request.packet_name, request.encode(), timeout=BLOCKING_DEADLINE_SECONDS
        )  # type: ignore

        resp = ClientGetDiskHashPayloadResponse()
        resp.decode(resp_bytes)

        mapping: dict[HashWithPosition, PayloadByHash] = {}
        for i in resp.payload:
            mapping[i.hash] = i

        hit: list[PayloadByHash] = []
        miss: list[HashWithPosition] = []

        for i in range(len(hashes)):
            if hashes[i] in mapping:
                hit.append(mapping[hashes[i]])
            else:
                miss.append(hashes[i])

        return hit, miss
