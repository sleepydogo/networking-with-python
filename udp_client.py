# code example to create a UDP client
import socket 

target_host = '127.0.0.1'
target_port = 9997

# create a socket object
# SOCK_DGRAM = indicates it is a UDP client
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send some data
# we use the sentence sendto and not connect because UDP
# is a conection less protocol
client.sendto(b"AAABBBCCC", (target_host, target_port))

# recieve some data
data, addr = client.recvfrom(4096)

print(data.decode())
client.close()