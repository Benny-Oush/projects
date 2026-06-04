import socket

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

my_socket.sendto('Hello'.encode(), ('127.0.0.1', 8080))

(data, remote_address) = my_socket.recvfrom(1024)

print('Message:', data.decode())

my_socket.close()