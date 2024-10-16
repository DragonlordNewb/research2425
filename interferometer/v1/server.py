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
	print(*args, end="\r                     ")

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
	println("  Finding relay information ...")
	relay_hn = socket.gethostname()
	relay_ip = socket.gethostbyname(relay_hn)
	print("  Found relay information - hostname", relay_hn, "IPv4", relay_ip)
	println("  Opening TCP socket ...")
	tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("  Successfully opened TCP socket on network as " + relay_hn + ".")
	println("  Binding socket to address ...")
	tcp_socket.bind((relay_ip, TCP_PORT))
	addr_str = relay_ip + ":" + str(TCP_PORT)
	tcp_socket.listen(1)
	print("  TCP socket bound to relay address at " + addr_str + ".")
	print("Finished network connection setup.")
	println("Awaiting connection from client ...")
	conn, addr = tcp_socket.accept()
	client_ip, client_port = addr
	addr_str = client_ip + ":" + str(client_port)
	print("Got connection from client at " + addr_str + ".")
	println("Transmitting data live...\t\tNO FEED")

	serial_port.readline()

	timeout = 0
	last = None

	print("Status\tData\tTimeout\tNDPR")

	while True:
		try:
			while True:
				if serial_port.in_waiting > 0:
					data = serial_port.readline().decode("utf-8").strip()
					num = float(data)
					if num == 0:
						print("ERROR\t" + last + "\t" + str(timeout) + "\t█")
					else:
						println("OK\t" + last + "\t" + str(timeout) + "\t█")
						last = data
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

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Invalid syntax: \"python3 relay.py <target> <port>\"")
		exit(-1)
	print("Loading serial connection ...", end="")
	sys.stdout.flush()
	ser = serial.Serial(sys.argv[2], 9600)
	print("done.\nLoading socket ...", end="")
	sys.stdout.flush()
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print("done, ready to transmit data.")

	ser.readline()

	while True:
		try:
			while True:
				# Read data from Arduino
				if ser.in_waiting > 0:
					data = ser.readline().decode('utf-8').strip()
					print(f"Received from interferometer: {data}")
					
					# Send data to TCP client
					sock.sendto(data.encode('utf-8'), (sys.argv[1], 7777))
				else:
					print("No feed.")
					time.sleep(.1)

		except KeyboardInterrupt:
			if input("Continue? (y/n) ") == "n":
				sock.close()
				ser.close()
		