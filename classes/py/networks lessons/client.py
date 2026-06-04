import socket

my_socket = socket.socket()

my_socket.connect(('127.0.0.1', 8080))

while True:
    
    message = input('Enter a message: ')

    if message != '':
        my_socket.send(message.encode())
    else:
        my_socket.send(bytes([0]))


    if message == 'exit':
        print('Exiting connection')
        break

    data = my_socket.recv(1024).decode()

    print('Answer: '+ data)

my_socket.close()

