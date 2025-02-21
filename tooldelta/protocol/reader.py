from typing import TypeVar
from collections.abc import Callable

VT = TypeVar("VT")


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0
        self.len = len(data)

    def read_byte(self):
        if self.offset >= self.len:
            raise ValueError(f"EOF: {self.offset}")
        value = self.data[self.offset]
        self.offset += 1
        return value

    def var_uint32(self):
        value = 0
        for i in range(5):
            byte = self.read_byte()
            value |= (byte & 0x7F) << (i * 7)
            if byte & 0x80 == 0:
                break
            elif i == 4:
                raise ValueError("VarUInt32 is too big")
        return value

    def uint8(self) -> int:
        return self.read_byte()

    def int8(self):
        return self.uint8() - 128

    def uint16(self):
        return self.uint8() | (self.uint8() << 8)

    def int16(self):
        return self.int8() | (self.int8() << 8)

    def bool(self) -> bool:
        value = self.uint8()
        return value == 1

    def string(self):
        strlen = self.var_uint32()
        value = self.data[self.offset : self.offset + strlen].decode()
        self.offset += strlen
        return value

    def bytes(self):
        length = self.var_uint32()
        value = self.data[self.offset : self.offset + length]
        self.offset += length
        return value

    def list(self, fnc: Callable[[], VT]) -> list[VT]:
        count = self.var_uint32()
        ls = []
        for _ in range(count):
            ls.append(fnc())
        return ls

