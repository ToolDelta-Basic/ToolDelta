import os
import json


def generate_json(directory):
    data = {}

    # 确保目标目录存在
    target_directory = os.path.join(directory, "plugin_market")
    if not os.path.exists(target_directory) or not os.path.isdir(target_directory):
        print("目录 plugin_market 不存在或不是一个目录")
        return data

    # 获取目录下所有文件
    for root, dirs, files in os.walk(target_directory):
        relative_path = os.path.relpath(root, target_directory)
        if relative_path == ".":
            relative_path = ""
        data[relative_path] = []

        # 添加文件
        for file in files:
            data[relative_path].append(file)

    return data


if __name__ == "__main__":
    directory = "."  # 你的仓库目录
    json_data = generate_json(directory)

    # 将生成的 JSON 数据写入文件
    with open("plugin_market/directory.json", "w") as json_file:
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)
