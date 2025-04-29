class BaseBytesPacket:
    def name(self) -> str:
        return ""

    def custom_packet_id(self) -> int:
        return -1

    def real_packet_id(self) -> int:
        return -1

    def encode(self) -> bytes:
        return b""

    def decode(self, bs: bytes):
        return
