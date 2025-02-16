import os
import sys
import json
import csv
import subprocess
import argparse
from tqdm import tqdm
from concurrent.futures.process import ProcessPoolExecutor
from itertools import product
from enum import Enum

# enum
class FadingModel(Enum):
	DETERMINISTIC = 0
	RAYLEIGH = 1
	CORRELATED = 2
	
class HandoverAlgorithmType(Enum):
	A3_RSRP = 0
	A2A4_RSRQ = 1

def parse_args():
	# Default run values, change if needed	
	ns3_config_map = {
		"simTime": {
			"type": "float",
			"values": [15],
			"help": "Vary the simulation time in seconds. Default: 15. Example: --simTime 10 15 20 30 60",
		},
		"timeToTrigger": {
			"type": "int",
			"values": [256],
			"help": "Vary the time to trigger in ms. Default: 256. Example: --timeToTrigger 0 40 64 80 100 128 160 256 320 480 512 640 1024 1280 2560 5120",
		},
		"hysteresis": {
			"type": "float",
			"values": [3],
			"help": "Vary the hysteresis in dB. Default: 3. Example: --hysteresis 0.5 1 1.5 2 2.5 3 3.5 4 4.5 5 5.5 6",
		},
		"servingCellThreshold": {
			"type": "int",
			"values": [30],
			"help": "Vary the serving cell threshold in dB. Default: 30. Example: --servingCellThreshold 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29",
		},
		"neighbourCellOffset": {
			"type": "int",
			"values": [1],
			"help": "Vary the neighbour cell offset in dB. Default: 1. Example: --neighbourCellOffset 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20",
		},
		"speed": {
			"type": "int",
			"values": [20],
			"help": "Vary the UE speed in km/h. Default: 20. Example: --speed 10 20 30 40 50 60 70 80 90 100",
		},
		"angle": {
			"type": "int",
			"values": [0],
			"help": "Vary the UE speed in degrees. Default: 0. Example: --angle 10 20 30 40 50 60 70 80 90",
		},
		"Qout": {
			"type": "float",
			"values": [-5],
			"help": "Vary the Qout in dB. Default: -5. Example: --Qout -6 -5.5 -5 -4.5 -4 -3.5 -3",
		},
		"Qin": {
			"type": "float",
			"values": [-3.9],
			"help": "Vary the Qin in dB. Default: -3.9. Example: --Qin -4 -3.5 -3 -2.5 -2 -1.5 -1",
		},
		"T310": {
			"type": "int",
			"values": [1000],
			"help": "Vary the T310 timer in ms. Default: 1000. Example: --T310 0 50 100 200 500 1000 2000",
		},
		"N310": {
			"type": "int",
			"values": [6],
			"help": "Vary the N310 timer in ms. Default: 6. Example: --N310 1 2 3 4 5 6 8 10 20",
		},
		"N311": {
			"type": "int",
			"values": [2],
			"help": "Vary the N311 timer in ms. Default: 2. Example: --N311 1 2 3 4 5 6 8 10",
		},
		"fadingModel": {
			"type": "FadingModel",
			"values": [FadingModel.DETERMINISTIC],
			"convertToValue": lambda x: x.value,
			"help": "Vary the fading model. Default: DETERMINISTIC. Example: --fadingModel DETERMINISTIC RAYLEIGH CORRELATED",
		},
		"handoverAlgorithm": {
			"type": "HandoverAlgorithmType",
			"values": [HandoverAlgorithmType.A3_RSRP],
			"convertToValue": lambda x: x.value,
			"help": "Vary the handover algorithm. Default: A3_RSRP. Example: --handoverAlgorithm A3_RSRP A2A4_RSRQ",
		},
		"enbCoordinatesString": {
			"type": "str",
			"values": ["0,0,0,100,0,0"],
			"help": "Vary the eNB coordinates in x,y,z. Each space separated string is one config. Default: 0,0,0,100,0,0. Example: --enbCoordinatesString 0,0,0,100,0,0 0,50,0,0,0,170",
		},
	}
	
	run_config_map = {
		"out_dir": {
			"type": "str",
			"value": "./outputs/",
			"help": "Output directory",
		},
		"debug": {
			"type": "bool",
			"value": False,
			"help": "Debug mode",
		},
		"iterationsPerConfig": {
			"type": "int",
			"value": 1,
			"help": "Vary the number of iterations per configuration. Default: 1. Example: --iterationsPerConfig 5",
		},
		"ignoreColumnOutput": {
			"type": "str",
			"value": [],
			"help": "Ignore the column output. Default: []. Example: --ignoreColumnOutput hysterisis servingCellThreshold",
		},
	}
	
	parser = argparse.ArgumentParser(description="Command line argument parser")
	parser.add_argument('run_name', type=str, help='Run Name')
		
	# combine the run_config and config_map arguments
	for key, value in {**run_config_map, **ns3_config_map}.items():
		parser.add_argument(
			f'--{key}', 
			type=eval(value["type"]),
			nargs='*' if isinstance(value.get("values", None), list) or isinstance(value.get("value", None), list) else None,
			default=value["values"] if key in ns3_config_map.keys() else value["value"],
			help=value["help"]
		)
	
	args = parser.parse_args()
	run_config = {}
	ns3_config = {}
	run_config["run_name"] = args.run_name
	run_config["run_command"] = " ".join(sys.argv)
	# map the args to values in ns3_config and run_config
	for key, value in args.__dict__.items():
		if key == "run_name":
			continue
		elif key in run_config_map.keys():
			run_config[key] = value
		elif "convertToValue" in ns3_config_map[key]:
			ns3_config[key] = [ns3_config_map[key]["convertToValue"](x) for x in value]
		else:
			ns3_config[key] = value
	
	return run_config, ns3_config

