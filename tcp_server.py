import socket 
import threading

IP = '0.0.0.0'
PORT = 9998

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # we set the ip address and port we want the server to listen on    
    server.bind((IP, PORT))

    # we tell the server to start listening with a maximum of five connections 
    server.listen(5)
    print (f'[*] Listening on {IP}:{PORT}')
    
    # this is the server main loop, it waits for incomming connections
    while True: 
        # we receive the client socket (endpoint) in the client variable
        # and the remote connection details in the address variable 
        client, address = server.accept()
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        client_handler = threading.Thread(target=handle_client, args=(client,))
        # we start a thread to handle the client connection
        # at this point the main server loop is ready to handle another incoming connection
        client_handler.start()

# this function performs the recv() and it sends some data back    
def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'ACK')

if __name__ == '__main__':
    main()