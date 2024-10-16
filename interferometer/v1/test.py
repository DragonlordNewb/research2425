from socket import *
import time
s = socket(AF_INET,SOCK_STREAM)
s.bind(("10.0.0.70",1234))
s.connect(("10.0.0.22",0x4e48))
try:
	while True:
		time.sleep(0.05)
		print(s.recv(1024))
except:
	pass
s.close()