from tooldelta.internal.launch_cli.fateark_libs.blob_hash_holder import (
    FateArkBlobHashHolder,
)
from tooldelta.internal.launch_cli.neo_libs.blob_hash.packet.define import (
    HashWithPosition,
)


def test_fateark_blob_hash_holder_fetches_and_caches_payloads() -> None:
    requests: list[list[int]] = []

    def request_hashes(hashes: list[int]) -> dict[int, bytes]:
        requests.append(hashes)
        return {1: b"one", 2: b"two"}

    holder = FateArkBlobHashHolder(request_hashes, lambda: 1)
    first = HashWithPosition(hash=1)
    second = HashWithPosition(hash=2)

    result = holder.get_client_function().get_hash_payload([first, second])

    assert requests == [[1, 2]]
    assert result == {first: b"one", second: b"two"}
    assert holder.load_blob_cache(1) == b"one"
    assert holder.load_blob_cache(2) == b"two"


def test_fateark_blob_hash_holder_clears_cache_on_reconnect() -> None:
    generation = 1
    holder = FateArkBlobHashHolder(lambda _hashes: {}, lambda: generation)
    holder.update_blob_cache(1, b"old-world")

    generation = 2

    assert holder.load_blob_cache(1) == b""
