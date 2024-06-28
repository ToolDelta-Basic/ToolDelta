<h1 align="center">ToolDelta - Multi Platform Edition</h1>
<p align="center">
  <a href="https://github.com/ToolDelta/ToolDelta/releases"><img src="https://img.shields.io/github/v/release/ToolDelta/ToolDelta?display_name=tag&sort=semver" alt="Releases"></a>
  <img src="https://img.shields.io/github/stars/ToolDelta/ToolDelta.svg?style=falt" alt="Stars">
</p>

<p align="center">
  <a href="https://github.com/ToolDelta/ToolDelta/issues"><img src="https://img.shields.io/github/issues/ToolDelta/ToolDelta.svg?style=flat" alt="opissues"></a>
  <a href="https://github.com/ToolDelta/ToolDelta/issues?q=is%3Aissue+is%3Aclosed"><img src="https://img.shields.io/github/issues-closed/ToolDelta/ToolDelta.svg?style=flat&color=success" alt="clissues"></a>
  <a href="https://github.com/ToolDelta/ToolDelta/pulls"><img src="https://img.shields.io/github/issues-pr/ToolDelta/ToolDelta.svg?style=falt" alt="oppr"></a>
  <a href="https://github.com/ToolDelta/ToolDelta/pulls?q=is%3Apr+is%3Aclosed"><img src="https://img.shields.io/github/issues-pr-closed/ToolDelta/ToolDelta.svg?style=flat&color=success" alt="clpr"></a>
</p>

<p align="center">
  <b>ToolDelta</b> 是依赖于 <b>PhoenixBuilder | Neo Omega</b> 的多功能扩展组件，可以加载各种各样有趣的插件。  
  <br/><b>ToolDelta</b> 可以使得你的 <b>中国版《我的世界》基岩版租赁服</b> 的玩法和功能更加多样化。  
  <br/><a href="https://tooldelta-wiki.tblstudio.cn/">维基和用户指南</a> | <a href="http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=ywf-Y9Sb7G3McLAN7TveI-qh-g1FEtLB&authKey=C0ZLK09UWRzWv9dpReVnZljSnZ15crGpNpdT5O%2BX%2B%2BQvZ%2Bsm2BWfN8qqdJ5OMnTq&noverify=0&group_code=194838530">交流群</a>  
</p>

> WARNING: 禁止在 GitCode 上搬运此项目或者镜像该项目：六十四，八十九，六四，八九

## 目录
- [目录](#目录)
- [注意事项](#注意事项)
- [友情链接](#友情链接)
- [运行和配置](#运行和配置)



## 注意事项
- 遇到平台不兼容的情况请尽快提交 `Issue`
- 已支持 `Termux`



## 友情链接
- [如何使用](https://tooldelta-wiki.tblstudio.cn/learn_use.html)
- [Docker 镜像](https://hub.docker.com/r/wlingzhenyu/tooldelta)



## 运行和配置
 - 直接下载 ToolDelta 可执行文件并运行
    - <a href="https://github.com/ToolDelta/ToolDelta/releases">发行版 ToolDelta 下载点这里</a>
 - 在 `pip` 安装 ToolDelta 并运行
    - `pip install tooldelta`
    - `echo "import tooldelta;tooldelta.client_title()" > main.py`
 - 在docker运行
    ```bash
    docker run -v .:/app -t -i wlingzhenyu/tooldelta:latest
    ```
