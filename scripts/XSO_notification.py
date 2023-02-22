import socket
import json

ip = "127.0.0.1"
port = 42069

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

msg = {
    "messageType": 1,
    "index": 0,
    "title": "Example",
    "content": "Hi",
    "height": 120.0,
    "sourceApp": "TEST_App",
    "timeout": 6.0,
    "volume": 0.5,
    "audioPath": "default",
    "useBase64Icon": False,
    "icon": "default",
    "opacity": 1.0
}
msgdata = json.dumps(msg)
byte = msgdata.encode()

sock.sendto(byte, (ip, port))

sock.close()