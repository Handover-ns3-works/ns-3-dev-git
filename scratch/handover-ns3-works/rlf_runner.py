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
	
class Handover(Enum):
	A3_RSRP = 0
	A2A4_RSRQ = 1

def execute_simulation(ttt, hys, servingCellThreshold, neighbourCellOffset, speed, angle, q_out, q_in, t_310, n_310, n_311, fading_model, handover_algorithm):
	config = f"--timeToTrigger={ttt} --hysteresis={hys} --servingCellThreshold={servingCellThreshold} --neighbourCellOffset={neighbourCellOffset} --speed={speed} --angle={angle}--Qout={q_out} --Qin={q_in} --T310={t_310} --N310={n_310} --N311={n_311} --fadingModel={fading_model.value} --handoverAlgorithm={handover_algorithm.value}"
	
	# This requires handling of batch results
	# for j in range(1, iterationsPerConfig+1):
	# print("Running iteration " + str(j))
	
	
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
	
	return {
		"ttt": ttt,
		"hys": hys,
		"servingCellThreshold": servingCellThreshold,
		"neighbourCellOffset": neighbourCellOffset,
		"speed": speed,
		"angle": angle,
		"Qout": q_out,
		"Qin": q_in,
		"T310": t_310,
		"N310": n_310,
		"N311": n_311,
		"fading_model": FadingModel(fading_model).name,
		"handover_algorithm": Handover(handover_algorithm).name,
		"output": output, 
		"stderr": result.stderr,
		"rlf_count": rlf_count, 
		"handover_count": ho_count,
		"hof_command": hof_com, 
		"hof_ttt": hof_ttt,
		"hof_total": hof_ttt + hof_com,
	}
		
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Command line argument parser")
	parser.add_argument('run_name', type=str, help='Run Name')
	# parser.add_argument('--ttt', action='store_true', help='Vary ttt')
	# parser.add_argument('--hys', action='store_true', help='Vary hys')
	# parser.add_argument('--speed', action='store_true', help='Vary speed')
	# parser.add_argument('--angle', action='store_true', help='Vary angle')
	# parser.add_argument('--Qout', action='store_true', help='Vary Qout')
	# parser.add_argument('--Qin', action='store_true', help='Vary Qin')
	# parser.add_argument('--T310', action='store_true', help='Vary T310')
	# parser.add_argument('--N310', action='store_true', help='Vary N310')
	# parser.add_argument('--N311', action='store_true', help='Vary N311')
	args = parser.parse_args()
	
	out_dir = "./"
	run_name = args.run_name
	
	# Default run values, change if needed
	ttt = [256]
	hys = [3]
	servingCellThreshold = [30]
	neighbourCellOffset = [1]
	speed = [20]
	angle = [0]
	Qout = [-5]
	Qin = [-3.9]
	T310 = [1000]
	N310 = [6]
	N311 = [2]	
	fading_model = [FadingModel.DETERMINISTIC]
	handover_algorithm = [Handover.A3_RSRP]
	
	# Testing params
	# Uncomment the params that you want to vary
	# ttt = [0, 40, 64, 80, 100, 128, 160, 256, 320, 480, 512, 640, 1024, 1280, 2560, 5120]
	# hys = [0.5*i for i in range(0, 31)]
	# servingCellThreshold = [i for i in range(0, 34)]
	# neighbourCellOffset = [i for i in range(0, 34)]
	# speed = list(range(10, 101, 10))
	# angle = list(range(10, 91, 10))
	# Qout = [-6 + 0.5*i for i in range(0, 13)]
	# Qin = [-4 + 0.5*i for i in range(0, 17)]
	# T310 = [0, 50, 100, 200, 500, 1000, 2000]
	# N310 = [1, 2, 3, 4, 6, 8, 10, 20]
	# N311 = [1, 2, 3, 4, 5, 6, 8, 10]
	# 0 = Deterministic, 1 = Rayleigh, 2 = Correlated
	# fading_model = [FadingModel.RAYLEIGH, FadingModel.CORRELATED]
	# handover_algorithm = [Handover.A2A4_RSRQ]
		
	# number of iterations to run for each configuration
	# iterationsPerConfig = 1

	# profile = subprocess.check_output(['./ns3', 'show profile'])
	# if profile[-1] != 'optimized':
	# 	subprocess.check_output(['./ns3', 'show profile'])
	
	with ProcessPoolExecutor() as executor:
		sims = []

		for run_values in list(product(ttt, hys, servingCellThreshold, neighbourCellOffset, speed, angle, Qout, Qin, T310, N310, N311, fading_model, handover_algorithm)):
			sims.append(executor.submit(execute_simulation, *run_values))	

		# results = [future.result() for future in sims]
		results = [future.result() for future in tqdm(sims, desc="Processing simulations")]

		# Filter out failed executions
		results = [item for item in results if item is not None]

		try:
			with open(f'{out_dir}{run_name}.json', 'w', encoding='utf-8') as json_file:
				json.dump(results, json_file, ensure_ascii=False, indent=2)

			keys_to_include = ['ttt', 'hys', 'servingCellThreshold', 'neighbourCellOffset', 'speed', 'angle', 'Qout', 'Qin', 'T310', 'N310', 'N311', 'fading_model', 'handover_algorithm', 'handover_count', 'rlf_count', 'hof_command', 'hof_ttt', 'hof_total']
			with open(f'{out_dir}{run_name}.csv', 'w', newline='', encoding='utf-8') as csv_file:
					writer = csv.DictWriter(csv_file, fieldnames=keys_to_include)

					writer.writeheader()
					for item in results:
							# Filtering the dictionary to only include the specified keys
							row = {key: item[key] for key in keys_to_include}
							writer.writerow(row)
		except Exception as e:
			print(e)
			print(results)
		