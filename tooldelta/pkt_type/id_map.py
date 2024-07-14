from tooldelta.pkt_type import (
    on_client_connect,
    verify_token,
    core_version,
    event_player_join
)

IDMap:dict = {
    0: on_client_connect,
    1: verify_token,
    2: core_version,
    3: event_player_join
}