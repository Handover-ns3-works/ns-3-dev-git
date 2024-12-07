import numpy as np
from scipy import stats
from scipy.stats import rice
import math
import cmath

# Function to compute the 95% confidence interval
def confidence_interval(data, confidence=95):
    data_array = np.array(data)
    mean = np.mean(data_array)
    n = len(data_array)
    std_err = stats.sem(data_array)  # Standard error of the mean
    if confidence==95:
      Z=1.960
    elif confidence==99:
      Z=2.576
    else:
      print("wrong confidence level")
      exit()
    margin_of_error = Z * std_err/math.sqrt(n)
    return mean, mean - margin_of_error, mean + margin_of_error, margin_of_error

class Queue:
    def __init__(self):
        self.queue = np.array([])  # Initialize an empty array to serve as the queue

    def enqueue(self, element):
        self.queue = np.append(self.queue, element)  # Add the element to the end (rear) of the queue

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Dequeue from an empty queue")
        element = self.queue[0]  # Get the first element (front)
        self.queue = np.delete(self.queue, 0)  # Remove the first element
        return element

    def peek(self):
        if self.is_empty():
            raise IndexError("Peek from an empty queue")
        return self.queue[0]  # Return the first element without removing it

    def is_empty(self):
        return self.queue.size == 0  # Return True if the queue is empty

    def size(self):
        return self.queue.size  # Return the size of the queue
    
def dist(a,b):
  return math.sqrt(((a[0]-b[0])**2)+(a[1]-b[1])**2)

def RSRP_to_RSRQ(RSRP_list):
  RSSI=sum(RSRP_list)
  RSRQ_list=[]
  for power in RSRP_list:
    RSRQ_list.append(power/RSSI)
  return RSRQ_list


class BS:
  def __init__(self,location,type,freq,T_power,corr=True):
    self.T_power=T_power
    self.noise= 6.309573444801943e-17
    self.location=location
    self.type=type # 0 for LTE, 1 for NR -1 for friss,
    self.freq=freq
    self.shadowing=np.random.standard_normal()*4.0
    self.corr=corr
  def pathloss(self,d):
    pl=0
    if self.type==0:
      f = self.freq/1e6  # Carrier frequency in MHz
      Dhb = 15  # Base station antenna height in meters
      R = d / 1000
      L = 120.9 + 37.6 * math.log10(R)
      pathloss_macro = L + math.log10(f)
      MCL = 70  #minimum coupling loss
      TX_PWR = self.T_power #30  #transmitted signal power
      G_TX = 3  #transmitter gain
      G_RX = 5  #receiver gain
      h_BS = 25 #antenna height at the BS in meters (last column, pg 24) <--------------------(recheck)
      h_UT_min = 1.5 #min effective antenna height
      h_UT_max = 22.5 #max effective antenna height
      pathloss=max(pathloss_macro - G_TX - G_RX, MCL)
      if self.corr:
        ## Shadowing part
        norm=np.random.standard_normal()
        d_corr=37
        BP_distance=2*math.pi*h_BS*h_UT_max*self.freq/3e8
        std_shadow=0
        if d<BP_distance:
          std_shadow=4.0
        else:
          std_shadow=6.0
        correlation=math.exp(-d/d_corr)

        ## update shadowing
        self.shadowing=correlation*self.shadowing+math.sqrt(1-correlation**2)*np.random.standard_normal()*std_shadow
        ## update pathloss
        pathloss+=self.shadowing
      pl = 10**(pathloss / 10)
      return pl
    elif self.type==1:
      fc = self.freq/1e9 #28e9 / 1e9  #center frequency
      c = 3.0e8 #propagation velocity
      h_BS = 25 #antenna height at the BS in meters (last column, pg 24) <--------------------(recheck)
      h_UT_min = 1.5 #min effective antenna height
      h_UT_max = 22.5 #max effective antenna height
      d_BP = 4 * h_BS * h_UT_max * fc / c #Breakpoint
      #UMALOS
      PL_UMA_LOS = 28 + 22 * math.log10(d) + 20 * math.log10(fc)
      # UMANLOS
      PL1 = 28 + 22 * math.log10(d) + 20 * math.log10(fc)
      PL2 = 28 + 40 * math.log10(d) + 20 * math.log10(fc) - 9 * math.log10(d_BP**2 + (h_BS - h_UT_max)**2)
      PL_UMA_NLOS = max(PL_UMA_LOS, PL2)
      if 0 <= d <= d_BP: ## replaced 10 with 0
          pathloss = PL_UMA_LOS
      elif d_BP <= d <= 5000:  # 5 km = 5000 m
          pathloss = PL_UMA_NLOS
      else:
          print("Dist out of range ",d)
          raise ValueError("Dist out of range")
      if self.corr:
        ## Shadowing part
        norm=np.random.standard_normal()
        d_corr=37
        BP_distance=2*math.pi*h_BS*h_UT_max*self.freq/3e8
        std_shadow=0
        if d<BP_distance:
          std_shadow=4.0
        else:
          std_shadow=6.0
        correlation=math.exp(-d/d_corr)

        ## update shadowing
        self.shadowing=correlation*self.shadowing+math.sqrt(1-correlation**2)*np.random.standard_normal()*std_shadow
        ## update pathloss
        pathloss+=self.shadowing


      pl = 10**(pathloss / 10)
      return pl

    elif self.type==-1:
      lamda=3e8/self.freq
      pl=(lamda/math.pi*4*d)**2
      return pl
    else:
      print("wrong choice of BS")
      raise ValueError("wrong choice of BS")
      exit()


