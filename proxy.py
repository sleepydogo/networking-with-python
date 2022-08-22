import sys 
import socket 
import threading

# it contains ASCCI-printable characters, if it exits, or a dot if not.

# Some logic about the string:
# The charactesr have a representation which has a length itself. This length its equal to 3 if the character is printable, otherwise it adopts another value.
# So the hexfilter it uses this facts to print only the representable characters and replace the others with dots.

HEX_FILTER = ''.join([ (len( repr(chr(i)) ) == 3 ) and chr(i) or '.' for i in range(256)])

# this function displays the comunnication between the local and remote machines to the console. 
# it takes some bytes or a string as the input, taken from the console and prints a hexdump to the console. 
# this will be usefull to print both hexadecimal and ASCII-printable values from the incoming package, and this is useful for understanding unknown protocoles

def hexdump(src, length=16, show=True):
    # first we make sure we are dealing with a string by transforming the incoming package into a string if it was passed in bytes.
    if isinstance(src, bytes):
        src = src.decode()


    results = list()

    print('len src--> ', len(src))
    for i in range(0, len(src), length): 
        # we copy a piece of the string.
        print("i-->",i)
        
        word = str(src[i:i+length])
        print("word -->", word)

        # we use translate function to substitute the string representation of each character for the corresponding character in the raw string printable.
        printable = word.translate(HEX_FILTER)
        print("printable -->", printable)
        # 
        hexa= ''.join([f'{ord(c):02x}' for c in word])
        # we define hexwidth 
        hexwidth = length*3

        results.append(f'{i:04x} {hexa:<{hexwidth}}  {printable}')

    if show: 
        for line in results:
            print(line)
        else:
            return results


# this function will be used by both parts of the connection in the proxy
# we pass the socket object that will be used for the coneection
def receive_from(connection):
    # we declare a byte string
    buffer = b""
    # we set a timeout of 5 seconds which is a little agressive if you are proxying traffic to another countries
    connection.settimeout(5)
    try:
        while True:
            #we receive from the incoming connection all the data in 4096 bits. 
            data = connection.recv(4096)
            # if there is no data we break the sequence
            if not data:
                break
            # the variable buffer almacenates all the data
            buffer += data
    except Exception as e:
        pass
    return buffer

def request_handler(buffer):
    # we made a few modifications to the package hehe ;)
    return buffer

def response_handler(buffer):
    # we made a few modifications to the package hehe ;)
    return buffer
    
# this function contains the main logic of the proxy itself
# we receive as arguments the client socket, the ip from the remote host, the port that we are going to establish the connection with, and an boolean which declares if we have to receive data first
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # see lines 7 to 9 in tcp_client.py
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # we check to make sure we dont need to first initiate a connection to the remote side and request data before going into the main loop.
    # some server daemos will expect you to do this
    # if the boolean is true
    if receive_first: 
        # we receive the server data
        remote_buffer = receive_from(remote_socket)
        # we hexdump it 
        hexdump(remote_buffer)
    # we pass the buffer through the response handler function before sending it to the client
    remote_buffer = response_handler(remote_buffer)
    # if there is a buffer to send, we send it and print the info in the console screen.
    if len(remote_buffer): 
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)
    
    # we go into the main loop 
    while True: 
        # we receive the data from the client
        local_buffer = receive_from(client_socket)
        # if there is any incoming data
        if len(local_buffer):
            # we print in the console's screen that we've received the data 
            line = "[==>] Received %d bytes from localhost." %len(local_buffer)
            print(line)
            
            # we hexdump the data
            hexdump(local_buffer)
            # we do some magic over the package before sending it to the server, then send it and inform it
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to localhost. ")

        # then we receive the remote data from the server
        remote_buffer = receive_from(remote_socket)
        # if there is any data we inform it, hexdump it, pass it thorugh the response_hanlder and then send it to the client. 
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote. " %len(remote_buffer))
            hexdump(remote_buffer)
            
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<== Sent to local host]")

        # if there's no data we just close the connection and break out the loop.
        if not len(local_buffer) or not len(remote_buffer): 
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connection.")
            break

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    # we create a socket and then bind to the local host and listens
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: 
        server.bind((local_host, local_port))
    except Exception as e:
        print('problem on bind: %r' % e)
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port)) 
        print("[!!] Check for other listening sockets or correct permissions.") 
        sys.exit(0)
    
    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)

    # when a new connection mades a request we will accept it and pass it to the proxy_handler in a new thread.
    while True: 
        client_socket, addr = server.accept()
        line = "> Receiving incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main(): 
    if len(sys.argv[1:]) != 5: 
        print("Usage: ./proxy.py [localhost] [localport]",  end='') 
        print("[remotehost] [remoteport] [receive_first]") 
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True") 
        sys.exit(0) 

    local_host = sys.argv[1] 
    local_port = int(sys.argv[2]) 
 
    remote_host = sys.argv[3] 
    remote_port = int(sys.argv[4]) 
 
    receive_first = sys.argv[5] 
 
    if "True" in receive_first: 
        receive_first = True 
    else: 
        receive_first = False 
 
    server_loop(local_host, local_port, remote_host, remote_port, receive_first) 
 
 
if __name__ == '__main__': 
    main()