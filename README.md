<h1 align="center">ToolDelta - Multi Platform Edition</h1>
<p align="center">
  <a href="https://github.com/SuperScript-PRC/ToolDelta/releases"><img src="https://img.shields.io/github/v/release/SuperScript-PRC/ToolDelta?display_name=tag&sort=semver" alt="Releases"></a>
  <img src="https://img.shields.io/github/stars/SuperScript-PRC/ToolDelta.svg?style=falt" alt="Stars">
</p>
  
<p align="center">
  <a href="https://github.com/SuperScript-PRC/ToolDelta/issues"><img src="https://img.shields.io/github/issues/SuperScript-PRC/ToolDelta.svg?style=flat" alt="opissues"></a>
  <a href="https://github.com/SuperScript-PRC/ToolDelta/issues?q=is%3Aissue+is%3Aclosed"><img src="https://img.shields.io/github/issues-closed/SuperScript-PRC/ToolDelta.svg?style=flat&color=success" alt="clissues"></a>
  <a href="https://github.com/SuperScript-PRC/ToolDelta/pulls"><img src="https://img.shields.io/github/issues-pr/SuperScript-PRC/ToolDelta.svg?style=falt" alt="oppr"></a>
  <a href="https://github.com/SuperScript-PRC/ToolDelta/pulls?q=is%3Apr+is%3Aclosed"><img src="https://img.shields.io/github/issues-pr-closed/SuperScript-PRC/ToolDelta.svg?style=flat&color=success" alt="clpr"></a>
</p>

<p align="center">
  <code>TooldDelta</code> 是依赖于 <code>PhoenixBuilder | NeOmega</code> 的多功能扩展组件，可以加载各种各样有趣的插件。
</p>




# 目录
- [目录](#目录)
- [注意事项](#注意事项)
- [更新日志](#更新日志)


# 注意事项
- 遇到平台不兼容的情况请尽快提交 `Issue`
- 由于环境问题, ToolDelta 无法在 `Termux` 平台上部署, 见谅.

# 更新日志
- `0.1.6`
  * 兼容了 dotcs 插件的加载
- `0.1.7`
  * 更新了 [PhoenixBuilder](https://github.com/LNSSPsd/PhoenixBuilder) 下载
  * 新增了一种输出方式 `rich(0.1.3)`
    * 支持了 `§r` 重置字体及颜色(默认: `#FFFFFF`)
  * 支持了视窗系统 `Windows` 中自动检测 `fbtoken` 并启动
- `0.1.8`
  * 新增缺失部分文件自动补全功能
  * Beta - 重写了 `cfg.py` 的代码使之更具人类可读性
  * Sigma - 兼容了 `NeOmega` 系统， 可在其上运行
- `0.2.8`
  * 由于 `FastBuilder External` 停止更新, ToolDelta 不再对其进行进一步的支持.
  * 更新了 `插件市场` 功能
  * 新增 `注入式插件` 加载方法
  * 重整文件目录结构 并上传到 `PyPi` 使 ToolDelta 可以作为一个库运行