## this class makes one object for every UE BS pair

class utility:
  def __init__(self,BS,UE):
    self.BS=BS
    self.UE=UE
    self.RSRP=Queue()
    self.fillQ()
    self.M=0
    self.F=0

  def fillQ(self):
    for i in range(5):
      self.RSRP.enqueue(0)

  def rice_gain(self):
    device=self.UE
    BS=self.BS
    gain=0
    d=dist(device.location,BS.location)
    K_dB=4
    K=10**(K_dB/10)
    mu=math.sqrt(K/((K+1)))
    sigma=math.sqrt(1/((K+1)))
    shape=math.sqrt(2*K)
    h=rice.rvs(shape,size=1)[0]
    #h=complex(sigma*np.random.standard_normal()+mu,sigma*np.random.standard_normal()+mu)
    pl=BS.pathloss(d)
    gain=h/math.sqrt(pl)
    return gain

  def ray_gain(self):
    device=self.UE
    BS=self.BS
    gain=0
    d=dist(device.location,BS.location)
    pl=BS.pathloss(d)
    h=complex(np.random.standard_normal(),np.random.standard_normal())
    gain=h/math.sqrt(pl)
    return gain

  def RSRP_ray(self):
    device=self.UE
    BS=self.BS
    TX_power=BS.T_power
    d=dist(device.location,BS.location)
    pl=BS.pathloss(d)
    gain=self.ray_gain()
    return (abs(gain)**2)*TX_power/12

  def RSRP_rice(self):
    device=self.UE
    BS=self.BS
    TX_power=BS.T_power
    d=dist(device.location,BS.location)
    pl=BS.pathloss(d)
    gain=self.rice_gain()
    return (abs(gain)**2)*TX_power/12

  def filterL1(self,RSRP_value):
    self.RSRP.dequeue()
    self.RSRP.enqueue(RSRP_value)
    M=0
    for i in range(self.RSRP.size()):
      M+=self.RSRP.queue[i]
    self.M=M/5
    return M/5

  def filterL3(self,M,TTT):
    if TTT>=0 and TTT<80:
      a=pow(0.5,0)
    elif TTT>=80 and TTT<480:
      a=pow(0.5,1/4)
    else:
      a=pow(0.5,1)

    self.F=(1-a)*self.F+a*10*math.log10(M)
    return 10**(self.F/10)




