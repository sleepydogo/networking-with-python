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
client.send(b"Hi can you read me??")

# recieve some data
response = client.recv(4096)

print(response.decode())
client.close()

