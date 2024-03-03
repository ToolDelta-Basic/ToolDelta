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
  <code>ToolDelta</code> 是依赖于 <code>PhoenixBuilder | NeOmega</code> 的多功能扩展组件，可以加载各种各样有趣的插件。   
  <code>ToolDelta</code> 可以使得你的 <b>中国版《我的世界》手机版租赁服</b> 的玩法和功能更加多样化。
</p>

# 目录

- [目录](#目录)
- [注意事项](#注意事项)
- [在docker运行](#在docker运行)
- [更新日志](#更新日志)

# 注意事项

- 遇到平台不兼容的情况请尽快提交 `Issue`
- 已支持 `Termux`

How to use?：[learn-use](https://tooldelta-wiki.tblstudio.cn/learn-use.html)

Docker Image: [DockerHub](https://hub.docker.com/r/wlingzhenyu/tooldelta)

# 在docker运行

```bash
docker run -v .:/app -t -i wlingzhenyu/tooldelta:latest
```


# 更新日志

- `0.1.6`

  * 📦 兼容了 dotcs 插件的加载
- `0.1.7`

  * 📦 更新了 [PhoenixBuilder](https://github.com/LNSSPsd/PhoenixBuilder) 下载
  * ✨ 新增了一种输出方式 `rich(0.1.3)`
  * 支持了 `§r` 重置字体及颜色(默认: `#FFFFFF`)
  * ✨ 支持了视窗系统 `Windows` 中自动检测 `fbtoken` 并启动
- `0.1.8`

  * ✨ 新增缺失部分文件自动补全功能
  * Beta - 重写了 `cfg.py` 的代码使之更具人类可读性
  * Sigma - 兼容了 `NeOmega` 系统， 可在其上运行
- `0.2.8`

  * 由于 `FastBuilder External` 停止更新, ToolDelta 不再对其进行进一步的支持.
  * 📦 更新了 `插件市场` 功能
  * ✨ 新增 `注入式插件` 加载方法
  * 重整文件目录结构 并上传到 `PyPi` 使 ToolDelta
- `0.2.9`
- `0.3.0`
* `0.3.1`
  * ✨ 加入`项目地址`， 更新`插件市场最终样式`
* `0.3.2`

  * 📦 更新欢迎提示和打印信息
  * 🐛 修复下载文件名重复问题
  * 🐛 修复颜色问题
* `0.3.3`

  * 🐛 修复严重错误 在`SafeJsonDump`方法上只读 & 新增方法
* `0.3.4`

  * 🐛 修复`readFrom`的严重恶性Bug
  * `Remote NeOmg`模式下不再检测文件完整性
* `0.3.5`

  * 📦 更新插件加载代码，导入了`sys`模块以及修改了插件文件路径
* `0.3.6`

  * 🐛 更新插件 -> 插件市场小修复: 回车键无法自动回溯上次的操作
* `0.3.7`

  * 🚑 更新插件类型为经典
  * ✨ 新增接口和注入式接入死亡时间和类型注释
  * ✨ 新增死亡返回与更新作者信息与版本号
* `0.3.8`

  * 🐛 修复参数给的不到位的原因
  * 📦 更新依赖库版本和内容哈希值
  * ✨ 新增安装脚本
* `0.3.9`

  * 📦 更新`pyproject.toml`文件中的依赖库版本
* `0.3.10`

  * 📦 优化安装脚本，支持Termux平台
* `0.3.11`
* `0.3.12`

  * 📦 更新同步版本工作流程文件
* `0.3.13`

  * 🐛 修复不是插件配置的bug
  * 📦 地图画导入 优化
  * 📦 更新发言频率插件
  * ✨ 添加地图画所需库PIL的支持
  * 📦 对未来类型注释提供必要性的帮助
  * 📦 更新了代码中的导入语句
  * ✨📖 添加函数文档
* `0.3.14`
  * 📦 更新插件市场的__init__.py文件
  * ✨创建基于Python-3.12.1版本的ToolDelta的Docker镜像文件
  * ✨首次提交可以自动编译镜像并创建容器的脚本