class RLF:
  def __init__(self,base,step_count,T=1000,N0=6,N1=2):
    self.T310=0
    self.n310=0
    self.n311=0
    self.T=T
    self.N0=N0
    self.N1=N1
    self.timer=False
    self.Qout=10**(-5/10) #dB
    self.Qin=10**(-3.5/10) #dB
    self.noise= 6.309573444801943e-17
    self.base=base
    self.step=step_count

  def RLF_status(self,RSRP_list,index):
    ## interference calculator::
    interfere=0
    it=0
    while(it<len(RSRP_list)):
      #print("in loop ",index," ",it," ",len(self.base))
      if self.base[index].type==self.base[it].type and index !=it:
        interfere+=RSRP_list[it]
      it+=1

    SINR=RSRP_list[index]/(self.noise+interfere)
    #print("When timer becomes true: ",SINR,"Q out= ",self.Qout," inter=",interfere,"power= ",RSRP_list[index], "index ",index)
    if SINR<self.Qout and self.timer==False:
      self.n310+=1
      if self.n310==self.N0:
        self.timer=True
        self.n310=0
    if self.timer==True:
      print("When timer becomes true: ",SINR,"Q out= ",self.Qout," inter=",interfere,"power= ",RSRP_list[index])
      self.T310+=self.step
      if self.T310==self.T:
        self.timer=False
        self.n310=0
        self.T310=0
        self.n311=0
        return True
      if SINR>self.Qin:
        self.n311+=1
        if self.n311==self.N1:
          print("When timer becomes False: ",SINR,"Q out= ",self.Qout," inter=",interfere,"power= ",RSRP_list[index])
          self.timer=False
          self.n311=0
          self.T310=0
          return False
      else:
        return False

    else:
      return False
  def reset(self):
    self.T310=0
    self.n310=0
    self.n311=0
    self.timer=False






class Handover:
  def __init__(self,type,hyst,ttt,A2,A4,SP):
    self.type=type # 0 for A3 1 for A1
    self.HYS=hyst ### in watts
    self.TTT=ttt
    self.A2=A2 ## in watts values are -110 or -120 dBm
    self.A4=A4
    self.HO1=False
    self.HO2=False
    self.SP=SP
    self.ttcounter=0

  def A3_HO(self,RSRP_list,attachment,target):
    ex_RSRP_list=RSRP_list[:0]+RSRP_list[0+1:]
    if max(ex_RSRP_list)/RSRP_list[0]>self.HYS:  ### attachment
      self.HO1=True
      target=RSRP_list.index(max(ex_RSRP_list))
    if self.HO1==True:

      if self.ttcounter>=self.TTT:
        self.HO1=False
        self.HO2=True
        self.ttcounter=0
        return target,attachment,self.HO1,self.HO2
      if  max(ex_RSRP_list)/RSRP_list[0]<=self.HYS:
        print("violation")
        self.HO1=False
        self.HO2=False
        self.ttcounter=0
        target=-1
        return target,attachment,self.HO1,self.HO2
      self.ttcounter+=self.SP


    return target,attachment,self.HO1,self.HO2

  def A2A4HO(self,RSRP_list,attachment,target):
    RSRQ_list=RSRP_to_RSRQ(RSRP_list)
    ex_RSRQ_list=RSRQ_list[:attachment]+RSRQ_list[attachment+1:]
    if RSRQ_list[attachment]<self.A2 and self.HO1==False:
      self.HO1=True
      target=target #RSRP_list.index(max(ex_RSRP_list))
      attachemnt=attachemnt


    if self.HO1==True:

      if  RSRQ_list[attachment]>self.A2 and self.HO2==False:
        self.HO1=False
        self.HO2=False
        attachment=attachment
        target=-1
        return target,attachment,self.HO1,self.HO2
      if max(ex_RSRQ_list)>=self.A4:
        self.HO1=False
        self.HO2=True
        target=RSRQ_list.index(max(ex_RSRQ_list))

        return target,attachment,self.HO1,self.HO2
      self.ttcounter+=self.SP


    return target,attachment,self.HO1,self.HO2


    pass

  def reset(self):
    self.HO1=False
    self.HO2=False
    self.ttcounter=0





