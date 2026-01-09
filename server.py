import socket
import threading
import time


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 8080))
server.listen(5)

HTTP_VERSION = "HTTP/1.1"
BAD_STATUS = 400
BAD_STATUS_REASON = "Bad Request"
BAD_RESPONSE_BODY = "Bad Request"
OK_STATUS = 200
OK_STATUS_REASON = "OK"
NOT_FOUND_STATUS = 404
NOT_FOUND_REASON = "Not Found"


def client_connection(conn):
    data = ""
    while "\r\n\r\n" not in data:
        request = conn.recv(1024).decode()
        if request:
            data += request
        else:
            response = f"{HTTP_VERSION} {BAD_STATUS} {BAD_STATUS_REASON}\r\nContent-Type: text/plain\r\nContent-Length: {len(BAD_RESPONSE_BODY)}\r\n\r\n{BAD_RESPONSE_BODY}"
            conn.sendall(response.encode())
            conn.close()
            break
    lines = data.split("\r\n")
    request_line = lines[0].split(" ")
    if len(request_line) != 3:
        response = f"{HTTP_VERSION} {BAD_STATUS} {BAD_STATUS_REASON}\r\nContent-Type: text/plain\r\nContent-Length: {len(BAD_RESPONSE_BODY)}\r\n\r\n{BAD_RESPONSE_BODY}"
        conn.sendall(response.encode())
        conn.close()
        return
    request_type = request_line[0]
    request_path = request_line[1]
    http_version = request_line[2]
    if (
        request_type not in ["GET", "POST"]
        or http_version != HTTP_VERSION
        or request_path not in ["/", "/hello", "/time", "/echo", "/uppercase"]
    ):
        response = f"{HTTP_VERSION} {BAD_STATUS} {BAD_STATUS_REASON}\r\nContent-Type: text/plain\r\nContent-Length: {len(BAD_RESPONSE_BODY)}\r\n\r\n{BAD_RESPONSE_BODY}"
        conn.sendall(response.encode())
        conn.close()
        return
    headers = lines[1:]
    HEADERS = {}
    for header in headers:
        if ": " in header:
            temp = header.split(": ")
            HEADERS[temp[0]] = temp[1]
    if "Host" not in HEADERS:
        response = f"{HTTP_VERSION} {BAD_STATUS} {BAD_STATUS_REASON}\r\nContent-Type: text/plain\r\nContent-Length: {len(BAD_RESPONSE_BODY)}\r\n\r\n{BAD_RESPONSE_BODY}"
        conn.sendall(response.encode())
        conn.close()
        return

    if request_type == "GET":
        if request_path in ["/", "/hello", "/time"]:
            if request_path == "/":
                request_body = "Welcome to my HTTP Server!"
                response = f"{HTTP_VERSION} {OK_STATUS} {OK_STATUS_REASON}\r\nContent-Type: text/plain\r\nContent-Length: {len(request_body)}\r\n\r\n{request_body}"
            elif request_path == "/hello":
                request_body = "Hello World"
                response = f"{HTTP_VERSION} {OK_STATUS} {OK_STATUS_REASON}\r\nContent-Type: text/plain\r\nContent-Length: {len(request_body)}\r\n\r\n{request_body}"
            elif request_path == "/time":
                request_body = time.ctime()
                response = f"{HTTP_VERSION} {OK_STATUS} {OK_STATUS_REASON}\r\nContent-Type: text/plain\r\nContent-Length: {len(request_body)}\r\n\r\n{request_body}"
            conn.sendall(response.encode())
            conn.close()
            return
        request_body = "Not Found"
        response = f"{HTTP_VERSION} {NOT_FOUND_STATUS} {NOT_FOUND_REASON}\r\nContent-Type: text/plain\r\nContent-Length: {len(request_body)}\r\n\r\n{request_body}"
        conn.sendall(response.encode())
        conn.close()
        return

    elif request_type == "POST":
        if request_path in ["/echo", "/uppercase"]:
            if "Content-Length" not in HEADERS:
                response = f"{HTTP_VERSION} {BAD_STATUS} {BAD_STATUS_REASON}\r\nContent-Type: text/plain\r\nContent-Length: {len(BAD_RESPONSE_BODY)}\r\n\r\n{BAD_RESPONSE_BODY}"
                conn.sendall(response.encode())
                conn.close()
                return
            start_index = data.index("\r\n\r\n") + 4
            temp = len(data) - start_index
            remaining = int(HEADERS["Content-Length"]) - temp
            while remaining > 0:
                request = conn.recv(min(1024, remaining))
                if request:
                    decoded_request = request.decode()
                    data += decoded_request
                    remaining -= len(request)
                else:
                    response = f"{HTTP_VERSION} {BAD_STATUS} {BAD_STATUS_REASON}\r\nContent-Type: text/plain\r\nContent-Length: {len(BAD_RESPONSE_BODY)}\r\n\r\n{BAD_RESPONSE_BODY}"
                    conn.sendall(response.encode())
                    conn.close()
                    return
            request_body = data[start_index:]
            if request_path == "/echo":
                response = f"{HTTP_VERSION} {OK_STATUS} {OK_STATUS_REASON}\r\nContent-Type: text/plain\r\nContent-Length: {len(request_body)}\r\n\r\n{request_body}"
            elif request_path == "/uppercase":
                response = f"{HTTP_VERSION} {OK_STATUS} {OK_STATUS_REASON}\r\nContent-Type: text/plain\r\nContent-Length: {len(request_body)}\r\n\r\n{request_body.upper()}"
            conn.sendall(response.encode())
            conn.close()
            return
        response = f"{HTTP_VERSION} {BAD_STATUS} {BAD_STATUS_REASON}\r\nContent-Type: text/plain\r\nContent-Length: {len(BAD_RESPONSE_BODY)}\r\n\r\n{BAD_RESPONSE_BODY}"
        conn.sendall(response.encode())
        conn.close()
        return


def accept_connections():
    while True:
        conn, _ = server.accept()
        t = threading.Thread(target=client_connection, args=(conn,), daemon=True)
        t.start()


t1 = threading.Thread(target=accept_connections, daemon=True)
t1.start()

while True:
    time.sleep(1)
