import time, os, sys, threading, json, traceback, datetime, platform, subprocess, socket, logging, ctypes, asyncio
import psutil, requests, nbt, qrcode, tqdm, getpass, ujson, pymysql, websockets
from typing import Callable
dotcs_module_env = {"time": time, "os": os, "json": json, "threading": threading, "requests": requests, "traceback": traceback, "qrcode": qrcode, "psutil": psutil, "pymysql": pymysql, "socket": socket, "websockets": websockets}