class UE:
  def __init__(self, Handover,RLF,location,velocity,step_count):
    self.handover=Handover
    self.RLF=RLF
    self.location=location
    self.attachment=0
    self.prep_list=[]
    self.target=-1
    self.time_count=0
    self.step_count=step_count
    self.velocity=velocity
    self.flag=-1


  def update_HO (self,RSRP_list,attachment,target,typeofho):
    if typeofho==0:
      t,a,H1,H2=self.handover.A3_HO(RSRP_list,attachment,target)
    else:
      t,a,H1,H2=self.handover.A2A4HO(RSRP_list,attachment,target)
    return t,a,H1,H2
  def update_RLF (self,RSRP_list,attachment):
    return self.RLF.RLF_status(RSRP_list,attachment)

  def attachment_status(self,RSRP_list,L3RSRP_list,typeofho):
    RLF_stat=self.update_RLF(RSRP_list,self.attachment)
    if self.time_count%self.handover.SP==0 and self.handover.HO2==False:
      #print("before the update call ",self.target,self.attachment)
      self.target,self.attachment,H1,H2=self.update_HO(L3RSRP_list,self.attachment,self.target,typeofho) #### changed to only rsrp list from l3
      if self.handover.HO1==True:
        print(" time for trigger ",self.time_count," location ",self.time_count*self.velocity/1000)
      #print(self.target," ",self.attachment," ",self.location)

    if self.handover.HO2==True and RLF_stat==True:
      self.flag=-2
      self.handover.reset()
      self.RLF.reset()
      return 2
    if self.handover.HO1==False and RLF_stat==True and self.handover.HO2==False:
      self.flag=-2
      self.RLF.reset()
      return 1

    if self.handover.HO1==True and RLF_stat==True:
      self.flag=-2
      self.RLF.reset()
      self.handover.reset()
      return 2

    """if self.handover.HO2==False and RLF_stat==True:
      self.flag=-2
      self.RLF.reset()
      return 0"""

    if self.time_count%(self.handover.SP+self.step_count)==0 and self.handover.HO2==True:
      if self.RLF.timer==True:
        self.flag=-2
        self.RLF.reset()
        self.handover.reset()
        return 3
      else:
        self.flag=-2
        self.attachment=self.target
        self.target=-1
        self.handover.reset()
        self.RLF.reset()
        return 0
    return self.flag

  def update_location(self,loc):
    self.location=loc
  def update_time(self):
    self.time_count+=self.step_count






def horizontal_motion(start_loc,end_loc,velocity,time_step):
  if start_loc[1]==end_loc[1]:
    locations=[]
    locations.append(start_loc)
    if start_loc[0]<end_loc[0]:
      pass
    else:
      velocity=-velocity
    while locations[-1][0]<end_loc[0]:
      locations.append([locations[-1][0]+velocity*time_step,locations[-1][1]])
    return locations
  else:
    print("wrong endpoints")

def horizontal_motion_time(start_loc,velocity,time_step,time):
  locations=[]
  locations.append(start_loc)
  iter=int(time/time_step)
  for i in range(iter):
    locations.append([locations[-1][0]+velocity*time_step,locations[-1][1]])
  return locations


import csv
import random



final_data=[]
iterations=1
motion_iterations=1
velocity=20 #m/s
time_step=0.001 #seconds ## 10 milliseconds
step_count=int(time_step*1000) ### this gives the actual number of milliseconds being passed at each iteration example: 0.01*1000=10 ms

hyst=[]
for i in range(3,4):
  hyst.append(i*1)
