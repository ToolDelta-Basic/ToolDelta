"""提供了一些实用方法的类"""

import copy
import ctypes
import json as rjson
import base64
import hashlib   
import os
import ast
import sqlite3
import threading
import time
import traceback
from collections.abc import Callable, Iterable
from sqlite_easy_ctrl import DataBaseSqlit
from io import TextIOWrapper
from typing import Any, TypeVar, List, Tuple, Dict

import ujson as json

from .color_print import Print
from .constants import TOOLDELTA_PLUGIN_DATA_DIR

event_pool = {"timer_events": threading.Event()}
threads_list: list["Utils.createThread"] = []
timer_events_table: dict[int, tuple[str, Callable, tuple, dict]] = {}

VT = TypeVar("VT")


class Utils:
    """提供了一些实用方法的类"""

    class ThreadExit(SystemExit):
        """线程退出."""

    class ToolDeltaThread(threading.Thread):
        """简化 ToolDelta 子线程创建的 threading.Thread 的子类."""

        def __init__(
            self, func: Callable, args: Iterable[Any] = (), usage="", **kwargs
        ):
            """新建一个 ToolDelta 子线程

            Args:
                func (Callable): 线程方法
                args (tuple, optional): 方法的参数项
                usage (str, optional): 线程的用途说明
                kwargs (dict, optional): 方法的关键词参数项
            """
            super().__init__(target=func)
            self.func = func
            self.daemon = True
            self.all_args = [args, kwargs]
            self.usage = usage
            self.start()
            self.stopping = False
            self._thread_id = None

        def run(self) -> None:
            """线程运行方法"""
            threads_list.append(self)
            try:
                self.func(*self.all_args[0], **self.all_args[1])
            except SystemExit:
                pass
            except ValueError as e:
                if str(e) != "未连接到游戏":
                    raise
                Print.print_war(f"线程 {self.usage} 因游戏断开连接被迫中断")
            except Exception:
                Print.print_err(
                    f"线程 {self.usage or self.func.__name__} 出错:\n"
                    + traceback.format_exc()
                )
            finally:
                threads_list.remove(self)

        def get_id(self) -> int:
            """获取线程的 ID

            Raises:
                RuntimeError: 线程 ID 未知

            Returns:
                int: 线程 ID
            """
            if self._thread_id is None:
                for thread in threading.enumerate():
                    if thread is self:
                        self._thread_id = thread.ident
                        break
            if self._thread_id is None:
                raise RuntimeError("Could not determine the thread's ID")
            return self._thread_id

        def stop(self) -> None:
            """终止线程"""
            self.stopping = True
            self._thread_id = self.ident
            thread_id = self.get_id()
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                thread_id, ctypes.py_object(SystemExit)
            )
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
                Print.print_err(f"§c终止线程 {self.name} 失败")

    createThread = ClassicThread = ToolDeltaThread

    class TMPJson:
        """提供了加载、卸载、读取和写入 JSON 文件到缓存区的方法的类."""

        @staticmethod
        def loadPathJson(path: str, needFileExists: bool = True) -> None:
            """
            将 json 文件从磁盘加载到缓存区，以便快速读写.
            在缓存文件已加载的情况下，再使用一次该方法不会有任何作用.

            Args:
                path (str): 作为文件的磁盘内路径的同时也会作为在缓存区的虚拟路径
                needFileExists (bool, optional): 默认为 True, 为 False 时，若文件路径不存在，就会自动创建一个文件，且默认值为 null

            Raises:
                err: 文件不存在时
            """
            if path in jsonPathTmp:
                return
            try:
                with open(path, encoding="utf-8") as file:
                    js = Utils.SimpleJsonDataReader.SafeJsonLoad(file)
            except FileNotFoundError as err:
                if not needFileExists:
                    js = None
                else:
                    raise err from None
            except UnicodeDecodeError:
                Print.print_err(path)
                raise
            jsonPathTmp[path] = [False, js]

        @staticmethod
        def unloadPathJson(path: str) -> bool:
            """
            将 json 文件从缓存区卸载 (保存内容到磁盘), 之后不能再在缓存区对这个文件进行读写.
            在缓存文件已卸载的情况下，再使用一次该方法不会有任何作用，但是可以通过其返回的值来知道存盘有没有成功.

            Args:
                path (str): 文件的虚拟路径

            Returns:
                bool: 存盘是否成功
            """
            if jsonPathTmp.get(path) is not None:
                isChanged, dat = jsonPathTmp[path]
                if isChanged:
                    with open(path, "w", encoding="utf-8") as file:
                        Utils.SimpleJsonDataReader.SafeJsonDump(dat, file)
                del jsonPathTmp[path]
                return True
            return False

        @staticmethod
        def read(path: str) -> Any:
            """对缓存区的该虚拟路径的文件进行读操作，返回一个深拷贝的 JSON 对象

            Args:
                path (str): 文件的虚拟路径

            Raises:
                Exception: json 路径未初始化，不能进行读取和写入操作

            Returns:
                list[Any] | dict[Any, Any] | Any: 该虚拟路径的 JSON
            """
            if path in jsonPathTmp:
                val = jsonPathTmp.get(path)
                if val is not None:
                    val = val[1]
                    if isinstance(val, list | dict):
                        val = copy.deepcopy(val)
                    return val
            raise ValueError("json 路径未初始化，不能进行读取和写入操作：" + path)

        @staticmethod
        def get(path: str) -> None:
            """
            直接获取缓存区的该虚拟路径的 JSON, 不使用 copy
            WARNING: 如果你不知道有什么后果，请老老实实使用`read(...)`而不是`get(...)`!

            Args:
                path (str): 文件的虚拟路径
            """
            if path in jsonPathTmp:
                val = jsonPathTmp.get(path)
                if val is not None:
                    val = val[1]
                    return val
            raise ValueError("json 路径未初始化，不能进行读取和写入操作：" + path)

        @staticmethod
        def write(path: str, obj: Any) -> None:
            """
            对缓存区的该虚拟路径的文件进行写操作，这将会覆盖之前的内容

            Args:
                path (str): 文件的虚拟路径
                obj (Any): 任何合法的 JSON 类型 例如 dict/list/str/bool/int/float
            """
            if path in jsonPathTmp:
                jsonPathTmp[path] = [True, obj]
            else:
                raise ValueError("json 路径未初始化，不能进行读取和写入操作：" + path)

        @staticmethod
        def read_as_tmp(
            path: str, needFileExists: bool = True, timeout: int = 60
        ) -> Any:
            """读取 json 文件并将其从磁盘加载到缓存区，以便一段时间内能快速读写.

            Args:
                path (str): 作为文件的磁盘内路径的同时也会作为在缓存区的虚拟路径
                needFileExists (bool, optional): 默认为 True, 为 False 时，若文件路径不存在，就会自动创建一个文件，且写入默认值 null
                timeout (int, optional): 多久没有再进行读取操作时卸载缓存

            Returns:
                Any: 该虚拟路径的 JSON
            """
            if path not in jsonUnloadPathTmp and path not in jsonPathTmp:
                jsonUnloadPathTmp[path] = timeout + int(time.time())
                Utils.TMPJson.loadPathJson(path, needFileExists)
            return Utils.TMPJson.read(path)

        @staticmethod
        def write_as_tmp(
            path: str, obj: Any, needFileExists: bool = True, timeout: int = 60
        ) -> None:
            """写入 json 文件并将其从磁盘加载到缓存区，以便一段时间内能快速读写.

            Args:
                path (str): 作为文件的磁盘内路径的同时也会作为在缓存区的虚拟路径
                obj (Any): 任何合法的 JSON 类型 例如 dict/list/str/bool/int/float
                needFileExists (bool, optional): 默认为 True, 为 False 时，若文件路径不存在，就会自动创建一个文件，且写入默认值 null
                timeout (int, optional): 多久没有再进行读取操作时卸载缓存
            """
            if path not in jsonUnloadPathTmp and path not in jsonPathTmp:
                jsonUnloadPathTmp[path] = timeout + int(time.time())
                Utils.TMPJson.loadPathJson(path, needFileExists)
            Utils.TMPJson.write(path, obj)

        @staticmethod
        def cancel_change(path: str) -> None:
            """取消缓存 json 所做的更改，非必要情况请勿调用，你不知道什么时候会自动保存所做更改"""
            jsonPathTmp[path][0] = False

        @staticmethod
        def get_tmps() -> dict:
            """不要调用!"""
            return jsonPathTmp.copy()

    class JsonIO:
        """提供了安全的 JSON 文件操作方法的类."""

        @staticmethod
        def SafeJsonDump(obj: Any, fp: TextIOWrapper | str, indent=2) -> None:
            """将一个 json 对象写入一个文件，会自动关闭文件读写接口.

            Args:
                obj (str | dict | list): JSON 对象
                fp (Any): open(...) 打开的文件读写口 或 文件路径
            """
            if isinstance(fp, str):
                with open(fp, "w", encoding="utf-8") as file:
                    file.write(json.dumps(obj, indent=indent, ensure_ascii=False))
            else:
                with fp:
                    fp.write(json.dumps(obj, indent=indent, ensure_ascii=False))

        @staticmethod
        def SafeJsonLoad(fp: TextIOWrapper | str) -> Any:
            """从一个文件读取 json 对象，会自动关闭文件读写接口.

            Args:
                fp (TextIOWrapper | str): open(...) 打开的文件读写口 或文件路径

            Returns:
                dict | list: JSON 对象
            """
            if isinstance(fp, str):
                with open(fp, encoding="utf-8") as file:
                    return json.load(file)
            with fp as file:
                return json.load(file)

        class DataReadError(json.JSONDecodeError):
            """读取数据时发生错误"""

        @staticmethod
        def readFileFrom(
            plugin_name: str, file: str, default: dict | None = None
        ) -> Any:
            """从插件数据文件夹读取一个 json 文件，会自动创建文件夹和文件.

            Args:
                plugin_name (str): 插件名
                file (str): 文件名
                default (dict, optional): 默认值，若文件不存在则会写入这个默认值

            Raises:
                Utils.JsonIO.DataReadError: 读取数据时发生错误
                err: 读取文件路径时发生错误

            Returns:
                dict | list: JSON 对象
            """
            if file.endswith(".json"):
                file = file[:-5]
            filepath = os.path.join(
                TOOLDELTA_PLUGIN_DATA_DIR, plugin_name, f"{file}.json"
            )
            os.makedirs(
                os.path.join(TOOLDELTA_PLUGIN_DATA_DIR, plugin_name), exist_ok=True
            )
            try:
                if default is not None and not os.path.isfile(filepath):
                    with open(filepath, "w") as f:
                        Utils.JsonIO.SafeJsonDump(default, f)
                    return default
                with open(filepath, encoding="utf-8") as f:
                    res = Utils.JsonIO.SafeJsonLoad(f)
                return res
            except rjson.JSONDecodeError as err:
                # 判断是否有 msg.doc.pos 属性
                raise Utils.JsonIO.DataReadError(err.msg, err.doc, err.pos)
            except Exception as err:
                Print.print_err(f"读文件路径 {filepath} 发生错误")
                raise err

        @staticmethod
        def writeFileTo(plugin_name: str, file: str, obj: Any, indent=4) -> None:
            """将一个 json 对象写入插件数据文件夹，会自动创建文件夹和文件.

            Args:
                plugin_name (str): 插件名
                file (str): 文件名
                obj (str | dict[Any, Any] | list[Any]): JSON 对象
            """
            os.makedirs(f"{TOOLDELTA_PLUGIN_DATA_DIR}/{plugin_name}", exist_ok=True)
            with open(
                f"{TOOLDELTA_PLUGIN_DATA_DIR}/{plugin_name}/{file}.json", "w"
            ) as f:
                Utils.JsonIO.SafeJsonDump(obj, f, indent=indent)

    SimpleJsonDataReader = JsonIO

    class ChatbarLock:
        """
        聊天栏锁, 用于防止玩家同时开启多个聊天栏对话

        调用了该锁的所有代码, 在另一个进程使用该锁的时候, 尝试调用其他锁会导致进程直接退出, 直到此锁退出为止

        示例(以类式插件为例):
        ```python
        class MyPlugin(Plugin):
            ...
            def on_player_message(self, player: str, msg: str):
                with ChatbarLock(player):
                    # 如果玩家处在另一个on_player_message进程 (锁环境) 中
                    # 则在上面就会直接引发 SystemExit
                    ...
        ```
        示例(以注入式插件为例):
        ```
        @player_message()
        async def onPlayerChat(info: player_message_info):
            with ChatbarLock(info.playername):
                ...
        ```
        """

        def __init__(self, player: str, oth_cb: Callable[[str], None] = lambda _: None):
            self.player = player
            self.oth_cb = oth_cb

        def __enter__(self):
            if self.player in chatbar_lock_list:
                self.oth_cb(self.player)
                Print.print_war(f"玩家 {self.player} 的线程锁正在锁定状态")
                raise SystemExit
            chatbar_lock_list.append(self.player)

        def __exit__(self, e, e2, e3):
            chatbar_lock_list.remove(self.player)

    class DataBaseSqlit:
        """数据库操作类, 用于简化数据库操作, 并提供一些常用的数据库操作方法"""

        def __init__(self) -> None:
            self.__DataBase__: dict = {}
            self.__DataBaseTableStruct__: dict[str, tuple] = {}

        class DataBaseTagIsNull(Exception):...
        class DataBaseOpenError(Exception):...
        class DataBaseNeedStruct(Exception):...
        class DataBaseTableNameIsNull(Exception):...

        class DataBaseTableStruct:
            """
            数据库表结构类, 用于简化数据库表结构的创建
            只需要提供字段名和他的python类型即可，因为ToolDelta会将数据转成统一类型

            Args:
                *args: tuple[str, type], 字段名和他的Python类型
                例: |
                    DataBaseTableStruct(("id", int), ("name", str))
            """
            def __init__(self, *args: tuple[str, type]) -> None:
                self.TypeTable: dict = {}
                for tup in args:
                    self.__add_value__(*tup)

            def __add_value__(self, name: str, type: type) -> None:
                self.TypeTable[name] = type

        class DataBaseTableCtrl:
            def __init__(self, DataBase, DataBaseTableStruct, Table, Key) -> None:
                self.DataBase = DataBase
                self.DataBaseTableStruct = DataBaseTableStruct
                self.Table = Table
                self.Key = Key
                self.cursor: sqlite3.Cursor = DataBase.cursor()
                self.DataBaseStruct = self.__get_struct__()

            class DataBaseTableSetDataArgsError(Exception):...
            class DataBaseTableGetDataDataLengthError(Exception):...
            class DataBaseTableDataBreakDown(Exception):...
            class DataBaseTableUpdateDataArgsError(Exception):...
            class DataBaseTableRemoveDataArgsError(Exception):...
            
            def __get_struct__(self) -> Any:
                for Name, Struct in self.DataBaseTableStruct:
                    if Name == self.Table:
                        return Struct.TypeTable
                return None

            def set_data(self, *args: Any) -> None:
                """
                新增数据到表中

                Args:
                    data (任何类型): 传入数据

                Raises:
                    DataBaseTableSetDataArgsError: 参数数量不匹配
                """
                num_placeholders = len(self.DataBaseStruct)
                placeholders = ','.join(['?' for _ in range(num_placeholders)])
                if len(args) != num_placeholders:
                    raise self.DataBaseTableSetDataArgsError("参数数量不匹配")
                
                processed_args = []

                for arg in args:
                    base64_arg = base64.b64encode(str(arg).encode('utf-8')).decode('utf-8')
                    processed_args.append(self.__encrypt_text__(base64_arg))
                
                self.cursor.execute(f"INSERT INTO {self.Table} values({placeholders})", processed_args)
                self.cursor.connection.commit()

            def update_data(self, update_values: dict, condition: dict):
                """
                更新表中的数据

                Args:
                    update_values (dict): 更新值字典   例: {"name": "xxx"}
                    condition (dict): 条件字典
                    例:
                        update_values = {"name": "xxx"} # 更新 name 字段为 xxx
                        condition = {"id": 1} # 条件为 id = 1
                """
                processed_update_values = {}
                for key, value in update_values.items():
                    base64_value = base64.b64encode(str(value).encode('utf-8')).decode('utf-8')
                    processed_update_values[key] = self.__encrypt_text__(base64_value)

                processed_condition = {}
                for key, value in condition.items():
                    base64_value = base64.b64encode(str(value).encode('utf-8')).decode('utf-8')
                    processed_condition[key] = self.__encrypt_text__(base64_value)

                update_set_clause = ', '.join([f"{key} = ?" for key in processed_update_values.keys()])
                condition_clause = ' AND '.join([f"{key} = ?" for key in processed_condition.keys()])
                sql = f"UPDATE {self.Table} SET {update_set_clause} WHERE {condition_clause}"

                self.cursor.execute(sql, list(processed_update_values.values()) + list(processed_condition.values()))
                self.cursor.connection.commit()

            def remove_data(self, condition: dict) -> None:
                """
                从表中删除数据
                
                Args:
                    condition (dict): 条件字典   例: {"id": 1}

                Raises:
                    DataBaseTableRemoveDataArgsError: condition 为空
                """
                if not condition:
                    raise self.DataBaseTableRemoveDataArgsError("condition 不能为空")
                
                where_clause = " AND ".join([f"{key} = ?" for key in condition.keys()])
                where_values = list(condition.values())
                sql = f"DELETE FROM {self.Table} WHERE {where_clause}"

                for arg in where_values:
                    base64_arg = base64.b64encode(str(arg).encode('utf-8')).decode('utf-8')
                    where_values.remove(arg)
                    where_values.append(self.__encrypt_text__(base64_arg))

                self.cursor.execute(sql, where_values)
                self.cursor.connection.commit()

            def get_data(self, idx: int = -1) -> List[Dict]:
                """
                从表中获取数据
                
                Args:
                    idx (int, optional): 索引, 默认为 -1, 即获取所有数据

                return:
                    List[Dict]: 表内所有数据
                """
                self.cursor.execute(f"SELECT * FROM {self.Table}")
                result = []
                for item in self.cursor:
                    decoded_item = tuple(base64.b64decode(self.__decrypt_text__(value)).decode('utf-8') for value in item)
                    result.append(decoded_item)
                original_item = self.restore_data_format(result) # type: ignore
                if idx == -1:
                    return original_item
                else:
                    if idx >= len(original_item):
                        raise self.DataBaseTableGetDataDataLengthError("数据长度不匹配!")
                    return original_item[idx] # type: ignore

            def restore_data_format(self, data: List[Tuple]) -> List[Dict]:
                """
                使用 DataBaseStruct 恢复原数据格式
                
                Args:
                    data (List[Tuple]): 数据库内的数据

                Raises:
                    DataBaseTableDataBreakDown: 数据库结构可能损坏!

                Returns:
                    List[Dict]: 原数据格式
                """
                try:
                    if not self.DataBaseStruct:
                        raise self.DataBaseTableSetDataArgsError("DataBaseStruct is not initialized.")

                    restored_data = []
                    for row in data:
                        restored_row = {}
                        for idx, (key, value) in enumerate(zip(self.DataBaseStruct.keys(), row)):
                            if self.DataBaseStruct[key] == dict:
                                restored_row[key] = json.loads(value.replace('"', "").replace("'", '"'))
                            elif self.DataBaseStruct[key] == list:
                                restored_row[key] = ast.literal_eval(value.replace('"', "").replace("'", '"'))
                            elif self.DataBaseStruct[key] == tuple:
                                restored_row[key] = eval(value)
                            else:
                                restored_row[key] = self.DataBaseStruct[key](value)
                        restored_data.append(restored_row)
                    return restored_data
                except:
                    raise self.DataBaseTableDataBreakDown("数据库结构可能损坏!")

            def __encrypt_text__(self, text: str) -> str:
                if not self.Key:
                    return text
                password_bytes = self.Key.encode('utf-8')
                sha256 = hashlib.sha256()
                sha256.update(password_bytes)
                text_bytes = text.encode('utf-8')
                encrypted_bytes = bytearray()
                for i in range(len(text_bytes)):
                    encrypted_bytes.append(text_bytes[i] ^ sha256.digest()[i % len(sha256.digest())])
                return encrypted_bytes.hex()

            def __decrypt_text__(self, encrypted_text: str) -> str:
                if not self.Key:
                    return encrypted_text
                password_bytes = self.Key.encode('utf-8')
                sha256 = hashlib.sha256()
                sha256.update(password_bytes)
                encrypted_bytes = bytearray.fromhex(encrypted_text)
                decrypted_bytes = bytearray()
                for i in range(len(encrypted_bytes)):
                    decrypted_bytes.append(encrypted_bytes[i] ^ sha256.digest()[i % len(sha256.digest())])
                return decrypted_bytes.decode('utf-8')

            def Del_Table(self) -> None:
                self.cursor.execute(f"DROP TABLE {self.Table}")
        
        def OpenDataBase(self, Tag: str = None, Key: str = None, Temp: bool = False) -> None: # type: ignore
            """
            打开一个数据包通过Tag, 若Tag不存在则创建新的数据库
            
            Args:
                Tag (str, optional): 数据库的标签
                Key (bytes, optional): 数据库的密钥[可选]
                Temp (bool, optional): 是否为临时数据库

            Raises:
                DataBaseTagIsNull: Tag不能为空
                DataBaseOpenError: 数据库打开失败!
            """
            if not Tag:
                raise self.DataBaseTagIsNull("Tag不能为空")
            if not Temp:
                if not os.path.exists(f"数据库文件/{Tag}"):
                    os.makedirs(f"数据库文件/{Tag}")
                self.__DataBase__[Tag] = {"Conn": sqlite3.connect(f"数据库文件/{Tag}/DataBase-{Tag}.db", check_same_thread=False),"Key": Key, "IsTemp": False}
            elif Temp: # type: ignore
                self.__DataBase__[Tag] = {"Conn": sqlite3.connect(":memory:", check_same_thread=False), "Key": Key, "IsTemp": True}
            
            if self.__DataBase__.get(Tag) is None:
                raise self.DataBaseOpenError("数据库打开失败!")

        def OpenDataBaseTable(self, Tag: str, TableName: str, Key: str = None, TableStruct: DataBaseTableStruct = None) -> DataBaseTableCtrl: # type: ignore
            """
            通过Tag打开一个数据库的对应数据包

            Args:
                Tag (str): 数据库的标签
                TableName (str): 数据库的表名
                Key (bytes, optional): 数据库的密钥[可选]

            Raises:
            """
            if not self.__DataBase__.get(Tag):
                raise self.DataBaseTagIsNull("数据库标签不存在!")
            if not TableStruct:
                raise self.DataBaseNeedStruct("数据库结构不能为空!")
            if not TableName:
                raise self.DataBaseTableNameIsNull("数据库表名不能为空!")

            cursor: sqlite3.Cursor = self.__DataBase__[Tag]["Conn"].cursor()
            TableVString: str = ""

            for i in TableStruct.TypeTable:
                TableVString += f"{i} TEXT,"

            cursor.execute(f"CREATE TABLE IF NOT EXISTS {TableName}({TableVString[:-1]})")

            if self.__DataBaseTableStruct__.get(Tag) is None:
                self.__DataBaseTableStruct__[Tag] = [(TableName, TableStruct)] # type: ignore
            else:
                self.__DataBaseTableStruct__[Tag].append((TableName, TableStruct)) # type: ignore

            return self.DataBaseTableCtrl(self.__DataBase__[Tag]["Conn"], self.__DataBaseTableStruct__[Tag], TableName, self.__DataBase__[Tag]["Key"]) # type: ignore

        def CloseDataBase(self, Tag: str) -> None: # type: ignore
            """
            关闭一个数据库

            Args:
                Tag (str): 数据库的标签

            Raises:
                DataBaseTagIsNull: Tag不能为空
            """
            if not Tag:
                raise self.DataBaseTagIsNull("Tag不能为空")

            if self.__DataBase__.get(Tag) is not None:
                self.__DataBase__[Tag]["Conn"].close()
                del self.__DataBase__[Tag]

    DataBase = DataBaseSqlit()
    # 例:
        # DataBase = DataBaseSqlit()
        # DataBase.OpenDataBase("Test-DataBase", "123456", False)
        # Table = DataBase.OpenDataBaseTable("Test-DataBase", "test", "123456", DataBase.DataBaseTableStruct(("id", int), ("isOp", bool), ("pos", tuple)))
        # Table.set_data(1, True, (1, -1, 6))
        # Table.get_data()
        # Table.update_data({"isOp": False}, {"id": 1})
        # Table.get_data()
        # Table.Del_Table()
        # DataBase.CloseDataBase("Test-DataBase")

    @staticmethod
    def get_threads_list() -> list["Utils.createThread"]:
        """返回使用 createThread 创建的全线程列表。"""
        return threads_list

    @staticmethod
    def simple_fmt(kw: dict[str, Any], sub: str) -> str:
        """
        快速将字符串内按照给出的 dict 的键值对替换掉内容.

        参数:
            kw: Dict[str, Any], 键值对应替换的内容
            *args: str, 需要被替换的字符串

        示例:
            >>> my_color = "red"; my_item = "apple"
            >>> kw = {"[颜色]": my_color, "[物品]": my_item}
            >>> Utils.SimpleFmt(kw, "I like [颜色] [物品].")
            I like red apple.
        """
        for k, v in kw.items():
            if k in sub:
                sub = sub.replace(k, str(v))
        return sub

    SimpleFmt = simple_fmt

    @staticmethod
    def simple_assert(cond: Any, exc: Any) -> None:
        """相当于 assert cond, 但是可以自定义引发的异常的类型"""
        if not cond:
            raise exc

    simpleAssert = simple_assert

    @staticmethod
    def thread_func(func_or_name: Callable | str) -> Any:
        """
        在事件方法可能执行较久会造成堵塞时使用，方便快捷地创建一个新线程，例如:

        ```python
        @Utils.thread_func
        def on_inject(self):
            ...
        ```
        或者:
        ```python
        @Utils.thread_func("一个会卡一分钟的线程")
        def on_inject(self):
            ...
        ```
        """
        if isinstance(func_or_name, str):

            def _recv_func(func: Callable):
                def thread_fun(*args: tuple, **kwargs: Any) -> None:
                    Utils.createThread(func, usage=func_or_name, args=args, **kwargs)

                return thread_fun

            return _recv_func

        def thread_fun(*args: tuple, **kwargs: Any) -> None:
            Utils.createThread(
                func_or_name,
                usage="简易线程方法：" + func_or_name.__name__,
                args=args,
                **kwargs,
            )

        return thread_fun

    @staticmethod
    def timer_event(t: int, name: str | None = None):
        """
        将修饰器下的方法作为一个定时任务, 每隔一段时间被执行一次。
        注意: 请不要在函数内放可能造成堵塞的内容
        注意: 当此函数被修饰后, 需要调用一次才能开始定时任务线程!

        Args:
            seconds (int): 周期秒数
            name (Optional[str], optional): 名字, 默认为自动生成的
        """

        def receiver(func: Callable[[], None] | Callable[[Any], None]):
            def caller(*args, **kwargs):
                func_name = name or f"简易方法:{func.__name__}"
                timer_events_table[t] = (func_name, func, args, kwargs)

            return caller

        return receiver

    @staticmethod
    def try_int(arg: Any) -> int | None:
        """尝试将提供的参数化为 int 类型并返回，否则返回 None"""
        try:
            return int(arg)
        except Exception:
            return None

    @staticmethod
    def fuzzy_match(lst: list[str], sub: str) -> list[str]:
        """
        模糊匹配列表内的字符串，可以用在诸如模糊匹配玩家名的用途

        参数:
            lst: list, 字符串列表
            sub: str, 需要匹配的字符串
        返回:
            list, 匹配结果
        """
        res = []
        for i in lst:
            if sub in i:
                res.append(i)
        return res

    @staticmethod
    def split_list(lst: list[VT], length: int) -> list[list[VT]]:
        """
        将列表进行块分割

        Args:
            lst (list[VT]): 传入列表
            length (int): 分割的单个列表的长度

        Returns:
            list[list[VT]]: 传出的被分割的列表
        """
        return [lst[i : i + length] for i in range(0, len(lst), length)]

    @staticmethod
    def to_plain_name(name: str) -> str:
        """去除 网易版 Minecraft 的名字中的颜色代码

        Args:
            name (str): 玩家名

        Returns:
            str: 去除颜色代码后的名字
        """
        if name.startswith("§"):
            cleaned_name = "".join(
                char
                for i, char in enumerate(name)
                if char != "§" and (i == 0 or name[i - 1] != "§")
            )

            last_word, temp_word = [], []
            in_brackets = False

            for char in cleaned_name:
                if char == "<":
                    in_brackets = True
                    temp_word = []
                elif char == ">":
                    in_brackets = False
                    last_word = temp_word[:]
                elif in_brackets:
                    temp_word.append(char)

            return "".join(last_word)
        return name

    DataBase = DataBaseSqlit()
    # 例:
        # DataBase = DataBaseSqlit()
        # DataBase.OpenDataBase("Test-DataBase", "123456", False)
        # Table = DataBase.OpenDataBaseTable("Test-DataBase", "test", "123456", DataBase.DataBaseTableStruct(("id", int), ("isOp", bool), ("pos", tuple)))
        # Table.set_data(1, True, (1, -1, 6))
        # Table.get_data()
        # Table.update_data({"isOp": False}, {"id": 1})
        # Table.get_data()
        # Table.Del_Table()
        # DataBase.CloseDataBase("Test-DataBase")

