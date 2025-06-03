"验证服务器的各种登录方法"

import getpass
import hashlib
import requests
import json

from .utils import fmts
from .constants.tooldelta_cli import FBLIKE_APIS


def fblike_sign_login(url: str, api_urls_fmt: list[str] = FBLIKE_APIS) -> str:
    """登录各大验证服务器获取 Token

    Raises:
        requests.exceptions.RequestException: 登录失败
    """
    login_api, new_api, main_api = (i % url for i in api_urls_fmt)
    while 1:
        hash_obj = hashlib.sha256()
        username = input(fmts.fmt_info("请输入账号: ", "§6 账号 "))
        hash_obj.update(
            getpass.getpass(fmts.fmt_info("请输入密码 (已隐藏):", "§6 密码 ")).encode()
        )
        password = hash_obj.hexdigest()
        auth_key = requests.get(url=new_api, timeout=5).text
        resp = requests.post(
            url=login_api,
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
        SUCCESS_CODE = 200
        if resp.status_code != SUCCESS_CODE:
            fmts.print_war(
                f"请求 Api 接口失败, 将自动使用 Token 登录 (状态码:{resp.status_code}, 返回值: {resp.text})"
            )
            raise requests.exceptions.RequestException("请求 Api 接口失败", resp)
        resp = resp.json()
        resp_msg = resp["message"]
        auth_succ = resp["success"]
        if not auth_succ:
            fmts.print_war(f"登录失败: {resp_msg}")
            continue
        break
    return resp["token"]
