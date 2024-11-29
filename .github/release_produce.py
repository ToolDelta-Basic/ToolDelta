import pytz
import json
import os
import shutil
from git import Repo
from datetime import datetime
from packaging.version import parse

def clone_repo(repo_url, repo_path, branch="main"):
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)
    Repo.clone_from(repo_url, to_path=repo_path, branch=branch)
    return Repo(repo_path)

def get_max_version_tag(repo):
    tags = [tag for tag in repo.tags if tag.name != "binaries"]
    sorted_tags = sorted(tags, key=lambda tag: parse(tag.name), reverse=True)
    return sorted_tags[0] if sorted_tags else None

def get_local_time(utc_time, timezone="Asia/Shanghai"):
    local_tz = pytz.timezone(timezone)
    return utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)

def generate_changelog(repo, max_version, version_file="version"):
    max_tag_creation_datetime = max_version.commit.committed_datetime

    new_commits_log = repo.git.log(
        '--pretty={"commit":"%H","author":"%cN","summary":"%s","date":"%cd"}',
        since=max_tag_creation_datetime,
        date="format:%Y-%m-%d %H:%M",
    )

    new_commits_list = new_commits_log.split("\n")
    new_real_commits_list = []
    for item in new_commits_list:
        if item:
            try:
                item = json.loads(item)
                item.update({"avali": True})
            except json.JSONDecodeError:
                item = {
                    "commit": "Error",
                    "author": "Error",
                    "summary": item,
                    "date": "Error",
                    "avali": False
                }


    ToolDeltaVersion = open(version_file).read().strip()

    with open("changelog.md", "w") as CHANGELOG:
        CHANGELOG.write(
            f"## ToolDelta Release v{ToolDeltaVersion} ({max_tag_creation_datetime.strftime('%Y-%m-%d %H:%M')})\n\n"
        )
        for commit in new_real_commits_list:
            commit_id = commit["commit"]
            author = commit["author"]
            summary = commit["summary"]
            date = commit["date"]
            if "github-actions" in summary or "GitHub" in summary:
                continue
            if commit["avali"]:
                CHANGELOG.write(
                    f"- [[`{commit_id[:7]}`](https://github.com/ToolDelta/ToolDelta/commit/{commit_id})] {summary} By {author} ({date})\n"
                )
            else:
                CHANGELOG.write(
                    f"- [`{commit_id[:7]}`] {summary}\n"
                )

def main():
    repo_path = "/home/runner/work/Test"
    repo_url = "https://github.com/ToolDelta/ToolDelta.git"

    # repo_path = "/home/xingchen/WorkSpace/ToolDelta/.github/test"
    # repo_url = "https://tdload.tblstudio.cn/https://github.com/ToolDelta/ToolDelta.git"
    
    repo = clone_repo(repo_url, repo_path)
    repo.git.pull()

    max_version = get_max_version_tag(repo)

    if max_version:
        utc_time = max_version.commit.committed_datetime
        local_time = get_local_time(utc_time)
        max_tag_creation_date = local_time.strftime("%Y-%m-%d %H:%M")

        print(f"最大版本号: {max_version.name}")
        print(f"Tag {max_version.name} 的创建日期是: {max_tag_creation_date}")

        generate_changelog(repo, max_version)
    else:
        print("No valid tags found.")
        exit()

if __name__ == "__main__":
    main()
