import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import sys
import json

def parse_csv_string(data):
		node_ids = []
		xs = []
		ys = []
		
		for line in data:
				# Split on comma and convert each part to a float or int as needed
				parts = line.split(',')
				
				# Convert values from strings to numbers:
				node_id = int(parts[1].strip())
				x = float(parts[2].strip())
				y = float(parts[3].strip())
				
				node_ids.append(node_id)
				xs.append(x)
				ys.append(y)
		
		return node_ids, xs, ys

def plot_csv(filename):
		try:
				with open(filename, "r") as f:
						data = json.load(f)
		except Exception as e:
				print(f"Error reading or parsing {filename}: {e}")
				return None
		
		# # node_ids, xs, ys = parse_csv_string(data["results"][0]["ue_positions_csv"])
		# # using set(map(float, "123,543,51.3".split(',')))
		# records = [set(map(float, line.split(','))) for line in data["results"][0]["ue_positions_csv"]]

		# # Make a line plot of the data
		# unique_nodes = sorted(set(record[0] for record in records))
		# n_nodes = len(unique_nodes)
		
		# # Create a colormap with one distinct color per node.
		# # Here, 'viridis' is used but you can choose any Matplotlib colormap.
		# colormap = cm.get_cmap('viridis', n_nodes)
		
		# # Map each unique node id to a color from the colormap.
		# node_color = {node: colormap(i) for i, node in enumerate(unique_nodes)}
		
		node_dict = {}

		# Process each CSV row
		for row in data["results"][0]["ue_positions_csv"]:
				# Split the row into parts and convert them to appropriate types
				parts = row.split(',')
				node_id = int(parts[1])
				x = float(parts[2])
				y = float(parts[3])
				
				# Update the dictionary for the given node id
				if node_id not in node_dict:
						node_dict[node_id] = {'x': [], 'y': []}
				
				node_dict[node_id]['x'].append(x)
				node_dict[node_id]['y'].append(y)
		
		num_nodes = len(node_dict)
		colors = plt.cm.jet(np.linspace(0, 1, num_nodes))

		# Create a new plot
		plt.figure(figsize=(8, 6))

		# Plot each node's data with a different color
		for (node_id, coords), color in zip(sorted(node_dict.items()), colors):
				plt.plot(coords['x'], coords['y'], marker='o', color=color, label=f'Node {node_id}')
				
		plt.xlabel('X')
		plt.ylabel('Y')
		plt.title('2D Plot of Nodes from CSV')
		plt.grid(True)
		plt.show()

if __name__ == "__main__":
	# Check if a filename was provided as a command-line argument
	if len(sys.argv) < 2:
			print("Usage: python script.py <filename>")
			sys.exit(1)

	# Pick the first argument that the user provided as the filename
	filename = sys.argv[1]
	print("Filename provided:", filename)
			
	plot_csv(filename)
