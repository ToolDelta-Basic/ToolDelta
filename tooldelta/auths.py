"认证模块"

import getpass
import hashlib
from typing import Any

import requests
import ujson as json

from tooldelta import constants

from .color_print import Print


def liliya_login() -> str:
    """登录咕咕账号

    Raises:
        requests.exceptions.RequestException: 登录失败
    """
    hash_obj = hashlib.sha256()
    username = input(Print.fmt_info("请输入账号：", "§6 账号 "))
    hash_obj.update(
        getpass.getpass(Print.fmt_info("请输入密码 (已隐藏):", "§6 密码 ")).encode()
    )
    password = hash_obj.hexdigest()
    auth_key = requests.get(url=constants.GUGU_APIS[1], timeout=5).text
    repo = requests.post(
        url=constants.GUGU_APIS[0],
        data=json.dumps(
            {
                "client_public_key": "",
                "server_code": "::DRY::",
                "server_passcode": "::DRY::",
                "username": username,
                "password": password,
            },
            ensure_ascii=False,
        ),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_key}",
        },
        timeout=5,
    )
    repo_text: dict[str, Any] = json.loads(repo.text)
    repo_message: str = repo_text["message"]
    repo_success: bool = repo_text["success"]
    if repo.status_code != 200:
        Print.print_war(
            f"请求 Api 接口失败，将自动使用 Token 登陆！状态码:{repo.status_code}，返回值:{repo.text}"
        )
        raise requests.exceptions.RequestException("请求 Api 接口失败", repo)
    if not repo_success:
        if "无效的用户中心用户名或密码" in repo_message:
            Print.print_war("登录失败，无效的用户名或密码！")
            raise requests.exceptions.RequestException("无效的用户名或密码")
        Print.print_war(f"登录失败，原因：{repo_message}")
        raise requests.exceptions.RequestException("登录无效", repo)
    token = repo_text["token"]
    return token


def fbuc_login() -> str:
    """登录 FastBuilder 账号

    Raises:
        requests.exceptions.RequestException: 登录失败
    """
    hash_obj = hashlib.sha256()
    username = input(Print.fmt_info("请输入账号：", "§6 账号 "))
    hash_obj.update(
        getpass.getpass(Print.fmt_info("请输入密码 (已隐藏):", "§6 密码 ")).encode()
    )
    password = hash_obj.hexdigest()
    mfa_code = getpass.getpass(
        Print.fmt_info("请输入双重验证码 (已隐藏)(如未设置请直接回车):", "§6 MFA  ")
    )
    auth_key = requests.get(url=constants.FB_APIS[1], timeout=5).text
    repo = requests.post(
        url=constants.FB_APIS[3],
        data=json.dumps(
            {
                "username": username,
                "password": password,
                "mfa_code": mfa_code,
            },
            ensure_ascii=False,
        ),
        headers={
            "Content-Type": "application/json",
            "authorization": f"Bearer {auth_key}",
        },
        timeout=5,
    )
    repo_text: dict[str, Any] = json.loads(repo.text)
    repo_message: str = repo_text["message"]
    repo_success: bool = repo_text["success"]
    if repo.status_code != 200:
        Print.print_war(
            f"请求 Api 接口失败，将自动使用 Token 登陆！状态码:{repo.status_code}，返回值:{repo.text}"
        )
        raise requests.exceptions.RequestException("请求 Api 接口失败", repo)

    if not repo_success:
        if "Invalid username, password, or MFA code." in repo_message:
            raise requests.exceptions.RequestException("无效的用户名、密码或 MFA 代码")
        raise requests.exceptions.RequestException("登录无效", repo)
    # 获取 token 前缀
    repo = requests.get(
        url=constants.FB_APIS[2],
        data=json.dumps({"with_prefix": constants.FB_APIS[4]}),
        timeout=5,
        headers={
            "Content-Type": "application/json",
            "authorization": f"Bearer {auth_key}",
        },
    )
    if repo.status_code != 200:
        Print.print_war(
            f"无法获取 tokenx 信息！状态码:{repo.status_code}，返回值:{repo.text}"
        )
        raise requests.exceptions.RequestException("请求 Api 接口失败", repo)
    with_perfix: dict[str, Any] = json.loads(repo.text)
    token_request = requests.get(
        url=constants.FB_APIS[4] + with_perfix["get_phoenix_token"],
        data=json.dumps({"secret": f"{auth_key}"}),
        timeout=5,
        headers={
            "Content-Type": "application/json",
            "authorization": f"Bearer {auth_key}",
        },
    )
    if token_request.status_code != 200:
        Print.print_war(
            f"无法获取 tokenx 信息！状态码:{token_request.status_code}，返回值:{token_request.text}"
        )
        raise requests.exceptions.RequestException("请求 Api 接口失败", token_request)
    return token_request.text
