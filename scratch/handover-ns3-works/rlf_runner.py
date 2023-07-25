
import subprocess

ttt=[0, 0.04, 0.08, 0.1, 0.128, 0.16, 0.256, 0.32, 0.48, 0.572, 0.64, 0.024, 1.28, 2.56, 5.120]
hys = [1 for i in range(0, len(ttt))]

# create a list of strings like --timeToTrigger=ttt[i] --hysteresis=hys[i]
args = ["--timeToTrigger=" + str(ttt[i]) + " --hysteresis=" + str(hys[i]) for i in range(0, len(ttt))]

# number of iterations to run for each configuration
iterationsPerConfig = 10

# selected configurations of hysteresis and timeToTrigger
selectedConfigs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

# init a csv file
filename = "rlf_results.csv"
f = open(filename, "w")
f.write("TTT, Hys, RLF count, RLF average time\n")

for i in selectedConfigs:
	rlfSumByConfig = 0
	rlfAveragesPerIteration = []
	print("Time to trigger: " + str(ttt[i]))
	print("Hysteresis: " + str(hys[i]))
	
	for i in range(1, iterationsPerConfig+1):
		print("Running iteration " + str(i))
		
		# run the simulation with args
		# Catch and exit if there is an error
		try: 
			output = subprocess.check_output([
				"../../ns3", "run", 
				'"scratch/handover-ns3-works/scenario/scenario.cc ' + args[i] + '"'
			])
			output = output.decode("utf-8")
		except subprocess.CalledProcessError as e:
			print("Error running simulation: " + e.output)
			# exit(1)
			##############################################################################################
			break;
		
		rlf_count = [x.split()[-1] for x in output.split('\n') if 'RLF count: ' in x][0]
		rlfSumByConfig += int(rlf_count)

		rlf_times = [x.split()[-1] for x in output.split('\n') if 'RLF time: ' in x]
		rlf_times = sum([float(x) for x in rlf_times]) / len(rlf_times)
		rlfAveragesPerIteration.append(rlf_times)
		
	print("RLF count: " + str(rlf_count))
	rlfAverageTimeByConfig = sum(rlfAveragesPerIteration) / len(rlfAveragesPerIteration)
	print("RLF average time: " + str(rlfAverageTimeByConfig))
	print("---------------------")
	
	f.write(str(ttt[i]) + ", " + str(hys[i]) + ", " + str(rlf_count) + ", " + str(rlfAverageTimeByConfig) + "\n")

f.close()	