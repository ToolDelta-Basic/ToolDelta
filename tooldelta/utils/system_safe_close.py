from . import (
    tooldelta_thread,
    tempjson,
    timer_events,
    fmts,
    logger
)

def safe_close():
    """安全关闭: 保存JSON配置文件和关闭所有定时任务"""
    timer_events.timer_event_stop.set()
    timer_events.timer_events_clear()
    fmts.print_inf("正在强制中断 ToolDeltaThread..")
    tooldelta_thread.force_stop_normal_threads()
    fmts.print_inf("正在保存数据文件..")
    tempjson.save_all()
    logger.publicLogger.reset()
