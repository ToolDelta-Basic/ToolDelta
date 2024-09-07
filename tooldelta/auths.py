"认证模块"

import getpass
import hashlib
from typing import Any

import requests
import ujson as json

from .color_print import Print


def sign_login(API_urls: list[str]) -> str:
    """登录各大验证服务器获取 Token

    Raises:
        requests.exceptions.RequestException: 登录失败
    """
    hash_obj = hashlib.sha256()
    username = input(Print.fmt_info("请输入账号：", "§6 账号 "))
    hash_obj.update(
        getpass.getpass(Print.fmt_info("请输入密码 (已隐藏):", "§6 密码 ")).encode()
    )
    password = hash_obj.hexdigest()
    auth_key = requests.get(url=API_urls[1], timeout=5).text
    repo = requests.post(
        url=API_urls[0],
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
    SUCCESS_CODE = 200
    if repo.status_code != SUCCESS_CODE:
        Print.print_war(
            f"请求 Api 接口失败，将自动使用 Token 登录！状态码:{repo.status_code}，返回值:{repo.text}"
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
