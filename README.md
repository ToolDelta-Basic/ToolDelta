<h1 align="center">ToolDelta - Bot Plugin Loader</h1>
<p align="center">
  <a href="https://github.com/ToolDelta/ToolDelta/releases"><img src="https://img.shields.io/github/v/release/ToolDelta/ToolDelta?display_name=tag&sort=semver" alt="Releases"></a>
  <img src="https://img.shields.io/github/stars/ToolDelta/ToolDelta.svg?style=falt" alt="Stars">
</p>

ToolDelta 是**为《我的世界：中国版》手机端租赁服**制作的、基于机器人的插件加载器，不同于其他类型的插件加载器，ToolDelta 可以运行在**多种游戏交互启动器核心**上。
ToolDelta 的插件可以极大幅提高您的租赁服的玩法上限和优化租赁服的流畅度。

加入我们：[维基和用户指南](https://td-wiki.dqyt.online/) | [交流群](http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=ywf-Y9Sb7G3McLAN7TveI-qh-g1FEtLB&authKey=C0ZLK09UWRzWv9dpReVnZljSnZ15crGpNpdT5O%2BX%2B%2BQvZ%2Bsm2BWfN8qqdJ5OMnTq&noverify=0&group_code=194838530)

## 目录
- [目录](#目录)
- [插件市场](#插件市场)
- [注意事项](#注意事项)
- [友情链接](#友情链接)
- [运行和配置](#运行和配置)



## 插件市场
- ToolDelta 的插件市场在 [这里](https://github.com/ToolDelta-Basic/PluginMarket)



## 注意事项
- 源码运行时，ToolDelta 仅能运行在 Python 3.10+ 版本上


## 友情链接
- [如何使用](https://td-wiki.dqyt.online)
- [Docker 镜像](https://hub.docker.com/r/wlingzhenyu/tooldelta)



## 运行和配置
 - 直接下载 ToolDelta 可执行文件并运行
    - <a href="https://github.com/ToolDelta/ToolDelta/releases">发行版 ToolDelta 下载点这里</a>
 - 在 `pip` 安装 ToolDelta 并运行
    - `pip install tooldelta`
    - `echo import tooldelta;tooldelta.client_title() > main.py`
    运行:
      - `python main.py` 或 `python3 main.py`
 - 在docker运行
    ```bash
    docker run -v .:/app -t -i registry.cn-hangzhou.aliyuncs.com/dqyt/tooldelta:latest
    ```
