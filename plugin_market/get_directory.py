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
    for root, _, files in os.walk(target_directory):
        relative_path = os.path.relpath(root, target_directory)
        if relative_path == ".":
            relative_path = ""
        data[relative_path] = []

        # 添加文件
        for file in files:
            data[relative_path].append(file)

    return data

def get_latest_versions():
    v_dict = {"dotcs_plugin": {}, "classic_plugin": {}, "injected_plugin": {}}
    with open(os.path.join(directory, "plugin_market", "market_tree.json"), "r", encoding="utf-8") as f:
        for k, v in json.load(f)["MarketPlugins"].items():
            v_dict[v["plugin-type"] + "_plugin"][k] = v["version"]
    return json.dumps(v_dict, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    directory = "."  # 你的仓库目录
    json_data = generate_json(directory)

    # 将生成的 JSON 数据写入文件
    with open("plugin_market/directory.json", "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)

    with open("plugin_market/latest_versions.json", "w", encoding="utf-8") as f:
        f.write(get_latest_versions())