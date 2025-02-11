import serial
import socket
import sys
import time
import random

if len(sys.argv) not in (3, 4):
	print("Invalid syntax (correct syntax: \"python3 server.py <serial port> <server host> [-t]\")")
	exit()

# Serial configuration
SERIAL_PORT = sys.argv[1]
BAUD_RATE = 9600

# Socket configuration
SERVER_HOST = sys.argv[2]
SERVER_PORT = 20040

TESTING_MODE = len(sys.argv) == 3

def main():
	print("Serial port:", SERIAL_PORT)
	print("Server address:", SERVER_HOST + ":" + str(SERVER_PORT))
	print("Testing mode:", TESTING_MODE)
	# Initialize Serial Connection
	if not TESTING_MODE:
		ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
	
	# Initialize Socket Server
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind((SERVER_HOST, SERVER_PORT))
	server_socket.listen(1)
	print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

	client_socket, client_address = server_socket.accept()
	print(f"Client connected: {client_address}")

	try:
		if TESTING_MODE:
			while True:
				s = ("GOOD " + str(random.randint(2000, 2100)))
				print("Sending dummy data:", s)
				client_socket.sendall(s.encode("utf-8") + b"\n")
				time.sleep(1)
		else:
			while True:
				# Read line from Serial
				if ser.in_waiting > 0:
					data = ser.readline().decode('utf-8').strip().split(".")[0]
					print(f"Received: {data}")
					client_socket.sendall(data.encode('utf-8') + b'\n')  # Send to client
	except KeyboardInterrupt:
		print("Shutting down...")
	finally:
		if not TESTING_MODE:
			ser.close()
		client_socket.close()
		server_socket.close()

if __name__ == "__main__":
	main()