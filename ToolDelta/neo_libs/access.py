import argparse
from neo_conn import ThreadOmega, ConnectType, AccountOptions

argparser = argparse.ArgumentParser("Omega Access Point")
argparser.add_argument("--token", type = str, help = "the user token")
argparser.add_argument("--server_code", type = str, help = "the server code")
argparser.add_argument("--server_pwd", type = str, help = "the server password")
argparser.add_argument("--openat", type = str, help = "the server password", default = "tcp://localhost:24016")
args = argparser.parse_args()


if __name__ == '__main__':
    try:
        # 远程连接挂载
        omega=ThreadOmega(
            connect_type=ConnectType.Local,
            address=args.openat,
            accountOption=AccountOptions(
                ServerCode=args.server_code,
                ServerPassword=args.server_pwd,
                UserToken=args.token
            )
        )
        omega.wait_disconnect()
    except KeyboardInterrupt:
        print("用户按键退出..")
        pass
    finally:
        print("SIGNAL: exit")