import requests, getpass, hashlib, json
from tooldelta import constants
from tooldelta.color_print import Print

def login_liliya():
    while 1:
        hash_obj: hashlib._Hash = hashlib.sha256()
        username: str = input(Print.fmt_info("请输入账号:", "§6 账号 "))
        hash_obj.update(
            getpass.getpass(Print.fmt_info("请输入密码(已隐藏):", "§6 密码 ")).encode()
        )
        __password: str = hash_obj.hexdigest()
        Authorization: str = requests.get(url=constants.GUGU_APIS[1], timeout=5).text
        repo: requests.Response = requests.post(
            url=constants.GUGU_APIS[0],
            data=json.dumps(
                {
                    "client_public_key": "",
                    "server_code": "::DRY::",
                    "server_passcode": "::DRY::",
                    "username": username,
                    "password": __password,
                },
                ensure_ascii=False,
            ),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {Authorization}",
            }, timeout=5
        )
        repo_text: dict = json.loads(repo.text)
        repo_message: str = repo_text["message"]
        repo_success: bool = repo_text["success"]
        if repo.status_code != 200:
            Print.print_war(
                f"请求Api接口失败，将自动使用Token登陆!状态码:{repo.status_code}，返回值:{repo.text}"
            )
            return
        if not repo_success:
            if "无效的用户中心用户名或密码" in repo_message:
                Print.print_war("登录失败, 无效的用户名、密码或MFA代码!")
            else:
                Print.print_war("登录失败, 原因: " + repo_message + ", 请重试!")
        else:
            break
    token = repo_text["token"]
    with open("fbtoken", "w", encoding="utf-8") as f:
        f.write(token)

def login_fbuc():
    while 1:
        hash_obj: hashlib._Hash = hashlib.sha256()
        username: str = input(Print.fmt_info("请输入账号:", "§6 账号 "))
        hash_obj.update(
            getpass.getpass(
                Print.fmt_info("请输入密码(已隐藏):", "§6 密码 ")
            ).encode()
        )
        __password: str = hash_obj.hexdigest()
        __mfa_code: str = getpass.getpass(
            Print.fmt_info(
                "请输入双重验证码(已隐藏)(如未设置请直接回车):", "§6 MFA  "
            )
        )
        Authorization: str = requests.get(url=constants.FB_APIS[1], timeout=5).text
        repo: requests.Response = requests.post(
            url=constants.FB_APIS[3],
            data=json.dumps(
                {
                    "username": username,
                    "password": __password,
                    "mfa_code": __mfa_code,
                },
                ensure_ascii=False,
            ),
            headers={
                "Content-Type": "application/json",
                "authorization": f"Bearer {Authorization}",
            },
        )
        repo_text: dict = json.loads(repo.text)
        repo_message: str = repo_text["message"]
        repo_success: bool = repo_text["success"]
        if repo.status_code != 200:
            Print.print_war(
                f"请求Api接口失败，将自动使用Token登陆! 状态码:{repo.status_code}，返回值:{repo.text}"
            )
            return
        if not repo_success:
            if "Invalid username, password, or MFA code." in repo_message:
                Print.print_war("登陆失败; 无效的用户名、密码或MFA代码!")
            else:
                Print.print_war("登录失败, 原因: " + repo_message + ", 请重试!")
        else:
            break
    with_perfix: dict = json.loads(
        requests.get(
            url=constants.FB_APIS[2],
            data=json.dumps({"with_prefix": constants.FB_APIS[4]}),
            timeout=5,
            headers={
                "Content-Type": "application/json",
                "authorization": f"Bearer {Authorization}",
            },
        ).text
    )
    fetch_announcements: dict = json.loads(
        requests.get(
            url=constants.FB_APIS[4] + with_perfix["fetch_announcements"],
            timeout=5,
            headers={
                "Content-Type": "application/json",
                "authorization": f"Bearer {Authorization}",
            },
        ).text
    )
    fetch_profile: dict = json.loads(
        requests.get(
            url=constants.FB_APIS[4] + with_perfix["fetch_profile"],
            timeout=5,
            headers={
                "Content-Type": "application/json",
                "authorization": f"Bearer {Authorization}",
            },
        ).text
    )
    get_helper_status: dict = json.loads(
        requests.get(
            url=constants.FB_APIS[4] + with_perfix["get_helper_status"],
            timeout=5,
            headers={
                "Content-Type": "application/json",
                "authorization": f"Bearer {Authorization}",
            },
        ).text
    )
    UserInfo: dict = {
        "isadmin": repo_text["isadmin"],
        "blc": fetch_profile["blc"],
            "cn_username": fetch_profile["cn_username"],
            "phoenix_otp": fetch_profile["phoenix_otp"],
            "points": fetch_profile["points"],
            "slots": fetch_profile["slots"],
            "get_helper_status": get_helper_status,
        }
    token = requests.get(
        url=constants.FB_APIS[4] + with_perfix["get_phoenix_token"],
        data=json.dumps({"secret": f"{Authorization}"}),
        timeout=5,
        headers={
            "Content-Type": "application/json",
            "authorization": f"Bearer {Authorization}",
        },
    ).text
    with open("fbtoken", "w", encoding="utf-8") as f:
        f.write(token)