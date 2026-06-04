import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_socket.bind(('0.0.0.0', 8080))

print('Listening to port 8080 on UDP...')

(client_message, client_address) = server_socket.recvfrom(1024)

print('The client said: ', client_message.decode())

server_socket.sendto('I am a server'.encode(), client_address)

server_socket.close()
