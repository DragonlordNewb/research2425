import socket
import matplotlib.pyplot as plt
from collections import deque
import sys

# Socket configuration
SERVER_IP = sys.argv[1]
SERVER_PORT = 20040

# Visualization configuration
BUFFER_SIZE = 100  # Number of points to display on the graph

def main():
    data_queue = deque(maxlen=BUFFER_SIZE)  # Circular buffer for plotting

    # Initialize connection to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")

    plt.ion()  # Interactive mode
    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'b-')
    ax.set_xlim(0, BUFFER_SIZE)
    ax.set_ylim(0, 2**64)  # Adjust according to data range
    ax.set_title("Live Data Plot")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Interferometer Value")

    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8').strip()
            if "GOOD" in data or "WEAK" in data:
                _, value = data.split()
                value = int(value)
                data_queue.append(value)
                line.set_xdata(range(len(data_queue)))
                line.set_ydata(list(data_queue))
                ax.relim()
                ax.autoscale_view()
                plt.pause(0.1)
    except KeyboardInterrupt:
        print("Client shutting down...")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
