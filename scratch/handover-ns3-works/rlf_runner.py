import json
import csv
import subprocess

def execute_simulation(ttt, hys, speed, angle):
	config = f"--timeToTrigger={ttt} --hysteresis={hys} --speed={speed} --angle={angle}"
	
	# This requires handling of batch results
	# for j in range(1, iterationsPerConfig+1):
	# print("Running iteration " + str(j))
	
	try: 
		output = subprocess.check_output([
			"./ns3", "run", 
			'"scratch/handover-ns3-works/scenario/scenario.cc ' + config + '"'
		])
		output = output.decode("utf-8")
	except subprocess.CalledProcessError as e:
		print("Error running simulation")
		return None;
	
	# RNTIs where the Handover command was recieved when T310 timer was running
	# Supposed to be reported as a HOF, but NS-3 is configured with an Ideal RRC, so it doesn't happen
	# This needs to be subtracted from number of HOs, to give actual number of Handovers
	t310_rnti = set([x.split()[-1] for x in output.split('\n') if 'T310' in x])
	rlf_rnti = set([x.split()[-1] for x in output.split('\n') if 'RLF occurred' in x])
	ttt_rnti = set([x.split()[-1] for x in output.split('\n') if 'TTT' in x])
	handover_command_rnti = set([x.split()[-1] for x in output.split('\n') if 'Handover Command' in x])
	handover_ok_rnti = set([x.split()[-1] for x in output.split('\n') if 'Handover_ok' in x])
	
	# This will give a wrong count if the events happen separately
	# It's not checking if the rlf happened during the ttt or the handover command was recieved during t310
	hof_com = len(t310_rnti.intersection(handover_command_rnti))
	hof_ttt = len(ttt_rnti.intersection(rlf_rnti))
	
	return {
		"ttt": ttt,
		"hys": hys,
		"speed": speed,
		"angle": angle,
		"output": output, 
		"rlf_count": len(rlf_rnti), 
		"handover_count": len(handover_ok_rnti) - hof_com,
		"hof_command": hof_com, 
		"hof_ttt": hof_ttt,
		"hof_total": hof_ttt + hof_com,
	}
		

out_dir = "./"
run_name = input("Enter run name: ")

# ttt=[256]
ttt=[0, 40, 64, 80, 100, 128, 160, 256, 320, 480, 512, 640, 1024, 1280, 2560, 5120]
# hys = [3]
hys = [0.5*i for i in range(0, 31)]
# speed = [20]
speed = list(range(10, 101, 10))
# angle = [0]
angle = list(range(10, 61, 10))

# number of iterations to run for each configuration
# iterationsPerConfig = 1

from concurrent.futures.process import ProcessPoolExecutor
executor = ProcessPoolExecutor()
sims = []

for t in ttt: 
	for h in hys:
		for s in speed:
			for a in angle:
				sims.append(executor.submit(execute_simulation, t, h, s, a))	


results = [future.result() for future in sims]

# Filter out failed executions
results = [item for item in results if item is not None]


with open(f'{out_dir}{run_name}.json', 'w', encoding='utf-8') as json_file:
	json.dump(results, json_file, ensure_ascii=False, indent=2)

keys_to_include = ['ttt', 'hys', 'speed', 'angle', 'rlf_count', 'hof_command', 'hof_ttt', 'hof_total']
with open(f'{out_dir}{run_name}.csv', 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=keys_to_include)

    writer.writeheader()
    for item in results:
        # Filtering the dictionary to only include the specified keys
        row = {key: item[key] for key in keys_to_include}
        writer.writerow(row)


executor.shutdown()