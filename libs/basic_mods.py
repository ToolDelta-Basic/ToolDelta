import time, os, sys, threading, json, traceback, datetime, subprocess, pymysql, getpass
import psutil, requests, ctypes, nbt, qrcode, logging
from typing import Callable
dotcs_module_env = {"time": time, "os": os, "json": json, "threading": threading, "requests": requests, "traceback": traceback, "qrcode": qrcode, "psutil": psutil, "pymysql": pymysql}