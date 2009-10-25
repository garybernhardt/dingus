def read_socket(socket):
    data = socket.recv(1024)
    socket.close()
    return data