def configure_optimized():
	# Check if we are running the optimized profile
	profile = subprocess.check_output(['./ns3', 'show', 'profile'])
	if 'optimized' in profile.decode('utf-8'):
		print("Running optimized profile")
	else:
		print("Configuring optimized profile")
		subprocess.run(['./ns3', 'configure', '--build-profile=optimized', '--out=build/optimized'])

def execute_simulation(run_map, currentIteration):
	config = " ".join([f"--{key}={value} " for key, value in run_map.items()])

	result = subprocess.run(
		["./ns3", "run", '"scratch/handover-ns3-works/scenario/scenario.cc ' + config + '"'],
		capture_output=True, text=True
	)
	output = result.stdout
	
	# RNTIs where the Handover command was recieved when T310 timer was running
	# Supposed to be reported as a HOF, but NS-3 is configured with an Ideal RRC, so it doesn't happen
	# This needs to be subtracted from number of HOs, to give actual number of Handovers
	t310_rnti = set([x.split()[-1] for x in output.split('\n') if 'T310' in x])
	rlf_rnti = set([x.split()[-1] for x in output.split('\n') if 'RLF occurred' in x])
	ttt_rnti = set([x.split()[-1] for x in output.split('\n') if 'TTT' in x])
	handover_command_rnti = set([x.split()[-1] for x in output.split('\n') if 'Handover Command' in x])
	# handover_ok_rnti = set([x.split()[-1] for x in output.split('\n') if 'Handover_ok' in x])
	
	# This will give a wrong count if the events happen separately
	# It's not checking if the rlf happened during the ttt or the handover command was recieved during t310
	hof_com = len(t310_rnti.intersection(handover_command_rnti))
	hof_ttt = len(ttt_rnti.intersection(rlf_rnti))
	
	imsi_states = {}  
	ho_count = 0
	rlf_count = 0
	hof_com = 0
	hof_ttt = 0

	for entry in output.split('\n'):
			if len(entry) == 0:
					continue
			
			imsi = entry.split()[-1]
			state = imsi_states.get(imsi, {"TTT": False, "T310": False})

			if 'T310' in entry:
					state['T310'] = True
			elif 'TTT' in entry:
					state['TTT'] = True
			elif 'Handover Command' in entry:
			# and state['TTT'] commenting this out because A2A4 doesn't have TTT
					state['TTT'] = False
					
					if state['T310']:
							hof_com+=1
					else:
							ho_count+=1
					
			elif 'RLF occurred' in entry:
					state['T310'] = False
					rlf_count+=1
					
					if state['TTT']:
							hof_ttt+=1
							state['TTT'] = False

			imsi_states[imsi] = state
	
	# add the output values to the map
	run_map.update({
		"currentIteration": currentIteration,
		"output": output,
		"stderr": result.stderr,
		"rlf_count": rlf_count,
		"handover_count": ho_count,
		"hof_command": hof_com,
		"hof_ttt": hof_ttt,
		"hof_total": hof_ttt + hof_com,
	})
	
	return run_map
		
if __name__ == "__main__":
	run_config, ns3_config = parse_args()
	run_name = run_config["run_name"]
	out_dir = run_config["out_dir"]
	
	if not run_config["debug"]:
		configure_optimized()
	
	print("Building NS-3")
	subprocess.run(['./ns3', 'build'])
	
	with ProcessPoolExecutor() as executor:
		sims = []

		# run the simulations
		for i in range(run_config["iterationsPerConfig"]):
			
			# get a list of all possible combinations of the ns3_config values
			for run_values in list(product(*[value for value in ns3_config.values()])):
				# create a map of the ns3_config keys and the run_values
				run_map = {}
				for key, value in zip(ns3_config.keys(), run_values):
					run_map[key] = value
					
				# run the simulation
				sims.append(executor.submit(execute_simulation, run_map, i))	

		# wait for the simulations to finish
		results = [future.result() for future in tqdm(sims, desc="Processing simulations")]

		# Filter out failed executions
		results = [item for item in results if item is not None]

		try:
			# Check if the output directory exists, if not create it
			os.makedirs(out_dir, exist_ok=True)
			
			# write the results to a json file
			with open(f'./{out_dir}/{run_name}.json', 'w', encoding='utf-8') as json_file:
				# Enrich the command for easy replication
				json_output = {
					"run_command": run_config["run_command"],
					"results": results
				}
				json.dump(json_output, json_file, ensure_ascii=False, indent=2)

			# check which columns to include
			keys_to_include = [key for key in ns3_config.keys() if key not in run_config["ignoreColumnOutput"]]
			
			# write the results to a csv file
			with open(f'./{out_dir}/{run_name}.csv', 'w', newline='', encoding='utf-8') as csv_file:
					# Create a DictWriter object with the specified fieldnames
					writer = csv.DictWriter(csv_file, fieldnames=keys_to_include)
					writer.writeheader()
					
					# Write the rows to the CSV file
					for item in results:
							# Filtering the dictionary to only include the specified keys
							row = {key: item[key] for key in keys_to_include}
							writer.writerow(row)
							
		except Exception as e:
			print(e)
			print(results)
		