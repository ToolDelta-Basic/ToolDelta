import atexit, os, time

class ToolDeltaLogger:
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"
    OTHER_TYPE = "???"
    def __init__(self, log_path, name_fmt = "%Y-%m-%d"):
        self.path = log_path
        self.name_fmt = name_fmt
        self.now_day = time.strftime("%Y-%m-%d")
        self.logging_fmt = "[%H-%M-%S]"
        self.lastLogTime = time.time()
        self.open_wrapper_io(log_path)
        atexit.register(self._exit)

    def open_wrapper_io(self, log_path: str):
        self._wrapper = open(
            log_path + os.sep + time.strftime(self.name_fmt) + ".log", 
            "a",
            encoding = "utf-8",
            buffering = 1024
        )

    def log_in(self, msg, level = INFO):
        if not isinstance(msg, str): raise TypeError
        if "\n" in msg: msg = msg.replace("\n", "\n    ")
        if len(msg) > 200: msg = msg[:200] + "..."
        self._check_is_another_day()
        self._wrapper.write(time.strftime(self.logging_fmt) + f" [{level}] " + (msg if msg.endswith("\n") else msg + "\n"))
        if time.time() - self.lastLogTime > 10:
            self.save_log()
            self.lastLogTime = time.time()

    def save_log(self):
        self._wrapper.flush()

    def _check_is_another_day(self):
        if time.strftime("%Y-%m-%d") != self.now_day:
            self._exit()
            self.open_wrapper_io(self.path)

    def _exit(self):
        self.save_log()
        self._wrapper.close()

def new_logger(log_path: str):
    os.makedirs(log_path, exist_ok = True)
    return ToolDeltaLogger(log_path)

publicLogger = new_logger("日志文件")
