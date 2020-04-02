import numpy as np
import matplotlib.pyplot as plt
import statistics as st
#Imports: numpy does the histograms, pyplot does plots, and statistics helps 
#with chi square analysis

#Variables of the problem

sqrt = np.sqrt
#for easier square roots
random = np.random.random
#random() will give a random integer between 0 and 1
X = 8.9 #cm
#characteristic length of travel in aluminum
S = 5.09 #MeV/cm
#mesurement of the energy the electron loses from radiation
tp = 0.9525 #cm
#thickness of a plate of aluminum
tg = 0.635 #cm
#thickness of the gaps between the plates
TRIALS = 10000
#used twice. once for the amount of electrons generated for one Monte Carlo (MC) 
#simulation. another for the amount of MC simulations taken for each
#mass.
RADIUS = 7.62 #cm
#Radius of the chamber

#experimental data. This also shows how histograms are formatted
experiment = [[4,7,13,15,4],[3,4,5,6,7]]
#A histogram is a tuple, the first value in the tuple is a list of the number 
#of counts (the y axis) while the second value is the bins. This variable is
#a list, not a tuple, and the second list does not contain both ends of the bin
#but the integer values that are measured. We will format the histograms to look
#like this for analysis


#This example is what was used for the initial presentation
def piPlot(N=100):
    Xin = []
    Yin = []
    Xout = []
    Yout = []
    count = 0
    
    for i in range(N):
        x = random()
        y = random()
        
        if(sqrt(x**2 + y**2)<1):
            count = count + 1
            Xin = Xin + [x]
            Yin = Yin + [y]
        else:
            Xout = Xout + [x]
            Yout = Yout + [y]
            
    #plt.scatter(Xout,Yout,color = 'red')
    #plt.scatter(Xin,Yin,color = 'blue')
    return 4*count/N

#These two were used to demonstrate the central limit theorem(though we might not use it)
def rollTwoDice(N=100):
    results = [(int)(6*random()+1)+(int)(6*random()+1) for i in range(N)]
    sevens = 0
    for result in results:
        if result==7:
            sevens = sevens + 1
    return sevens

def CLT(N=100):
    results = [rollTwoDice(N) for i in range(N)]
    plt.hist(results)

#This function contains the unnormalized distribution of electron energy
#Input are the mass of the muon and the energy of the electron, and output
#is the relative probability of generating this electron.
def electronDist(E,m):
    if(E>m/2):
        return 0
    return (m*E**2) * (3 - 4*E/m)


#This is also for demonstration. It simply plots the electron distribution
def plotElectronDist():
    N=TRIALS
    x = [(1)*i*3/(4*N) for i in range(N+1)]
    y = [electronDist(x[i],1) for i in range(len(x))]
    for i in range(len(y)):
        if(y[i] < 0):
            x =x[0:i]
            y = y[0:i]
            break
    plt.plot(x,y)
    plt.xlabel("$E_e (m_u)c^2$")
    plt.ylabel("Relative Probability $P(E_e)$")
    
    
#Ok this is the first complicated function to understand. First because it 
def generateE(m):
    x = random()*m/2
    y = random()*electronDist(m/2,m)
    if(electronDist(x,m)>y):
        return x
    else:
        return generateE(m)
    
def generateR(R):
    x = random()
    y = random()
    if(x>y):
        return x*R
    else:
        return generateR(R)
    
def MC(m,plot=False):
    N=TRIALS
    data = []
    for i in range(N):
        E = generateE(m)
        z = random()*tp
        r = generateR(RADIUS/2)
        theta = random()*np.pi/6
        phi = random()*2*np.pi
        ns = MCunit(E,r,theta,phi,z)
        data = data + [ns]
    if(plot):
        plt.scatter(experiment[1],experiment[0],color='black',zorder = 2,label = "Experimental data")
        plt.hist(data,bins = 1+max(data)-min(data),weights = [43/TRIALS for i in range(len(data))],zorder = 1,range = (min(data) - 0.5,max(data)+0.5),label = "Simulation data $m_\mu c^2 = " + str(m) + "MeV$")
        plt.xlabel("$n_s$")
        plt.ylabel("Counts")
        plt.legend()
    return data
    
def MCunit(E,r,theta,phi,z):
    l = X*np.log(1 + E/(X*S))
    lesc = (np.sqrt((r*np.cos(phi))**2 + (RADIUS ** 2 - r ** 2)) - r*np.cos(phi))*tp/(np.sin(theta)*(tp+tg))
    if(l>lesc):
        l=lesc
    ns = 1+((int)((l*np.cos(theta)-z)/tp))
    return ns

def getIndex(data,val):
    indicies = [(int)(data[1][i]) for i in range(len(data[1]))]
    
    if(val in indicies):
        return data[0][data[1].index(val)]
    else:
        return 0

def tryM(m):    
    Ss = []
    for n in range(10):
        data = MC(m)
        theoretical = np.histogram(data,bins = 1+max(data)-min(data),weights = [43/TRIALS for i in range(len(data))],range = (min(data) - 0.5,max(data)+0.5))
        
        theoretical = [theoretical[0].tolist(),theoretical[1].tolist()]
        theoretical[1].remove(max(theoretical[1]))
        
        theoretical[1] = [theoretical[1][i] + 0.5 for i in range(len(theoretical[1]))]
        
        maximum = max(theoretical[1] + experiment[1])
        minimum = min(theoretical[1] + experiment[1])
        S=0
        
        for i in range((int)(minimum),(int)(maximum+1)):
            theoryvalue = getIndex(theoretical,i)
            experimentvalue = getIndex(experiment,i)
            
            error = 1
            if(experimentvalue != 0):
                error = 1#np.sqrt(experimentvalue)
                
                S = S + ((theoryvalue - experimentvalue)/error) **2
        Ss = Ss + [S]
        
    Avg = sum(Ss)/len(Ss)
    stdev = st.stdev(Ss)
           
    return Avg,stdev,Ss
    
def go():
    N=16
    x = [95 + 20*i/N for i in range(N+1)]
    simulation = [tryM(x[i]) for i in range(len(x))]
    chis = [simulation[i][0] for i in range(len(x))]
    errs = [simulation[i][1] for i in range(len(x))]
    plt.errorbar(x,chis,errs)
    plt.xlabel("$m_\mu c^2$ (MeV)")
    plt.ylabel("S")