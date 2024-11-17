import socket
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from collections import deque
import sys

# Socket configuration
SERVER_IP = sys.argv[1]  # Replace with Raspberry Pi's IP
SERVER_PORT = 20040

# Visualization configuration
BUFFER_SIZE = 100  # Number of points to display on the graphs

class InterferometerClientApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Interferometer Client")
		
		# Data buffers
		self.data_buffer = deque([0] * BUFFER_SIZE, maxlen=BUFFER_SIZE)
		self.derivative_buffer = deque([0] * BUFFER_SIZE, maxlen=BUFFER_SIZE)

		# Tkinter Frames
		self.graph_frame = ttk.Frame(root)
		self.graph_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
		
		self.analysis_frame = ttk.Frame(root)
		self.analysis_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

		# Matplotlib figures
		self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 5))
		self.fig.tight_layout()

		# Line graph for raw data
		self.line, = self.ax1.plot([], [], 'b-')
		self.ax1.set_title("Raw Data")
		self.ax1.set_xlabel("Time (points)")
		self.ax1.set_ylabel("Value")
		self.ax1.set_xlim(0, BUFFER_SIZE)
		self.ax1.set_ylim(0, 1000000)  # Adjust if necessary

		# Line graph for derivative
		self.derivative_line, = self.ax2.plot([], [], 'r-')
		self.ax2.set_title("Percent Change (Derivative)")
		self.ax2.set_xlabel("Time (points)")
		self.ax2.set_ylabel("Percent Change")
		self.ax2.set_xlim(0, BUFFER_SIZE)
		self.ax2.set_ylim(-100, 100)  # Adjust if necessary

		# Matplotlib Canvas
		self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

		# Analysis Section
		self.mean_label = ttk.Label(self.analysis_frame, text="Mean: --")
		self.mean_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
		
		self.std_label = ttk.Label(self.analysis_frame, text="Standard Deviation: --")
		self.std_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

		# Start the socket connection and update loop
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((SERVER_IP, SERVER_PORT))
		self.data_buffer.append(0)
		self.update_data()

	def update_data(self):
		try:
			# Receive data
			data = self.socket.recv(1024).decode('utf-8').strip()
			print("Received:", data)
			if "GOOD" in data or "WEAK" in data:
				_, value = data.split()
				value = int(value)

				# Update data buffer
				self.data_buffer.append(value)

				# Compute derivative
				if len(self.data_buffer) > 1:
					prev_value = self.data_buffer[-1]
					percent_change = 0 if prev_value == 0 else ((value - prev_value) / prev_value) * 100
					self.derivative_buffer.append(percent_change)
				else:
					self.derivative_buffer.append(0)

				# Update plots
				self.update_plots()

				# Update analysis
				self.update_analysis()

			else:

				print("Bad data")

		except Exception as e:
			print(f"Error receiving data: {e}")
		
		# Schedule next update
		self.root.after(100, self.update_data)

	def update_plots(self):
		# Update raw data plot
		self.line.set_xdata(range(len(self.data_buffer)))
		self.line.set_ydata(self.data_buffer)
		self.ax1.relim()
		self.ax1.autoscale_view()

		# Update derivative plot
		self.derivative_line.set_xdata(range(len(self.derivative_buffer)))
		self.derivative_line.set_ydata(self.derivative_buffer)
		self.ax2.relim()
		self.ax2.autoscale_view()

		# Redraw canvas
		self.canvas.draw()

	def update_analysis(self):
		# Compute mean and standard deviation
		data_array = np.array(self.data_buffer)
		mean = np.mean(data_array)
		std = np.std(data_array)

		# Update labels
		self.mean_label.config(text=f"Mean: {mean:.2f}")
		self.std_label.config(text=f"Standard Deviation: {std:.2f}")

# Main Tkinter loop
if __name__ == "__main__":
	root = tk.Tk()
	app = InterferometerClientApp(root)
	root.mainloop()
