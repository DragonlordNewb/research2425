import serial
import socket
import sys
import time

SERIAL_PORT_NAME = "/dev/ttyACM0"
BAUD = 9600
TCP_PORT = 0x4E48

serial_port: serial.Serial = None
tcp_socket: socket.socket = None

def println(*args):
	print(*args, end="                         \r")

if __name__ == "__main__":
	if len(sys.argv) == 4:
		SERIAL_PORT_NAME, BAUD, tcp_PORT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
	elif len(sys.argv) == 3:
		SERIAL_PORT_NAME, BAUD = sys.argv[1], int(sys.argv[2])
	elif len(sys.argv) == 2:
		SERIAL_PORT_NAME = sys.argv[1]

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
	try:
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
				conn.close()
			except:
				pass
			serial_port.close()
			exit(1)
		print("Got connection from client at " + addr_str + ".")

		serial_port.readline()

		timeout = 0
		last = None

		print("Status\tData\tTimeout\t\tNDPR")

		while True:
			try:
				while True:
					if serial_port.in_waiting > 0:
						data = serial_port.readline().decode("utf-8").strip()
						try:
							num = float(data)
						except:
							print("ERROR\tERROR\t" + str(timeout/20) + "\t█\tDATA FEED ERROR")
							continue
						if num == 0:
							print("ERROR\tERROR\t" + str(timeout/20) + "\t█\tINTERFEROMETER SYSTEM ERROR")
							continue
						else:
							last = num
							println("OK\t" + str(last) + "\t" + str(timeout/20) + "\t█")
							conn.send(data.encode("utf-8"))
					elif timeout < 100:
						println("OK\t" + str(last) + "\t" + str(timeout/20))
						timeout += 1
						time.sleep(.05)
					else:
						println("ERROR\tERROR\tTIMEOUT\tINTERFEROMETER TIMEOUT ERROR")
			except KeyboardInterrupt:
				if input("Shut down server? (y/n) ") == "n":
					tcp_socket.close()
					conn.close()
					serial_port.close()
					print("Server systems closed and shut down.")
					exit(0)
	except Exception as e:
		print("Fatal error; TCP address and serial port saved!")
		conn.close()
		tcp_socket.close()
		serial_port.close()
		raise e