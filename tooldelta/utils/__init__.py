from . import tempjson
from .fbtoken import fbtokenFix, if_token
from .locks import ChatbarLock, players_in_chatbar_lock
from .packet_transition import get_playername_and_msg_from_text_packet
from .safe_json import (
    DataReadError,
    safe_json_dump,
    safe_json_load,
    read_from_plugin,
    write_to_plugin,
)
from .system_safe_close import safe_close
from .timer_events import timer_event, timer_event_boostrap
from .tooldelta_thread import ToolDeltaThread, createThread, thread_func, thread_gather
from .basic import (
    simple_fmt,
    simple_assert,
    try_int,
    try_convert,
    fuzzy_match,
    split_list,
    fill_list_index,
    remove_mc_color_code,
    to_plain_name,
    to_player_selector,
    create_result_cb,
    create_desperate_attr_class,
)

# ---------------- 向下兼容 ---------------


def loadPathJson(
    path: str,
    needFileExists: bool = True,
    timeout: int = 60,
    default=None,
):
    tempjson.load_from_path(
        path, need_file_exists=needFileExists, unload_delay=timeout, default=default
    )


def read_as_tmp(
    path: str,
    needFileExists: bool = True,
    timeout: int = 60,
    default=None,
):
    tempjson.load_and_read(
        path, need_file_exists=needFileExists, timeout=timeout, default=default
    )


def write_as_tmp(
    path: str,
    obj,
    needFileExists: bool = True,
    timeout: int = 60,
    default=None,
):
    tempjson.load_and_write(path, obj, need_file_exists=needFileExists, timeout=timeout)


TMPJson = create_desperate_attr_class(
    "TMPJson",
    [
        loadPathJson,
        read_as_tmp,
        write_as_tmp,
        tempjson.read,
        tempjson.write,
        tempjson.flush,
        tempjson.cancel_change,
        tempjson.get,
        tempjson.get_tmps,
    ],
)
r"""
:class:`TMPJson` 已弃用。
如果想使用其中的函数，请改为使用 `from tooldelta.utils import tempjson`。
"""

TMPJson.unloadPathJson = tempjson.unload_to_path

JsonIO = create_desperate_attr_class("JsonIO", [])
r"""
:class:`JsonIO` 已弃用。
如果想使用其中的函数，请改为使用 `from tooldelta.utils import safe_json`。
"""

JsonIO.readFileFrom = read_from_plugin
JsonIO.writeFileTo = write_to_plugin
JsonIO.SafeJsonLoad = safe_json_load
JsonIO.SafeJsonDump = safe_json_dump
JsonIO.DataReadError = DataReadError

Utils = create_desperate_attr_class(
    "Utils",
    [
        JsonIO,
        TMPJson,
        ChatbarLock,
        ToolDeltaThread,
        simple_fmt,
        simple_assert,
        try_int,
        try_convert,
        fuzzy_match,
        split_list,
        fill_list_index,
        remove_mc_color_code,
        to_plain_name,
        to_player_selector,
        create_result_cb,
        thread_func,
        thread_gather,
        timer_event,
    ],
)
r"""
:class:`Utils` 已弃用。
如果想使用其中的函数，请改为使用 `from tooldelta import utils`。
"""

Utils.createThread = createThread
chatbar_lock_list = players_in_chatbar_lock

# ruff: noqa: F401