ttt=[4600]#,4800,5000,5120]#320,480,512,640,1024,1280,2560,5120]#[0,40,64,80,100,128,160,256] #



for h in hyst:
  for trigger in ttt:
    rlf_count=[] ### to store the probility of rlf for a thousand iterations
    hof1_count=[]
    hof2_count=[]
    ho_cout=[]
    Base_stations=[BS((0,0),0,2.12e9,39.81,False),BS((1000,0),0,2.12e9,39.81,False)]#,BS((100,50),1,28e9,39.81,True),BS((100,-50),1,28e9,39.81,True)] #### Base stations defined
    radio_stat=RLF(Base_stations,step_count,1000,1,2)
    HO=Handover(0,10**(h/10),trigger,0,0,40)

   # for i in range(Number_of_UEs):
   #   radio_stat.append(RLF(1000,6,2))
   #   HO.append(Handover(0,10**(h/10),trigger,0,40))

    for iter in range(iterations):


      Rc=0 ### counting the number of RLFs over 100 runs of UE
      H1c=0
      H2c=0
      hoc=0
      noc=0

      for miter in range(motion_iterations):
        RSRP_list=[]
        L3RSRP_list=[]

        for j in range(len(Base_stations)):
          RSRP_list.append(0.0)
          L3RSRP_list.append(0.0)

        y=50#random.randint(20, 30)
        locations=horizontal_motion((500,y),(2500,y),velocity,time_step)
        #print(len(locations))   ##### Locations and motion defined
        User=UE(HO,radio_stat,(0,y),velocity,step_count)

        #for i in range(Number_of_UEs):
        #  User.append(UE(HO[i],radio_stat[i],(0,y),velocity))

        Utility=[]
        #for i in range(len(User)):
        #  a=[]

        for j in range(len(Base_stations)):
          Utility.append(utility(Base_stations[j],User))

        #Utility.append(a)

        for loc in locations:
          #for i in range(len(User)):
          User.update_location(loc)
          User.update_time()
          #compute the RSRPS
          for i in range(len(Base_stations)):
            RSRP_list[i]=Utility[i].RSRP_ray()
            M=Utility[i].filterL1(RSRP_list[i])
            L3RSRP_list[i]=Utility[i].filterL3(M,trigger)
          result=User.attachment_status(RSRP_list,L3RSRP_list,0)

          ### the counting part
          if result>=0:
            if result==0:
              hoc+=1
              print(" Success HO ",User.attachment)
              break
            elif result==1:
              Rc+=1
              print("RLF")
              break
            elif result==2:
              H1c+=1
              Rc+=1
              print(User.target)
              break
            elif result==3:
              H2c+=1
              #print(User.target," ",User.attachment)
              break
          else:
            if result==-1 and loc==locations[-1]:
              noc+=1

        #print("outside loc iteration")

      rlf_count.append(Rc/(motion_iterations))
      hof1_count.append(H1c/(motion_iterations))
      hof2_count.append(H2c/(motion_iterations))
      ho_cout.append(hoc+noc/(motion_iterations))
      print(hoc," ",noc)

    #print("outside the iter iteration")
    mean1, lb1,ub1, margin_of_error1=confidence_interval(rlf_count)
    mean2, lb2,ub2, margin_of_error2=confidence_interval(hof1_count)
    mean3, lb3,ub3, margin_of_error3=confidence_interval(hof2_count)
    mean0, lb0,ub0, margin_of_error0=confidence_interval(ho_cout)
    final_data.append([h,trigger,velocity,mean1,mean2,mean3,mean0,margin_of_error1,margin_of_error2,margin_of_error3])

  print("outside the ttt iteration")
print("outside the hyst iteration")










head=['hyst','ttt','vel','rlf','hof1','hof2','ho','cirlf','cihof1','cihof2']
with open("/content/drive/My Drive/ttt_data.csv",'w') as csvfile:
	csvwriter = csv.writer(csvfile)
	csvwriter.writerow(head)
	csvwriter.writerows(final_data)

