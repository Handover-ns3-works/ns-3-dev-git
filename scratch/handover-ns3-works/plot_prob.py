from matplotlib import pyplot as plt
import pandas as pd
metrics = ["rlf_count", "hof_total", "hof_command", "hof_ttt", "handover_count"]
ep=0.00005

c_hys = pd.read_csv("/home/souvik/Documents/handover_journal/sumit roy/Data/Correlated/c_t310.csv")
r=c_hys.shape[0]

c_hys["rlf_count"]=c_hys["rlf_count"]/(c_hys["handover_count"]+c_hys["rlf_count"]+c_hys["hof_command"])


a=[]
for i in range(c_hys.shape[0]):
  
  if c_hys["hof_total"][i]!=0:
    c_hys["hof_command"][i]=c_hys["hof_command"][i]/(c_hys["handover_count"][i]+c_hys["hof_total"][i])
    c_hys["hof_ttt"][i]=c_hys["hof_ttt"][i]/(c_hys["handover_count"][i]+c_hys["hof_total"][i])
  else:
    c_hys["hof_command"][i]=0
    c_hys["hof_ttt"][i]=0
  if c_hys["hof_command"][i]!=0:
    x=(c_hys['hof_ttt'][i])/(c_hys['hof_command'][i])
  else:
    x=(c_hys["hof_ttt"][i]+ep)/ep
  a.append(x)
c_hys['alpha']=a

c_hys.to_csv("c_t310.csv", index=False)

c_speed = pd.read_csv("/home/souvik/Documents/handover_journal/sumit roy/Data/Correlated/c_n310.csv")

c_speed["rlf_count"]=c_speed["rlf_count"]/(c_speed["handover_count"]+c_speed["rlf_count"]+c_speed["hof_command"])


a=[]
for i in range(c_speed.shape[0]):
  
  if c_speed["hof_total"][i]!=0:
    c_speed["hof_command"][i]=c_speed["hof_command"][i]/(c_speed["handover_count"][i]+c_speed["hof_total"][i])
    c_speed["hof_ttt"][i]=c_speed["hof_ttt"][i]/(c_speed["handover_count"][i]+c_speed["hof_total"][i])
  else:
    c_speed["hof_command"][i]=0
    c_speed["hof_ttt"][i]=0
  if c_speed["hof_command"][i]!=0:
    x=(c_speed['hof_ttt'][i])/(c_speed['hof_command'][i])
  else:
    x=(c_speed["hof_ttt"][i]+ep)/ep
  a.append(x)
c_speed['alpha']=a

c_speed.to_csv("c_n310.csv", index=False)

c_ttt = pd.read_csv("/home/souvik/Documents/handover_journal/sumit roy/Data/Correlated/c_n311.csv")

c_ttt["rlf_count"]=c_ttt["rlf_count"]/(c_ttt["handover_count"]+c_ttt["rlf_count"]+c_ttt["hof_command"])


a=[]
for i in range(c_ttt.shape[0]):
  
  if c_ttt["hof_total"][i]!=0:
    c_ttt["hof_command"][i]=c_ttt["hof_command"][i]/(c_ttt["handover_count"][i]+c_ttt["hof_total"][i])
    c_ttt["hof_ttt"][i]=c_ttt["hof_ttt"][i]/(c_ttt["handover_count"][i]+c_ttt["hof_total"][i])
  else:
    c_ttt["hof_command"][i]=0
    c_ttt["hof_ttt"][i]=0
  if c_ttt["hof_command"][i]!=0:
    x=(c_ttt['hof_ttt'][i])/(c_ttt['hof_command'][i])
  else:
    x=(c_ttt["hof_ttt"][i]+ep)/ep
  a.append(x)
c_ttt['alpha']=a

c_ttt.to_csv("c_n311.csv", index=False)

d_hys = pd.read_csv("/home/souvik/Documents/handover_journal/sumit roy/Data/Deterministic/rlf_hys.csv")

d_hys["rlf_count"]=d_hys["rlf_count"]/(d_hys["handover_count"]+d_hys["rlf_count"]+d_hys["hof_command"])


