<h1 align="center">ToolDelta - Bot Plugin Loader</h1>

<p align="center">
  <a href="https://github.com/ToolDelta/ToolDelta/releases"><img src="https://img.shields.io/github/v/release/ToolDelta/ToolDelta?display_name=tag&sort=semver" alt="Releases"></a>
  <img src="https://img.shields.io/github/stars/ToolDelta/ToolDelta.svg?style=falt" alt="Stars">
</p>

**ToolDelta** 是**为《我的世界：中国版》手机端租赁服**制作的、基于机器人的插件加载器。

ToolDelta 可以运行在**多种游戏交互启动器核心**上， 包括但不限于：
   - ~~FastBuilder~~
   - NeOmega接入点
   - NeOmega启动器
   - Eulogist赞颂者
   - FateArk接入点  （目前公开可用）
   - LanGame本地联机接入点 （目前公开可用）

ToolDelta 的插件可以极大幅提高您的租赁服的玩法上限和优化租赁服的流畅度。


## 目录
- [目录](#目录)
- [相关网站和交流群](#相关网站和交流群)
- [插件市场](#插件市场)
- [注意事项](#注意事项)
- [运行和配置](#运行和配置)



## 插件市场
- ToolDelta 的插件市场在 [这里](https://github.com/ToolDelta-Basic/PluginMarket)



## 注意事项
- 源码运行时，ToolDelta 仅能运行在 Python 3.10+ 版本上


## 相关网站和交流群
- [ToolDelta 官站](https://tooldelta.top)
- [ToolDelta 百科及用户指南](https://wiki.tooldelta.top)
- [ToolDelta 官方技术交流群](https://qm.qq.com/q/3JtUTHzZwY) 准入等级为 QQ 16 级（一个太阳）
- [ToolDelta 第三方社区交流群](https://qm.qq.com/q/6J79yelYNq) 无准入门槛




## 运行和配置
- 直接下载 ToolDelta 可执行文件并运行
   - [发行版 ToolDelta 下载点这里](https://github.com/ToolDelta/ToolDelta/releases)
- 在 `pip` 安装 ToolDelta 并运行
   ```sh
   pip install tooldelta
   echo import tooldelta;tooldelta.client_title() > main.py
   ```
- 运行:
   ```sh
   python3 main.py
   ```
   或
   ```
   python main.py
   ```

## 打包 Docker 镜像
在项目目录下运行命令：
```sh
docker build -t tooldelta .
```

## 使用已打包的 Docker 镜像
运行命令：
```sh
sudo docker pull crpi-6pmrt6su7uwffyo4.cn-shanghai.personal.cr.aliyuncs.com/tooldelta/tooldelta:latest
```
如果您需要将 ToolDelta 运行在 MCSM 中，在 **应用实例设置>容器化** 中选择镜像名 **tooldelta:latest** 即可。