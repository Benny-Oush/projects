import socket

server_socket = socket.socket()

server_socket.bind(('0.0.0.0', 8080))

server_socket.listen()

print('Listening to port 8080')

(client_socket, client_address) = server_socket.accept()

print('Connected to address: ' + str(client_address))

while True:

    data = client_socket.recv(1024).decode()

    if data == 'exit':
        print('Server shutting down')
        break

    print('The client said: ' + data)

    client_socket.send(data.encode())

client_socket.close()
server_socket.close()