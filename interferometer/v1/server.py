import serial
import socket
import sys
import time

TARGET_IP = None
SERIAL_PORT_NAME = "/dev/ttyACM0"
BAUD = 9600
TCP_PORT = 0x4E48

serial_port: serial.Serial = None
tcp_socket: socket.socket = None

def println(*args):
	print(*args, end="                         \r")

if __name__ == "__main__":
	if len(sys.argv) == 5:
		TARGET_IP, SERIAL_PORT_NAME, BAUD, tcp_PORT = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
	elif len(sys.argv) == 4:
		TARGET_IP, SERIAL_PORT_NAME, BAUD = sys.argv[1], sys.argv[2], int(sys.argv[3])
	elif len(sys.argv) == 3:
		TARGET_IP, SERIAL_PORT_NAME = sys.argv[1:3]
	elif len(sys.argv) == 2:
		TARGET_IP = sys.argv[1]
	else:
		print("Syntax error: correct syntax requires at least a target IP")
		print("Correct syntax: \"python3 relay.py <IP> [<serial>] [<bauds>] [<tcp port>]\"")
		exit(-1)

	println("Loading serial connection ...")
	ser_sload = time.time()
	serial_port = serial.Serial(SERIAL_PORT_NAME, BAUD)
	ser_eload = time.time()
	ser_dt = ser_eload - ser_sload
	print("Successfully loaded serial connection (" + str(ser_dt) + ").")
	print("Loading network connection ...")
	println("  Finding relay address ...")
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	relay_ip = s.getsockname()[0]
	s.close()
	print("  Found relay IPv4 address -", relay_ip)
	println("  Opening TCP socket ...")
	tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("  Successfully opened TCP socket on network as " + relay_ip + ".")
	println("  Binding socket to address ...")
	tcp_socket.bind((relay_ip, TCP_PORT))
	addr_str = relay_ip + ":" + str(TCP_PORT)
	tcp_socket.listen(1)
	print("  TCP socket bound to relay address at " + addr_str + ".")
	print("Finished network connection setup.")
	println("Awaiting connection from client ...")
	try:
		conn, addr = tcp_socket.accept()
		client_ip, client_port = addr
		addr_str = client_ip + ":" + str(client_port)
	except KeyboardInterrupt:
		print("Server setup aborted. Quitting ...             ")
		try:
			tcp_socket.close()
		except:
			pass
		serial_port.close()
		exit(1)
	print("Got connection from client at " + addr_str + ".")

	serial_port.readline()

	timeout = 0
	last = None

	print("Status\tData\tTimeout\tNDPR")

	while True:
		try:
			while True:
				if serial_port.in_waiting > 0:
					data = serial_port.readline().decode("utf-8").strip()
					try:
						num = float(data)
					except:
						print("ERROR\tERROR\t" + str(timeout) + "\t█")
					if num == 0:
						print("ERROR\tERROR\t" + str(timeout) + "\t█")
					else:
						last = num
						println("OK\t" + last + "\t" + str(timeout) + "\t█")
						tcp_socket.send(data.encode("utf-8"))
				else:
					println("OK\t" + last + "\t" + str(timeout))
					timeout += .1
					time.sleep(.1)
		except KeyboardInterrupt:
			if input("Shut down server? (y/n) ") == n:
				tcp_socket.close()
				serial_port.close()
				print("Server systems closed and shut down.")
				exit(0)