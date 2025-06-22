from dataclasses import dataclass


@dataclass
class QueriedInventoryItemEnchant:
    level: int
    name: str
    type: int

    @classmethod
    def from_dict(cls, dic: dict):
        return cls(level=dic["level"], name=dic["name"], type=dic["type"])


@dataclass
class QueriedInventoryItem:
    aux: int
    enchantments: list[QueriedInventoryItemEnchant]
    freeStackSize: int
    id: str
    maxStackSize: int
    namespace: str
    stackSize: int

    @classmethod
    def from_dict(cls, dic: dict):
        return cls(
            aux=dic["aux"],
            enchantments=[
                QueriedInventoryItemEnchant.from_dict(e) for e in dic["enchantments"]
            ],
            freeStackSize=dic["freeStackSize"],
            id=dic["id"],
            maxStackSize=dic["maxStackSize"],
            namespace=dic["namespace"],
            stackSize=dic["stackSize"],
        )


@dataclass
class QueriedInventory:
    first: int
    last: int
    slotCount: int
    slots: list[QueriedInventoryItem | None]

    @classmethod
    def from_dict(cls, dic: dict):
        return cls(
            first=dic["first"],
            last=dic["last"],
            slotCount=dic["slotCount"],
            slots=[
                QueriedInventoryItem.from_dict(slot) if slot else None
                for slot in dic["slots"]
            ],
        )