a=[]
for i in range(d_hys.shape[0]):
  
  if d_hys["hof_total"][i]!=0:
    d_hys["hof_command"][i]=d_hys["hof_command"][i]/(d_hys["handover_count"][i]+d_hys["hof_total"][i])
    d_hys["hof_ttt"][i]=d_hys["hof_ttt"][i]/(d_hys["handover_count"][i]+d_hys["hof_total"][i])
  else:
    d_hys["hof_command"][i]=0
    d_hys["hof_ttt"][i]=0
  if d_hys["hof_command"][i]!=0:
    x=(d_hys['hof_ttt'][i])/(d_hys['hof_command'][i])
  else:
    x=(d_hys["hof_ttt"][i]+ep)/ep
  a.append(x)
d_hys['alpha']=a
d_hys.to_csv("d_hys.csv", index=False)

d_speed = pd.read_csv("/home/souvik/Documents/handover_journal/sumit roy/Data/Deterministic/rlf_speed.csv")

d_speed["rlf_count"]=d_speed["rlf_count"]/(d_speed["handover_count"]+d_speed["rlf_count"]+d_speed["hof_command"])


a=[]
for i in range(d_speed.shape[0]):
  
  if d_speed["hof_total"][i]!=0:
    d_speed["hof_command"][i]=d_speed["hof_command"][i]/(d_speed["handover_count"][i]+d_speed["hof_total"][i])
    d_speed["hof_ttt"][i]=d_speed["hof_ttt"][i]/(d_speed["handover_count"][i]+d_speed["hof_total"][i])
  else:
    d_speed["hof_command"][i]=0
    d_speed["hof_ttt"][i]=0
  if d_speed["hof_command"][i]!=0:
    x=(d_speed['hof_ttt'][i])/(d_speed['hof_command'][i])
  else:
    x=(d_speed["hof_ttt"][i]+ep)/ep
  a.append(x)
d_speed['alpha']=a

d_speed.to_csv("d_speed.csv", index=False)

d_ttt = pd.read_csv("/home/souvik/Documents/handover_journal/sumit roy/Data/Deterministic/rlf_ttt.csv")

d_ttt["rlf_count"]=d_ttt["rlf_count"]/(d_ttt["handover_count"]+d_ttt["rlf_count"]+d_ttt["hof_command"])


a=[]
for i in range(d_ttt.shape[0]):
  
  if d_ttt["hof_total"][i]!=0:
    d_ttt["hof_command"][i]=d_ttt["hof_command"][i]/(d_ttt["handover_count"][i]+d_ttt["hof_total"][i])
    d_ttt["hof_ttt"][i]=d_ttt["hof_ttt"][i]/(d_ttt["handover_count"][i]+d_ttt["hof_total"][i])
  else:
    d_ttt["hof_command"][i]=0
    d_ttt["hof_ttt"][i]=0
  if d_ttt["hof_command"][i]!=0:
    x=(d_ttt['hof_ttt'][i])/(d_ttt['hof_command'][i])
  else:
    x=(d_ttt["hof_ttt"][i]+ep)/ep
  a.append(x)
d_ttt['alpha']=a

d_ttt.to_csv("d_ttt.csv", index=False)


r_hys = pd.read_csv("/home/souvik/Documents/handover_journal/sumit roy/Data/Rayleigh/hys.csv")

r_hys["rlf_count"]=r_hys["rlf_count"]/(r_hys["handover_count"]+r_hys["rlf_count"]+r_hys["hof_command"])


a=[]
for i in range(r_hys.shape[0]):
  
  if r_hys["hof_total"][i]!=0:
    r_hys["hof_command"][i]=r_hys["hof_command"][i]/(r_hys["handover_count"][i]+r_hys["hof_total"][i])
    r_hys["hof_ttt"][i]=r_hys["hof_ttt"][i]/(r_hys["handover_count"][i]+r_hys["hof_total"][i])
  else:
    r_hys["hof_command"][i]=0
    r_hys["hof_ttt"][i]=0
  if r_hys["hof_command"][i]!=0:
    x=(r_hys['hof_ttt'][i])/(r_hys['hof_command'][i])
  else:
    x=(r_hys["hof_ttt"][i]+ep)/ep
  a.append(x)
r_hys['alpha']=a

r_hys.to_csv("r_hys.csv", index=False)

r_speed = pd.read_csv("/home/souvik/Documents/handover_journal/sumit roy/Data/Rayleigh/speed.csv")

