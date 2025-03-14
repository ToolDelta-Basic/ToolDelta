#!/bin/bash
# 设置安装目录
install_dir="$PWD/tooldelta"
# 设置应用程序名称
app_name="ToolDelta"
# 设置快捷指令
shortcut_command="td"


function EXIT_FAILURE(){
    exit -1
}

function download_exec_for_termux(){
echo "开始更新系统环境，遇到停顿请回车"
sleep 5
# 安装 PIL 的前置库
echo "正在安装图片处理依赖库(用于地图画导入)..."
curl http://222.187.254.86:5244/d/QQd/bot/ToolDelta/ToolDelta/d/libexpat.deb -o libexpat.deb
curl http://222.187.254.86:5244/d/QQd/bot/ToolDelta/ToolDelta/d/libffi.deb -o libffi.deb
curl http://222.187.254.86:5244/d/QQd/bot/ToolDelta/ToolDelta/d/openssl.deb -o openssl.deb
curl http://222.187.254.86:5244/d/QQd/bot/ToolDelta/ToolDelta/d/zlib.deb -o zlib.deb
curl http://222.187.254.86:5244/d/QQd/bot/ToolDelta/ToolDelta/d/libjpeg-turbo.deb -o libjpeg-turbo.deb
curl http://222.187.254.86:5244/d/QQd/bot/ToolDelta/ToolDelta/d/ToolDelta -o "/data/data/com.termux/files/usr/bin/td"
apt install ./openssl.deb ./libffi.deb ./libexpat.deb ./zlib.deb ./libjpeg-turbo.deb
chmod +x "/data/data/com.termux/files/usr/bin/$shortcut_command"
echo "安装完成啦，您现在可以在命令行中输入 '$shortcut_command' 来启动 $app_name。"

}

function download_exec(){
# 权限
mkdir -p "$install_dir"
chown -R +x "$install_dir"

# 切换到安装目录
pushd "$install_dir" || exit
# 获取ToolDelta的最新版本
LatestTag=$(wget -qO- -t1 -T2 "https://github.tooldelta.top/https://api.github.com/repos/ToolDelta-Basic/ToolDelta/releases/latest" | jq -r '.tag_name')
# 设置 GitHub release URL
github_release_url="https://github.tooldelta.top/https://github.com/ToolDelta-Basic/ToolDelta/releases/download/${LatestTag}/ToolDelta-linux"
# 下载
if curl -o "$app_name" -L "$github_release_url"; then
    echo "下载完成。"
else
    echo "下载失败。请检查网络连接或稍后再试。"
    exit 1
fi

# 权限
chmod 777 "$app_name"
case ${PLANTFORM} in
    "Linux_x86_64")
    executable="/usr/local/bin/$shortcut_command"
    ;;
    "Andorid_armv8")
    executable="/data/data/com.termux/files/usr/bin/$shortcut_command"
    ;;
    *)
    echo "不支持的平台${PLANTFORM}"
    EXIT_FAILURE
    ;;
esac

if ln -s "$install_dir/start.sh" $executable; then
    echo "快捷指令 '$shortcut_command' 创建成功。"
else
    echo "创建快捷指令 '$shortcut_command' 失败。请检查权限或手动创建快捷指令。"
fi
# 生成start.sh脚本
echo "pushd $install_dir && ./$app_name && popd " >  "$install_dir/start.sh"
chmod 777 "$install_dir/start.sh"
echo "安装完成啦，您现在可以在命令行中输入 '$shortcut_command' 来启动 $app_name。"
}

if [[ $(uname -o) == "GNU/Linux" ]] || [[ $(uname -o) == "GNU/Linux" ]]; then
    PLANTFORM="Linux_x86_64"
    if [[ $(uname -m) != "x86_64" ]]; then
        echo "不支持非64位的Linux系统"
        EXIT_FAILURE
    fi
    download_exec
elif [[ $(uname -o) == "Android" ]]; then
    PLANTFORM="Andorid_armv8"
    if [[ $(uname -m) == "armv7" ]]; then
        echo "不支持armv7的Andorid系统"
        EXIT_FAILURE
    fi
    echo "检测文件权限中..."
    if [ ! -x "/sdcard/Download" ]; then
        echo "请给予 termux 文件权限 ~"
        sleep 2
        termux-setup-storage
        EXIT_FAILURE
    fi
    if [ -x "/sdcard/Download" ]; then
        echo -e ""
        # working_dir="/sdcard/Download"
        # executable="/sdcard/Download/fastbuilder"
    else
        red_line "拜托你很逊欸，没权限"
        EXIT_FAILURE
    fi
    # dialog --menu "请选择安装方法" 15 40 4 1 "脚本安装(推荐)" 2 "覆盖安装(当方法1无法使用时使用)" 2> 1
      # case "$(cat 1)" in
        # 1)
        # download_exec_for_termux
        # ;;
        # 2)
        # Download_termux
        # ;;
        # *)
        # EXIT_FAILURE
    # esac
    download_exec_for_termux

else
    echo "不支持该系统，你的系统是"
    uname -a
fi