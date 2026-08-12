"""插件市场源和 GitHub 镜像的控制台配置命令。"""

from urllib.parse import urlparse

from ..constants import PLUGIN_MARKET_SOURCE_OFFICIAL
from ..constants.tooldelta_cfg import LAUNCH_CFG_STD
from ..plugin_market import market
from ..utils import cfg, fmts, urlmethod
from . import regist_extend_function
from .basic import ExtendFunction


CONFIG_PATH = "ToolDelta基本配置.json"
CONFIG_KEYS = {
    "plugin_market": "插件市场源",
    "github_mirror": "全局GitHub镜像",
}
CONFIG_KEYS_HINT = "plugin_market|github_mirror"


def _normalize_url(value: str) -> str:
    """校验并规范化配置 URL。"""
    if any(char.isspace() for char in value):
        raise ValueError
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError
    return value.rstrip("/")


@regist_extend_function
class PluginConfig(ExtendFunction):
    """管理插件市场源和全局 GitHub 镜像。"""

    def when_activate(self):
        """激活扩展并注册控制台命令。"""
        super().when_activate()
        self.when_console_cmd_reset()

    def when_console_cmd_reset(self):
        """注册插件源配置命令。"""
        self.frame.add_console_cmd_trigger(
            ["plg config set"],
            f"<{CONFIG_KEYS_HINT}> <URL>",
            "设置插件市场源或全局 GitHub 镜像",
            self.on_set_config,
        )
        self.frame.add_console_cmd_trigger(
            ["plg config unset"],
            f"<{CONFIG_KEYS_HINT}>",
            "清除插件市场源或全局 GitHub 镜像的自定义值",
            self.on_unset_config,
        )
        self.frame.add_console_cmd_trigger(
            ["plg config list"],
            None,
            "查看插件市场源和全局 GitHub 镜像",
            self.on_list_config,
        )

    def on_set_config(self, args: list[str]) -> None:
        """设置并立即应用指定配置。"""
        if len(args) != 2:
            self._print_usage("set")
            return
        key, value = args
        if not self._check_key(key):
            return
        try:
            value = _normalize_url(value)
        except ValueError:
            fmts.print_err("URL 必须是包含主机名的 http:// 或 https:// 地址")
            return
        if self._save_config(key, value):
            self._apply_config(key, value)
            fmts.print_suc(f"已设置 {key}: {value}，当前进程已生效")

    def on_unset_config(self, args: list[str]) -> None:
        """清除指定配置并恢复运行时默认值。"""
        if len(args) != 1:
            self._print_usage("unset")
            return
        key = args[0]
        if not self._check_key(key):
            return
        if self._save_config(key, ""):
            self._apply_config(key, "")
            effective_value = self._get_effective_value(key)
            fmts.print_suc(f"已清除 {key} 的自定义值，当前使用: {effective_value}")

    def on_list_config(self, args: list[str]) -> None:
        """显示配置值及当前生效值。"""
        if args:
            self._print_usage("list")
            return
        configs = self._load_config()
        if configs is None:
            return
        fmts.print_inf("插件源配置:")
        for key, config_key in CONFIG_KEYS.items():
            configured_value = configs[config_key] or "自动"
            effective_value = self._get_effective_value(key)
            fmts.print_inf(f" {key}: 配置={configured_value}，当前={effective_value}")

    @staticmethod
    def _check_key(key: str) -> bool:
        """检查命令使用的配置键。"""
        if key in CONFIG_KEYS:
            return True
        fmts.print_err(f"未知配置项 {key!r}，可用项: {', '.join(CONFIG_KEYS)}")
        return False

    @staticmethod
    def _load_config() -> dict | None:
        """读取 ToolDelta 基本配置。"""
        try:
            return cfg.get_cfg(CONFIG_PATH, LAUNCH_CFG_STD)
        except (OSError, cfg.ConfigError) as err:
            fmts.print_err(f"读取 ToolDelta 基本配置失败: {err}")
            return None

    def _save_config(self, key: str, value: str) -> bool:
        """保留其他配置项并持久化指定值。"""
        configs = self._load_config()
        if configs is None:
            return False
        configs[CONFIG_KEYS[key]] = value
        try:
            cfg.write_default_cfg_file(CONFIG_PATH, configs, force=True)
        except OSError as err:
            fmts.print_err(f"保存 ToolDelta 基本配置失败: {err}")
            return False
        return True

    @staticmethod
    def _apply_config(key: str, value: str) -> None:
        """将配置应用到当前运行中的客户端。"""
        if key == "plugin_market":
            market.set_source_url(value or PLUGIN_MARKET_SOURCE_OFFICIAL)
            return
        urlmethod.set_global_github_src_url(value)

    @staticmethod
    def _get_effective_value(key: str) -> str:
        """获取当前进程实际使用的配置值。"""
        if key == "plugin_market":
            return market.plugin_market_content_url
        return urlmethod.get_global_github_src_url()

    @staticmethod
    def _print_usage(command: str) -> None:
        """输出子命令的正确用法。"""
        usages = {
            "set": f"plg config set <{CONFIG_KEYS_HINT}> <URL>",
            "unset": f"plg config unset <{CONFIG_KEYS_HINT}>",
            "list": "plg config list",
        }
        fmts.print_err(f"用法: {usages[command]}")
