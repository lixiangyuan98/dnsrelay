import socket

client = socket.socket(type=socket.SOCK_DGRAM)
client.sendto(bytes('test', encoding='utf8'), ('127.0.0.1', 8080))
data, addr = client.recvfrom(100)
print(data, addr)
