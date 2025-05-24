from typing import TYPE_CHECKING
from dataclasses import dataclass
from enum import IntEnum
from tooldelta.constants import PacketIDS

if TYPE_CHECKING:
    from tooldelta import GameCtrl
    from ..maintainers.players import PlayerInfoMaintainer
    from .player import Player


class Ability(IntEnum):
    AbilityBuild = 0
    AbilityMine = 1
    AbilityDoorsAndSwitches = 2
    AbilityOpenContainers = 3
    AbilityAttackPlayers = 4
    AbilityAttackMobs = 5
    AbilityOperatorCommands = 6
    AbilityTeleport = 7
    AbilityInvulnerable = 8
    AbilityFlying = 9
    AbilityMayFly = 10
    AbilityInstantBuild = 11
    AbilityLightning = 12
    AbilityFlySpeed = 13
    AbilityWalkSpeed = 14
    AbilityMuted = 15
    AbilityWorldBuilder = 16
    AbilityNoClip = 17
    AbilityPrivilegedBuilder = 18
    AbilityCount = 19


@dataclass
class Abilities:
    build: bool
    mine: bool
    doors_and_switches: bool
    open_containers: bool
    attack_players: bool
    attack_mobs: bool
    operator_commands: bool
    teleport: bool
    # invulnerable: bool
    # flying: bool
    # may_fly: bool
    # instant_build: bool
    # lightning: bool
    # fly_speed: float
    # walk_speed: float
    player_permissions: int
    command_permissions: int

    def auto_permission_level(self):
        if (
            self.build
            and self.mine
            and self.doors_and_switches
            and self.open_containers
            and self.attack_players
            and self.attack_mobs
            and self.operator_commands
            and self.teleport
        ):
            return 2 # 管理员权限
        elif (
            self.build
            and self.mine
            and self.doors_and_switches
            and self.open_containers
            and self.attack_players
            and self.attack_mobs
        ):
            return 1 # 普通玩家权限
        elif not (
            self.build
            or self.mine
            or self.doors_and_switches
            or self.open_containers
            or self.attack_mobs
            or self.attack_players
            or self.operator_commands
            or self.teleport
        ):
            return 0 # 访客权限
        else:
            return 3 # 自定义权限

    def marshal(self) -> int:
        return (
            (self.build << Ability.AbilityBuild)
            | (self.mine << Ability.AbilityMine)
            | (self.doors_and_switches << Ability.AbilityDoorsAndSwitches)
            | (self.open_containers << Ability.AbilityOpenContainers)
            | (self.attack_players << Ability.AbilityAttackPlayers)
            | (self.attack_mobs << Ability.AbilityAttackMobs)
            | (self.operator_commands << Ability.AbilityOperatorCommands)
            | (self.teleport << Ability.AbilityTeleport)
        )

    @classmethod
    def unmarshal(
        cls, abilities: int, player_permissions: int, command_permissions: int
    ):
        abilities = abilities & (
            (1 << Ability.AbilityBuild)
            | (1 << Ability.AbilityMine)
            | (1 << Ability.AbilityDoorsAndSwitches)
            | (1 << Ability.AbilityOpenContainers)
            | (1 << Ability.AbilityAttackPlayers)
            | (1 << Ability.AbilityAttackMobs)
            | (1 << Ability.AbilityOperatorCommands)
            | (1 << Ability.AbilityTeleport)
        )
        return cls(
            build=bool(abilities & (1 << Ability.AbilityBuild)),
            mine=bool(abilities & (1 << Ability.AbilityMine)),
            doors_and_switches=bool(abilities & (1 << Ability.AbilityDoorsAndSwitches)),
            open_containers=bool(abilities & (1 << Ability.AbilityOpenContainers)),
            attack_players=bool(abilities & (1 << Ability.AbilityAttackPlayers)),
            attack_mobs=bool(abilities & (1 << Ability.AbilityAttackMobs)),
            operator_commands=bool(abilities & (1 << Ability.AbilityOperatorCommands)),
            teleport=bool(abilities & (1 << Ability.AbilityTeleport)),
            player_permissions=player_permissions,
            command_permissions=command_permissions,
        )


def upload_player_abilities(
    pkt_sender: "GameCtrl", playerUniqueID: int, abilities: Abilities
):
    pkt_sender.sendPacket(
        PacketIDS.RequestPermissions,
        {
            "EntityUniqueID": playerUniqueID,
            "PermissionLevel": abilities.auto_permission_level(),
            "RequestedPermissions": abilities.marshal(),
        },
    )


def update_player_ability_from_ability_data(
    maintainer: "PlayerInfoMaintainer", player: "Player", ab_data: dict
):
    player_permissions = ab_data["PlayerPermissions"]
    command_permissions = ab_data["CommandPermissions"]
    for layer_data in ab_data["Layers"]:
        if layer_data["Type"] == 1:
            maintainer.player_abilities[player.unique_id] = Abilities.unmarshal(
                layer_data["Values"], player_permissions, command_permissions
            )
