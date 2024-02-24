# Manage libraries
try:
    import time, os, sys, threading, json, traceback, datetime, platform, subprocess, socket, logging, ctypes, asyncio, copy, math, random

    sys.path.append(os.path.join(os.getcwd(), "libs"))
    import psutil, requests, nbt, qrcode, getpass, pymysql, websockets, ujson, hashlib, base64, rich.progress
except ModuleNotFoundError as err:
    # 第一次部署该项目, 将会自动安装这些模块.
    from . import get_python_libs

    get_python_libs.try_install_libs(err)
    import time, os, sys, threading, json, traceback, datetime, platform, subprocess, socket, logging, ctypes, asyncio, copy, math, random
    import psutil, requests, nbt, qrcode, getpass, pymysql, websockets, ujson, hashlib, base64, rich.progress

from typing import Callable

dotcs_module_env = {
    "time": time,
    "os": os,
    "json": json,
    "threading": threading,
    "requests": requests,
    "traceback": traceback,
    "qrcode": qrcode,
    "psutil": psutil,
    "pymysql": pymysql,
    "socket": socket,
    "websockets": websockets,
    "datetime": datetime,
    "random": random,
    "math": math,
    "platform": platform,
    "subprocess": subprocess,
    "base64": base64,
    "asyncio": asyncio,
    "sys": sys,
    "rich": rich,
}
