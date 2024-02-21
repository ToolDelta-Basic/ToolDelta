# 基于Python-3.12.1版本的基础镜像
FROM python:3.12.1

# 将ToolDelta源码添加到ToolDelta文件夹
ADD . /ToolDelta

# 设置ToolDelta文件夹为工作目录
WORKDIR /ToolDelta

# 安装可能缺少的支持库
RUN pip install colorama

# 设置挂在目录 未使用(未测试)
# VOLUME [ "/root/ToolDelta","/ToolDelta"]

CMD [ "python","/ToolDelta/main.py"]


