#!/bin/bash
# 设置安装目录
install_dir="/opt/tooldelta"
rm -rf /usr/local/bin/td $install_dir
# 设置应用程序名称
app_name="ToolDelta"
# 设置快捷指令
shortcut_command="td"
# 设置 GitHub release URL
github_release_url="https://mirror.ghproxy.com/https://github.com/ToolDelta/ToolDelta/releases/download/0.3.8/ToolDelta-linux"

# 权限
mkdir -p "$install_dir"
chown -R $(whoami):$(whoami) "$install_dir"

# 切换到安装目录
pushd "$install_dir" || exit

# 下载
if curl -o "$app_name" -L "$github_release_url"; then
    echo "下载完成。"
else
    echo "下载失败。请检查网络连接或稍后再试。"
    exit 1
fi

# 权限
chmod +x "$app_name"
# 创建符号链接
if ln -s "$install_dir/start.sh" "/usr/local/bin/$shortcut_command"; then
    echo "快捷指令 '$shortcut_command' 创建成功。"
else
    echo "创建快捷指令 '$shortcut_command' 失败。请检查权限或手动创建快捷指令。"
fi

# 生成start.sh脚本
echo "pushd $install_dir && ./$app_name && popd " >  "$install_dir/start.sh"
chmod +x "$install_dir/start.sh"

echo "安装完成。您现在可以在命令行中输入 '$shortcut_command' 启动 $app_name。"
popd