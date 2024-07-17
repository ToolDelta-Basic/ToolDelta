# pip install GitPython packaging pytz
from git import Repo
from datetime import datetime
import os
import pytz
from packaging.version import parse

# repo_path = os.path.join('/home/xingchen/WorkSpace/ToolDelta/.github', 'test')
repo_path = os.path.join('/root', 'test')
if not os.path.exists(repo_path):
    Repo.clone_from('https://tdload.tblstudio.cn/https://github.com/ToolDelta/ToolDelta.git', to_path=repo_path, branch='main')
repo = Repo(repo_path)
tags = [tag for tag in repo.tags if tag.name != 'binaries']
max_version = max(tags, key=lambda tag: parse(tag.name), default=None)
if max_version:
    utc_time = max_version.commit.committed_datetime
    local_tz = pytz.timezone('Asia/Shanghai')
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
    tag_creation_date = local_time.strftime('%Y-%m-%d %H:%M')
    print(f"最大版本号: {max_version.name}")
    print(f"Tag {max_version.name} 的创建日期是: {tag_creation_date}")
else:
    print("没有找到任何标签")

tag_creation_datetime = datetime.strptime(tag_creation_date, '%Y-%m-%d %H:%M')

new_commits_log = repo.git.log('--pretty={"commit":"%h","author":"%an","summary":"%s","date":"%cd"}', 
                               since=tag_creation_date, date='format:%Y-%m-%d %H:%M')
new_commits_list = new_commits_log.split("\n")
new_real_commits_list = [eval(item) for item in new_commits_list]
print(new_real_commits_list)
ToolDeltaVersion = open("version", "r").read()
print(ToolDeltaVersion)
CHANGELOG = open('CHANGELOG.md', 'w')
CHANGELOG.write(f"## {ToolDeltaVersion} ({tag_creation_date})\n")