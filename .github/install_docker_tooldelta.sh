#!/bin/bash
# 此安装脚本适用于Linux(Debian已测试),Termux(未测试)

# 设置变量
WorkDir="$PWD/ToolDelta-Docker"
DataPath="/root/.ToolDelta-Docker"
DockerName="ToolDelta-Docker"

# 切换到工作目录
mkdir $WorkDir
mkdir $DataPath
cd $WorkDir

# 判断是Termux还是普通Linux
if [ $(uname -o) = "aarch64 Android" ]; then
    Type="Termux"
elif [ $(uname -o) = "GNU/Linux" ]; then
    Type="Linux"
else
    echo "暂不支持您的操作系统类型!"
    exit
fi
echo "检测到的操作系统类型:$Type"

# 安装jq包
if [ $Type = "Termux" ]; then
    pkg install jq
elif [ $Type = "Linux" ]; then
    apt-get install jq
else
    exit
fi

# 获取ToolDelta的最新版本
LatestTag=$(wget -qO- -t1 -T2 "https://api.github.com/repos/ToolDelta/ToolDelta/releases/latest" | jq -r '.tag_name')

# 检查Docker是否安装
echo "正在检查系统内是否安装Docker..."
docker -v
if [ $? -ne  0 ]; then
	echo "检测到Docker未安装!"
	echo "***** 开始安装 Docker 工具 *****"
    if [ $Type = "Termux" ]; then
        pkg install runc
        pkg install root-repo
        pkg install docker   
    elif [ $Type = "Linux" ]; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
    else
        exit
    fi
	echo "***** 安装 Docker 工具完成 *****"
else
	echo "Docker 已安装!"
fi

# 下载ToolDelta文件
wget https://mirror.ghproxy.com/https://github.com/ToolDelta/ToolDelta/archive/refs/tags/${LatestTag}.tar.gz -O ${LatestTag}.tar.gz
tar  zxvf  ${LatestTag}.tar.gz  -C $WorkDir
mv $WorkDir/ToolDelta-${LatestTag}/* $WorkDir  
rm -f ${LatestTag}.tar.gz

# 构建Docker镜像
docker build -t tooldelta-docker:${LatestTag} -f $WorkDir/Dockerfile .
echo "Docker镜像编译完成!"

# 创建容器
echo "***** 安装 ToolDelta-Docker 版 *****"
read -p "请输入数据存放目录(默认$DataPath):" TmpDataPath
if [ ! "$TmpDataPath" = "" ]; then
    DataPath=$TmpDataPath
fi
read -p "请设置容器名称(默认$DockerName):" TmpDockerName
if [ ! "$TmpDockerName" = "" ]; then
    DockerName=$TmpDockerName
fi

# 成功提示
echo "***** 安装成功! *****"
echo "Docker版ToolDelta安装成功!"
echo "***** ToolDelta-Docker *****"
echo "ToolDelta数据存放位置:$DataPath"
echo "运行容器并连接命令:docker start $(docker create -it --name $DockerName -v $DataPath:/root/.TDC --network=host tooldelta-docker:$LatestTag)"