r_speed["rlf_count"]=r_speed["rlf_count"]/(r_speed["handover_count"]+r_speed["rlf_count"]+r_speed["hof_command"])


a=[]
for i in range(r_speed.shape[0]):
  
  if r_speed["hof_total"][i]!=0:
    r_speed["hof_command"][i]=r_speed["hof_command"][i]/(r_speed["handover_count"][i]+r_speed["hof_total"][i])
    r_speed["hof_ttt"][i]=r_speed["hof_ttt"][i]/(r_speed["handover_count"][i]+r_speed["hof_total"][i])
  else:
    r_speed["hof_command"][i]=0
    r_speed["hof_ttt"][i]=0
  if r_speed["hof_command"][i]!=0:
    x=(r_speed['hof_ttt'][i])/(r_speed['hof_command'][i])
  else:
    x=(r_speed["hof_ttt"][i]+ep)/ep
  a.append(x)
r_speed['alpha']=a

r_speed.to_csv("r_speed.csv", index=False)

r_ttt = pd.read_csv("/home/souvik/Documents/handover_journal/sumit roy/Data/Rayleigh/ttt.csv")

r_ttt["rlf_count"]=r_ttt["rlf_count"]/(r_ttt["handover_count"]+r_ttt["rlf_count"]+r_ttt["hof_command"])


a=[]
for i in range(r_ttt.shape[0]):
  
  if r_ttt["hof_total"][i]!=0:
    r_ttt["hof_command"][i]=r_ttt["hof_command"][i]/(r_ttt["handover_count"][i]+r_ttt["hof_total"][i])
    r_ttt["hof_ttt"][i]=r_ttt["hof_ttt"][i]/(r_ttt["handover_count"][i]+r_ttt["hof_total"][i])
  else:
    r_ttt["hof_command"][i]=0
    r_ttt["hof_ttt"][i]=0
  if r_ttt["hof_command"][i]!=0:
    x=(r_ttt['hof_ttt'][i])/(r_ttt['hof_command'][i])
  else:
    x=(r_ttt["hof_ttt"][i]+ep)/ep
  a.append(x)
r_ttt['alpha']=a

r_ttt.to_csv("r_ttt.csv", index=False)
print(c_hys," ",r)




