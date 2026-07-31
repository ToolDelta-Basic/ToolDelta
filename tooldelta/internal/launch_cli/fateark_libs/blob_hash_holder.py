from collections.abc import Callable
from threading import RLock

from ..neo_libs.blob_hash.packet.define import HashWithPosition
from . import core_conn


class FateArkBlobHashClientFunction:
    """FateArk 的 BlobHashHolder 客户端操作。"""

    def __init__(self, holder: "FateArkBlobHashHolder") -> None:
        self._holder = holder

    def get_hash_payload(
        self, hashes: list[HashWithPosition]
    ) -> dict[HashWithPosition, bytes]:
        """获取缺失哈希数据，同时写入本地缓存。"""
        if not hashes:
            return {}
        payloads = self._holder._request_hashes([item.hash for item in hashes])
        result: dict[HashWithPosition, bytes] = {}
        for item in hashes:
            payload = payloads.get(item.hash)
            if payload is None:
                continue
            self._holder.update_blob_cache(item.hash, payload)
            result[item] = payload
        return result


class FateArkBlobHashHolder:
    """通过 FateArk gRPC 访问当前会话的世界数据缓存。"""

    def __init__(
        self,
        request_hashes: Callable[[list[int]], dict[int, bytes]] | None = None,
        get_generation: Callable[[], int] | None = None,
    ) -> None:
        self._request_hashes = request_hashes or core_conn.get_blob_hash_payloads
        self._get_generation = get_generation or core_conn.get_connection_generation
        self._generation = self._get_generation()
        self._cache: dict[int, bytes] = {}
        self._lock = RLock()
        self._client_function = FateArkBlobHashClientFunction(self)

    def _sync_generation(self) -> None:
        generation = self._get_generation()
        with self._lock:
            if generation != self._generation:
                self._cache.clear()
                self._generation = generation

    def is_server(self) -> bool:
        return False

    def is_disk_holder(self) -> bool:
        return False

    def wait_login_sequence_down(self) -> None:
        return

    def load_blob_cache(self, hash_value: int) -> bytes:
        self._sync_generation()
        with self._lock:
            return self._cache.get(hash_value, b"")

    def update_blob_cache(self, hash_value: int, payload: bytes) -> bool:
        self._sync_generation()
        with self._lock:
            self._cache[hash_value] = bytes(payload)
        return True

    def as_server_side(self) -> None:
        return

    def as_mirror_world_side(self) -> None:
        return

    def get_client_function(self) -> FateArkBlobHashClientFunction:
        return self._client_function
