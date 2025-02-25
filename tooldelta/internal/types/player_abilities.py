from typing import TYPE_CHECKING
from dataclasses import dataclass
from enum import IntEnum
from tooldelta.constants import PacketIDS

if TYPE_CHECKING:
    from tooldelta import GameCtrl
    from ..maintainers import PlayerInfoMaintainer
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
        level = 0
        if (
            self.mine
            or self.doors_and_switches
            or self.open_containers
            or self.attack_players
            or self.attack_mobs
        ):
            level += 1
        if self.operator_commands and self.teleport:
            level += 1

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


def update_player_abilities(pkt_sender: "GameCtrl", playerUniqueID: int, abilities: Abilities):
    pkt_sender.sendPacket(
        PacketIDS.IDRequestAbility,
        {
            "EntityUniqueID": playerUniqueID,
            "PermissionLevel": abilities.auto_permission_level(),
            "RequestedPermissions": abilities.marshal(),
        },
    )


def update_player_ability_from_server(
    maintainer: "PlayerInfoMaintainer", player: "Player", packet: dict
):
    ab_data = packet["AbilityData"]
    player_permissions = ab_data["PlayerPermissions"]
    command_permissions = ab_data["CommandPermissions"]
    for layer_data in ab_data["Layers"]:
        if layer_data["Type"] == 1:
            maintainer.player_abilities[player.unique_id] = (
                Abilities.unmarshal(
                    layer_data["Value"], player_permissions, command_permissions
                )
            )
