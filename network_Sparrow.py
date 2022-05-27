# we've imported all the libraries we need
import argparse 
import socket 
import shlex
import sys 
import subprocess
import textwrap
import threading

# then define de execute function, wich receives a commands and returns an output
def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    # here we use the subprocess library which provides an interface for process-creation, with check_output
    # we execute a command on the local operating system and returns the output.
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()

class Network_Sparrow:
    def __init__(self, args, buffer=None):
        # we initialize the Network_Sparrow object with the arguments and the buffer
        self.args = args
        self.buffer = buffer
        #  we create the socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # this is the entry point for managing the netcat object if we are setting up a listener we call listen() otherwise we call send()
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        # First we connect to the target and port
        self.socket.connect((self.args.target, self.args.port))
        # if we have a buffer we send that to the target
        if self.buffer:
            self.socket.send(self.buffer)
        # we define this block so we can close the connection manually with CTRL+C 
        try:
            # we start a loop to receive data from the target
            while True:
                # we initialize the variables recv_len = response data length, and response which is the data itself
                recv_len = 1
                response = ''
                while recv_len:
                    # Receive data from the socket. The return value is a bytes object representing the data received. The maximum amount of data to be received at once is specified by bufsize. (socket.recv(buffsize))
                    data = self.socket.recv(4096)
                    # we pack all the data in the response variable
                    response += data.decode()
                    # if there is no more data we break out the loop
                    if recv_len < 4096:
                        break
                # then we print the response and we open the posibillity to create another buffer data to send
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                self.socket.send(buffer.encode())
        # The loop will continue until we make a KeyboardInterrupt which will close the socket.
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()
    
    def listen(self):
        # socket.bind(address) 
        # Bind the socket to address. The socket must not already be bound. (The format of address depends on the address family), in this case we use
        #       --> A pair (host, port) is used for the AF_INET address family, where host is a string representing either a hostname in internet domain notation like 'daring.cwi.nl' or an IPv4 address like '100.50.200.5', and port is an integer. 
        self.socket.bind((self.args.target, self.args.port))
        # socket.listen([backlog])
        # Enable a server to accept connections. If backlog is specified, it must be at least 0 (if it is lower, it is set to 0); it specifies the number of unaccepted connections that the system will allow before refusing new connections.
        self.socket.listen(5)
        # then we start a loop 
        while True:
            # socket.accept()
            # Accept a connection. The socket must be bound to an address and listening for connections. The return value is a pair (conn, address) where conn is a new socket object usable to send and receive data on the connection, and address is the address bound to the socket on the other end of the connection.
            client_socket, _ = self.socket.accept()
            # we pass the connected socket to the handle method
            client_thread = threading.Thread(
                target = self.handle, args=(client_socket,)
            )
            client_thread.start()

    # this function executes the task corresponding to the argument it receives, it creates a shell, it executes a command or it upload a file .
    def handle(self, client_socket):
        # if the argument is execute we pass the argument to the execute function 
        if self.args.execute:   
            # we send the execute arguments to the function
            output = execute(self.args.execute)
            # sends the output back on the socket
            client_socket.send(output.encode())
        elif self.args.upload:
            # the b before the string indicates that the content its in bytes
            file_buffer = b''
            # while there is incoming data we keep the loop and pack the data in file_buffer
            while True:
                data = client_socket.recv(4096)
                if data: 
                    file_buffer += data
                else:
                    break
            # then we write the accumulated content to an specified file
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            # we notify everything's ok
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    # we send a prompt to the sender and wait for a command string to come back
                    client_socket.send(b'BHP: #> ')
                    # we recieve the hole command and we packed it in cmd_buffer
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    # we execute the command and save the response
                    response = execute(cmd_buffer.decode())
                    # if there is a response we send it back to the listener
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()

if __name__ == '__main__':
    # we use the argparse module, from the standar library to create a command interface
    parser = argparse.ArgumentParser(
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter, 
        epilog=textwrap.dedent('''Example
            netcat.py -t 192.168.1.108 -p 5555 -l -c                     # command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt          # upload to file
            netcat.py -t 192.168.1.108 -p 5555 -l -e="cat /etc/pssswd"   # execute a command
            echo 'ABC' | netcat.py -t 192.168.1.108 -p 135               # echo text to server port 135
    '''))
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', action='store_true', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified ip')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()
    # If we are setting it up as a listener we invoke the netcat object with no arguments, otherwise we send the buffer content from stdin
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()
    nc = Network_Sparrow(args,buffer.encode())
    # we call the run method 
    nc.run() 