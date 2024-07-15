from tooldelta.java_conn.pkt_type import (
    on_client_connect,
    verify_token,
    core_version,
    event_player_join,
    event_player_quit,
    get_online_players,
)

IDMap:dict = {
    0: on_client_connect,
    1: verify_token,
    2: core_version,
    3: event_player_join,
    4: event_player_quit,
    5: get_online_players,
}