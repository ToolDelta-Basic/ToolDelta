from git import Repo
from datetime import datetime
import pytz
from packaging.version import parse


def clone_repo(repo_url, repo_path, branch="main"):
    Repo.clone_from(repo_url, to_path=repo_path, branch=branch)
    return Repo(repo_path)


def get_max_version_tag(repo):
    tags = [tag for tag in repo.tags if tag.name != "binaries"]
    return max(tags, key=lambda tag: parse(tag.name), default=None)


def get_local_time(utc_time, timezone="Asia/Shanghai"):
    local_tz = pytz.timezone(timezone)
    return utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)


def generate_changelog(repo, max_version, tag_creation_date, version_file="version"):
    tag_creation_datetime = datetime.strptime(tag_creation_date, "%Y-%m-%d %H:%M")
    new_commits_log = repo.git.log(
        '--pretty={"commit":"%H","author":"%aN","summary":"%s","date":"%cd"}',
        since=tag_creation_datetime,
        date="format:%Y-%m-%d %H:%M",
    )

    new_commits_list = new_commits_log.split("\n")
    new_real_commits_list = [eval(item) for item in new_commits_list if item]

    ToolDeltaVersion = open(version_file).read().strip()

    with open("changelog.md", "w") as CHANGELOG:
        CHANGELOG.write(
            f"## ToolDelta Release v{ToolDeltaVersion} ({tag_creation_date})\n\n"
        )
        for commit in new_real_commits_list:
            commit_id = commit["commit"]
            author = commit["author"]
            summary = commit["summary"]
            date = commit["date"]
            CHANGELOG.write(
                f"- [{commit_id[:7]}](https://github.com/ToolDelta/commit/{commit_id}): {summary} by {author} ({date})\n"
            )


def main():
    repo_path = "/home/runner/work/Test"
    repo_url = "https://github.com/ToolDelta/ToolDelta.git"

    repo = clone_repo(repo_url, repo_path)

    max_version = get_max_version_tag(repo)
    if max_version:
        utc_time = max_version.commit.committed_datetime
        local_time = get_local_time(utc_time)
        tag_creation_date = local_time.strftime("%Y-%m-%d %H:%M")
        print(f"最大版本号: {max_version.name}")
        print(f"Tag {max_version.name} 的创建日期是: {tag_creation_date}")

        generate_changelog(repo, max_version, tag_creation_date)
    else:
        print("No valid tags found.")
        exit()


if __name__ == "__main__":
    main()
