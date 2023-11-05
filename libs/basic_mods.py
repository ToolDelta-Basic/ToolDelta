import libs.get_python_libs as _get_py_libs
try:
    import time, os, sys, threading, json, traceback, datetime, platform, subprocess, socket, logging, ctypes, asyncio, copy, math, random
    import psutil, requests, nbt, qrcode, getpass, pymysql, websockets, ujson, hashlib, base64, rich.progress
except ModuleNotFoundError:
    _get_py_libs.try_install_libs()
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
