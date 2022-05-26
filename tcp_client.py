# code example to create a TCP client
import socket 

target_host = '0.0.0.0'
target_port = 9998

# create a socket object
# AF_INET = indicates standar ipv4 adress
# SOCK_STREAM = indicates the client will be a TCP client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
client.connect((target_host, target_port))

# send some data
client.send(b"Hi hello, we are connecting via tcp protocol across the net xd")

# recieve some data
response = client.recv(4096)

print(response.decode())
client.close()

