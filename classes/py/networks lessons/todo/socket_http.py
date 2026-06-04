import socket

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8080))
server_socket.listen()
print('Listens to port 8080')

(client_socket, client_address) = server_socket.accept()
print('connected to address: '+str(client_address))

body = 'Ahoy world!'
head = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: ' + str(len(body)) + '\r\n\r\n'
data = head + body

client_socket.send(data.encode())

client_socket.close()
server_socket.close()