def safe_close() -> None:
    """安全关闭"""
    event_pool["timer_events"].set()
    _tmpjson_save()


def _tmpjson_save():
    "请不要在系统调用以外调用"
    for k, (isChanged, dat) in jsonPathTmp.copy().items():
        if isChanged:
            Utils.SimpleJsonDataReader.SafeJsonDump(dat, k)
            jsonPathTmp[k][0] = False
    for k, v in jsonUnloadPathTmp.copy().items():
        if time.time() - v > 0:
            Utils.TMPJson.unloadPathJson(k)
            del jsonUnloadPathTmp[k]


@Utils.timer_event(1, "缓存JSON数据定时保存")
@Utils.thread_func("JSON 缓存文件定时保存")
def tmpjson_save():
    "请不要在系统调用以外调用"
    _tmpjson_save()


@Utils.thread_func("ToolDelta 定时任务")
def timer_event_boostrap():
    "请不要在系统调用以外调用"
    timer = 0
    evt = event_pool["timer_events"]
    while not evt.is_set():
        for k, (_, v, a, kwa) in timer_events_table.items():
            if timer % k == 0:
                v(*a, **kwa)
        evt.wait(1)
        timer += 1


jsonPathTmp = {}
chatbar_lock_list = []
jsonUnloadPathTmp = {}
