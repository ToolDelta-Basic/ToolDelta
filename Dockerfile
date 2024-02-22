# 基于Python-3.12.1版本的基础镜像
FROM python:3.12.1-slim

# 将ToolDelta源码添加到ToolDelta文件夹
ADD . /ToolDelta

# 设置ToolDelta文件夹为工作目录
RUN mkdir /root/.TDC
WORKDIR /root/.TDC

# 安装可能缺少的支持库
RUN pip install colorama

CMD [ "python","/ToolDelta/main.py"]