"""def hys_plot(data, fading, metric):
  # TTT and velocity are constant
  # x axis hys
  # y axis rlf_count
  plt.plot(data['hys'], data[metric])
  plt.xlabel('Hys (db)')
  plt.ylabel(metric)
  plt.title(fading +' - Hys vs '+ metric + ': TTT=256ms, velocity=20m/s')
  plt.show()

def hys_case_plot(data, fading, metric1, metric2):
  plt.plot(data['hys'], data[metric1], c='red', label=metric1, alpha=0.5)
  plt.plot(data['hys'], data[metric2], c='blue', label=metric2, alpha=0.5)
  plt.xlabel('Hys (db)')
  plt.ylabel("HoF-{case 1, case 2}")
  plt.legend()
  plt.title(fading +' - Hys vs '+ metric1 + ' and '+ metric2 + ' : TTT=256ms, velocity=20m/s')
  plt.show()

# RLF
print("RLF Count")
hys_plot(c_hys, "Correlated", metrics[0])
hys_plot(d_hys, "Deterministic", metrics[0])
hys_plot(r_hys, "Rayleigh", metrics[0])
print("\n\n")

# HoF total
print("HoF Total")
hys_plot(c_hys, "Correlated", metrics[1])
hys_plot(d_hys, "Deterministic", metrics[1])
hys_plot(r_hys, "Rayleigh", metrics[1])
print("\n\n")

# HoF case 1
print("HoF Case 1 and Case 2")
hys_case_plot(c_hys, "Correlated", metrics[2], metrics[3])
hys_case_plot(d_hys, "Deterministic", metrics[2], metrics[3])
hys_case_plot(r_hys, "Rayleigh", metrics[2], metrics[3])
print("\n\n")


def ttt_plot(data, fading, metric):
  # HYS and velocity are constant
  # x axis ttt
  # y axis rlf_count
  plt.plot(data['ttt'], data[metric])
  plt.xlabel('TTT')
  plt.ylabel(metric)
  plt.title(fading +' - TTT vs '+ metric + ': Hys=3db, velocity=20m/s')
  plt.show()

def ttt_case_plot(data, fading, metric1, metric2):
  plt.plot(data['ttt'], data[metric1], c='red', label=metric1, alpha=0.5)
  plt.plot(data['ttt'], data[metric2], c='blue', label=metric2, alpha=0.5)
  plt.xlabel('TTT')
  plt.ylabel("HoF-{case 1, case 2}")
  plt.legend()
  plt.title(fading +' - Hys vs '+ metric1 + ' and '+ metric2 + ' : TTT=256ms, velocity=20m/s')
  plt.show()

# RLF
print("RLF Count")
ttt_plot(c_ttt, "Correlated", metrics[0])
ttt_plot(d_ttt, "Deterministic", metrics[0])
ttt_plot(r_ttt, "Rayleigh", metrics[0])
print("\n\n")

# HoF total
print("HoF Total")
ttt_plot(c_ttt, "Correlated", metrics[1])
ttt_plot(d_ttt, "Deterministic", metrics[1])
ttt_plot(r_ttt, "Rayleigh", metrics[1])
print("\n\n")

# HoF case 1 and Case 2
print("HoF Case 1 and Case 2")
ttt_case_plot(c_ttt, "Correlated", metrics[2], metrics[3])
ttt_case_plot(d_ttt, "Deterministic", metrics[2], metrics[3])
ttt_case_plot(r_ttt, "Rayleigh", metrics[2], metrics[3])
print("\n\n")




def velocity_plot(data, fading, metric):
  # HYS and TTT are constant
  # x axis velocity
  # y axis rlf_count
  unique_ttt = data['ttt'].unique()
  num_rows = (len(unique_ttt) + 3) // 2
  num_cols = min(len(unique_ttt), 4)
  fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 4*num_rows))
  axes = axes.flatten()

  for i, ttt in enumerate(unique_ttt):
    df_hys = data[data["ttt"] == ttt]
    ax = axes[i]
    ax.plot(df_hys["speed"], df_hys[metric])
    ax.set_xlabel("velocity(m/s)")
    ax.set_ylabel(metric)
    ax.set_title(fading +' - Velocity vs '+ metric + ': Hys=3db, TTT='+str(ttt))

  for i in range(len(unique_ttt), num_rows * num_cols):
    fig.delaxes(axes[i])

  plt.tight_layout()
  plt.show()

# RLF
print("RLF Count")
velocity_plot(c_speed, "Correlated", metrics[0])
velocity_plot(d_speed, "Deterministic", metrics[0])
velocity_plot(r_speed, "Rayleigh", metrics[0])
print("\n\n")

# HoF total
print("HoF Total")
velocity_plot(c_speed, "Correlated", metrics[1])
velocity_plot(d_speed, "Deterministic", metrics[1])
velocity_plot(r_speed, "Rayleigh", metrics[1])
print("\n\n")





def velocity_case_plot(data, fading, metric1, metric2):
  # HYS and TTT are constant
  # x axis velocity
  # y axis rlf_count
  unique_ttt = data['ttt'].unique()
  num_rows = (len(unique_ttt) + 3) // 2
  num_cols = min(len(unique_ttt), 4)
  fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 4*num_rows))
  axes = axes.flatten()

  for i, ttt in enumerate(unique_ttt):
    df_hys = data[data["ttt"] == ttt]
    ax = axes[i]
    ax.plot(df_hys["speed"], df_hys[metric1], c='red', label=metric1, alpha=0.5)
    ax.plot(df_hys["speed"], df_hys[metric2], c='blue', label=metric1, alpha=0.5)
    ax.set_xlabel("velocity(m/s)")
    ax.set_ylabel("HoF-{case 1, case 2}")
    ax.set_title(fading +' - Velocity vs '+ metric1 + ' and '+ metric2 + ': Hys=3db, TTT='+str(ttt))

  for i in range(len(unique_ttt), num_rows * num_cols):
    fig.delaxes(axes[i])

  plt.tight_layout()
  plt.show()


# HoF case 1
print("HoF Case 1 and Case 2")
velocity_case_plot(c_speed, "Correlated", metrics[2], metrics[3])
velocity_case_plot(d_speed, "Deterministic", metrics[2], metrics[3])
velocity_case_plot(r_speed, "Rayleigh", metrics[2], metrics[3])
print("\n\n")"""

