from dataclasses import dataclass
from enum import IntEnum
from tooldelta import tooldelta
from tooldelta.constants import PacketIDS


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


def marshal_abilities(abilities: Abilities) -> int:
    return (
        (abilities.build << Ability.AbilityBuild)
        | (abilities.mine << Ability.AbilityMine)
        | (abilities.doors_and_switches << Ability.AbilityDoorsAndSwitches)
        | (abilities.open_containers << Ability.AbilityOpenContainers)
        | (abilities.attack_players << Ability.AbilityAttackPlayers)
        | (abilities.attack_mobs << Ability.AbilityAttackMobs)
        | (abilities.operator_commands << Ability.AbilityOperatorCommands)
        | (abilities.teleport << Ability.AbilityTeleport)
    )


def unmarshal_abilities(abilities: int) -> Abilities:
    return Abilities(
        build=bool(abilities & (1 << Ability.AbilityBuild)),
        mine=bool(abilities & (1 << Ability.AbilityMine)),
        doors_and_switches=bool(abilities & (1 << Ability.AbilityDoorsAndSwitches)),
        open_containers=bool(abilities & (1 << Ability.AbilityOpenContainers)),
        attack_players=bool(abilities & (1 << Ability.AbilityAttackPlayers)),
        attack_mobs=bool(abilities & (1 << Ability.AbilityAttackMobs)),
        operator_commands=bool(abilities & (1 << Ability.AbilityOperatorCommands)),
        teleport=bool(abilities & (1 << Ability.AbilityTeleport)),
    )


def update_player_abilities(playerUniqueID: int, abilities: Abilities):
    tooldelta.get_game_control().sendPacket(
        PacketIDS.IDRequestAbility,
        {
            "EntityUniqueID": playerUniqueID,
            "PermissionLevel": abilities.auto_permission_level(),
            "RequestedPermissions": marshal_abilities(abilities),
        },
    )
