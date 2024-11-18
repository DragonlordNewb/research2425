import socket
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from collections import deque
import sys
import csv
import threading
from datetime import datetime

# Socket configuration
SERVER_IP = sys.argv[1]  # Replace with Raspberry Pi's IP
SERVER_PORT = 20040

# Visualization configuration
BUFFER_SIZE = 100  # Number of points to display on the graphs

class InterferometerClientApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Interferometer Client")
		
		self.data_buffer = deque([0] * BUFFER_SIZE, maxlen=BUFFER_SIZE)
		self.derivative_buffer = deque([0] * BUFFER_SIZE, maxlen=BUFFER_SIZE)
		self.event_log = []  # List to store logged events

		self.graph_frame = ttk.Frame(root)
		self.graph_frame.grid(row=1, column=1)
		
		self.analysis_frame = ttk.Frame(root)
		self.analysis_frame.grid(row=2, column=1, columnspan=2)

		self.event_frame = ttk.Frame(root, width=250)
		self.event_frame.grid(row=1, column=2)
		
		self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 5))
		self.fig.tight_layout()

		self.line, = self.ax1.plot([], [], 'b-')
		self.ax1.set_title("Raw Data")
		self.ax1.set_ylabel("Value")
		self.ax1.set_xlim(0, BUFFER_SIZE)
		self.ax1.set_ylim(0, 1000000)  # Adjust if necessary

		self.derivative_line, = self.ax2.plot([], [], 'r-')
		self.ax2.set_title("Percent Change (Derivative)")
		self.ax2.set_xlim(0, BUFFER_SIZE)
		self.ax2.set_ylim(-100, 100)  # Adjust if necessary

		self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)  # Added padding

		self.mean_label = ttk.Label(self.analysis_frame, text="Mean: --")
		self.mean_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")  # Added padding
		
		self.std_label = ttk.Label(self.analysis_frame, text="Standard Deviation: --")
		self.std_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")  # Added padding

		# Save Data Button
		self.save_button = ttk.Button(self.analysis_frame, text="Save Data", command=self.open_save_window)
		self.save_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

		# Event log header
		self.event_label = ttk.Label(self.event_frame, text="Events", font=("Arial", 14, "bold"))
		self.event_label.pack(padx=10, pady=10)

		self.event_listbox = tk.Listbox(self.event_frame, height=20, width=40, selectmode=tk.SINGLE)
		self.event_listbox.pack(padx=10, pady=10)

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((SERVER_IP, SERVER_PORT))

		self.index = -1
		
		# Start the data reception in a separate thread
		self.data_thread = threading.Thread(target=self.receive_data)
		self.data_thread.daemon = True  # Daemon thread will exit when the main program exits
		self.data_thread.start()

	def receive_data(self):
		"""Handle data reception in a separate thread."""
		while True:
			try:
				# Receive data
				data = self.socket.recv(1024).decode('utf-8').strip()
				print("Received:", data)
				if "GOOD" in data or "WEAK" in data:
					_, value = data.split()
					value = int(value)

					# Update data buffer
					self.index += 1
					self.data_buffer.append(value)

					# Compute derivative
					if len(self.data_buffer) > 1:
						prev_value = self.data_buffer[-1]
						percent_change = 0 if prev_value == 0 else ((value - prev_value) / prev_value) * 100
						self.derivative_buffer.append(percent_change)
					else:
						self.derivative_buffer.append(0)

					# Check if the data point is an "event" (more than 2 standard deviations away)
					self.check_for_event(value)

					# Update the GUI (must be done in the main thread)
					self.root.after(0, self.update_plots)
					self.root.after(0, self.update_analysis)
				else:
					print("Bad data")

			except Exception as e:
				print(f"Error receiving data: {e}")

	def check_for_event(self, value):
		"""Check if the data point is an event and log it if necessary."""
		# Calculate the mean and standard deviation of the current data buffer
		data_array = np.array(self.data_buffer)
		mean = np.mean(data_array)
		std = np.std(data_array)

		# Check if the point is more than 2 standard deviations away from the mean
		if abs(value - mean) > 2 * std:
			# Calculate the significance level
			deviation = abs(value - mean) / std
			significance = self.get_significance_level(deviation)
			if significance == None:
				return

			# Create the event message
			event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			event_message = f"{event_time} - {self.index} - {value} - {significance} ({deviation:.2f} SD)"
			
			# Log the event
			self.event_log.append(event_message)

			# Update the event listbox in the GUI (must be done in the main thread)
			self.root.after(0, self.update_event_log)

	def get_significance_level(self, deviation):
		"""Return a significance rating based on the number of standard deviations."""
		if deviation < 2:
			return None
		elif deviation < 3:
			return "D"
		elif deviation < 5:
			return "C"
		elif deviation < 7.5:
			return "B"
		elif deviation < 10:
			return "A"
		else:
			return "S"

	def update_event_log(self):
		"""Update the event log display."""
		# Clear the existing event list
		self.event_listbox.delete(0, tk.END)

		# Add the logged events to the listbox
		for event in self.event_log:
			self.event_listbox.insert(tk.END, event)

	def open_save_window(self):
		"""Open a new window to save the data as a CSV file."""
		save_window = tk.Toplevel(self.root)
		save_window.title("Save Data")
		
		ttk.Label(save_window, text="Select the location to save the data:").pack(padx=10, pady=10)

		def save_data():
			# Ask for file path using file dialog
			file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
			if file_path:
				self.save_data_to_csv(file_path)
				save_window.destroy()

		# Save button in the save window
		ttk.Button(save_window, text="Save", command=save_data).pack(pady=10)
		ttk.Button(save_window, text="Cancel", command=save_window.destroy).pack(pady=5)

	def save_data_to_csv(self, file_path):
		"""Save the data buffers to a CSV file."""
		# Prepare data to be written to CSV
		data_to_save = zip(self.data_buffer, self.derivative_buffer)

		# Write to CSV
		with open(file_path, mode='w', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(['Raw Data', 'Derivative'])  # Column headers
			for row in data_to_save:
				writer.writerow(row)
			print(f"Data saved to {file_path}")

	def update_plots(self):
		# Update raw data plot
		self.line.set_xdata(range(len(self.data_buffer)))
		self.line.set_ydata(self.data_buffer)

		# Dynamically adjust Y-axis limits for raw data
		if len(self.data_buffer) > 0:
			min_val = min(self.data_buffer)
			max_val = max(self.data_buffer)
			self.ax1.set_ylim(min_val - 0.1 * abs(min_val), max_val + 0.1 * abs(max_val))  # Add 10% padding
		self.ax1.set_xlim(0, len(self.data_buffer))

		# Update derivative plot
		self.derivative_line.set_xdata(range(len(self.derivative_buffer)))
		self.derivative_line.set_ydata(self.derivative_buffer)

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
