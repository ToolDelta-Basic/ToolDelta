# Manage libraries
try:
    import time
    import os
    import re
    import sys
    import threading
    import json
    import traceback
    import datetime
    import platform
    import subprocess
    import socket
    import logging
    import ctypes
    import asyncio
    import copy
    import math
    import random
    import psutil
    import pyspeedtest
    import requests
    import nbt
    import qrcode
    import getpass
    import pymysql
    import websockets
    import tarfile
    import gzip
    import importlib
    import ujson
    import hashlib
    import base64
    import rich
    import tqdm

    sys.path.append(os.path.join(os.getcwd(), "libs"))

except ModuleNotFoundError as err:
    # 第一次部署该项目, 将会自动安装这些模块.
    from . import get_python_libs

    get_python_libs.try_install_libs(err)
    import psutil
    import requests
    import nbt
    import qrcode
    import getpass
    import pymysql
    import websockets
    import ujson
    import hashlib
    import base64
    import rich

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
