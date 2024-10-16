from socket import *
s = socket(AF_INET,SOCK_STREAM)
s.bind(("10.0.0.70", 1234))
s.connect(("10.0.0.22", 0x4e48))
input("<Enter> to close")
s.close()