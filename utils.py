from datetime import datetime
from socket import socket, AF_INET, SOCK_DGRAM


def log_file(file_name: str, message: str):
    with open(file_name, "a") as file:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{date} | {message}\n")


def get_lan_ip_address():
    socket_server = socket(AF_INET, SOCK_DGRAM)
    try:
        # ip does not have to be reachable
        socket_server.connect(("10.255.255.255", 1))
        local_ip = socket_server.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        socket_server.close()
    return local_ip
