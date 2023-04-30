import time, os, sys, threading, json, traceback, datetime, subprocess, pymysql
import psutil, requests, ctypes, nbt, qrcode, rich, numpy, bdx_work_shop
from typing import Callable
dotcs_module_env = {"time": time, "os": os, "json": json, "threading": threading, "requests": requests, "traceback": traceback, "qrcode": qrcode, "numpy": numpy, "bdx_work_shop": bdx_work_shop, "psutil": psutil, "pymysql": pymysql}