<h1 align="center">ToolDelta - Multi Platform Edition</h1>
<p align="center">
  <a href="https://github.com/ToolDelta/ToolDelta/releases"><img src="https://img.shields.io/github/v/release/ToolDelta/ToolDelta?display_name=tag&sort=semver" alt="Releases"></a>
  <img src="https://img.shields.io/github/stars/ToolDelta/ToolDelta.svg?style=falt" alt="Stars">
</p>

<p align="center">
  <a href="https://github.com/ToolDelta/ToolDelta/issues"><img src="https://img.shields.io/github/issues/ToolDelta/ToolDelta.svg?style=flat" alt="opissues"></a>
  <a href="https://github.com/ToolDelta/ToolDelta/issues?q=is%3Aissue+is%3Aclosed"><img src="https://img.shields.io/github/issues-closed/SuperScript-PRC/ToolDelta.svg?style=flat&color=success" alt="clissues"></a>
  <a href="https://github.com/ToolDelta/ToolDelta/pulls"><img src="https://img.shields.io/github/issues-pr/ToolDelta/ToolDelta.svg?style=falt" alt="oppr"></a>
  <a href="https://github.com/ToolDelta/ToolDelta/pulls?q=is%3Apr+is%3Aclosed"><img src="https://img.shields.io/github/issues-pr-closed/ToolDelta/ToolDelta.svg?style=flat&color=success" alt="clpr"></a>
</p>

<p align="center">
  <code>ToolDelta</code> 是依赖于 <code>PhoenixBuilder | NeOmega</code> 的多功能扩展组件，可以加载各种各样有趣的插件。  
  <code>ToolDelta</code> 可以使得你的 <b>中国版《我的世界》手机版租赁服</b> 的玩法和功能更加多样化。  
  ToolDelta Wiki/用户指南: <a href="Wiki: https://tooldelta-wiki.tblstudio.cn/">ToolDelta Wiki</a>  
  ToolDelta 交流群: 194838530  
</p>

# 目录

- [目录](#目录)
- [注意事项](#注意事项)
- [在docker运行](#在docker运行)

# 注意事项

- 遇到平台不兼容的情况请尽快提交 `Issue`
- 已支持 `Termux`

How to use?：[learn-use](https://tooldelta-wiki.tblstudio.cn/learn-use.html)

Docker Image: [DockerHub](https://hub.docker.com/r/wlingzhenyu/tooldelta)

## 如何运行
 - 直接下载 ToolDelta 可执行文件并运行
    - <a href="https://github.com/ToolDelta/ToolDelta/releases">发行版 ToolDelta 下载点这里</a>

 - 在 `pip` 安装 ToolDelta 并运行
    - `pip install tooldelta`
    - `echo "import tooldelta;tooldelta.client_title()"`

 - 在docker运行
    ```bash
    docker run -v .:/app -t -i wlingzhenyu/tooldelta:latest
    ```
