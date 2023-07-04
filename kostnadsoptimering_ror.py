import re
import xml.etree.ElementTree as ET
import math
import fluids
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame


#predifined regex filter, finds anything starting with atleast one or more numbers then potentially a . and then potentially more numbers
valuefilter = re.compile("[0-9]+.?[0-9]*");

#function to filter text using the compiled regex
def filter(content):
    new = valuefilter.findall(content);
    print(new);
    new = float(new[0]); #everything will be numbers but some might be integers however its not worth the time to filter out
    return new;

#open config file
with open("setup.cfg","r") as setup_config:
    print("Setup");
    content = setup_config.readlines();
    setup_config.close();
    print("success");
    
#filter config text
q = filter(content[0]);
den = filter(content[1]);
dyn_vis = filter(content[2]);
min_v = filter(content[3]);
max_v = filter(content[4]);
pump_eff = filter(content[5]);
pot_head = filter(content[6]);
diff_head = filter(content[7]);
yearly_h = filter(content[8]);
en_cost = filter(content[9]);
sys_length = filter(content[10]);
lifespan = filter(content[11]);
scaff = filter(content[12]);
sal_w = filter(content[13]);
sal_i = filter(content[14]);
sal_a = filter(content[15]);
speed_w = filter(content[16]);
spots_w = filter(content[17]);
thic_m = filter(content[18]);
thic_i = filter(content[19]);
time_i = filter(content[20]);
time_a = filter(content[21]);
price_i = filter(content[22]);
price_a = filter(content[23]);
work_eff = filter(content[24]);
bends = filter(content[25]);
rough = filter(content[26]);




#Find material specific data from xmlfile
tree = ET.parse('ror_dim.xml')
root = tree.getroot()

#arrays for storing data from all the materials
dim = []
mcost = []
vel = []
con_cost = []
total_cost = []
yearly_cost = []
energy_cost = []
functional = []

     
def velocity(d):
    return (1.273*q)/(d**2);

def headloss(f,dim,v):
    hl = f*sys_length*(v**2)/(dim*2*9.81);
    return hl;
    
#friction coeffecient for laminar flow
def laminar(re):
    f = 64/re;
    return f;

def reynolds_number(v):
    rey = den*v*sys_length/dyn_vis;
    return rey;
    
#calculate friction coeffecient for turbulent flow using some fancy method
def Mileikovskyi(re,rr): 
    A0 = -0.79638*math.log((rr/8.298)+(7.3357/re));
    A1 = re*rr+9.3120665*A0;
    f=((8.128943+A1)/(8.128943*A0-0.86859209*A1*math.log(A1/(3.7099535*re))))**2;
    return f;

#use fluids to calculate headloss from bends
def bend_calc(d,f,v):
    K = fluids.fittings.entrance_sharp();
    for n in range(math.floor(bends)):
        K += fluids.fittings.bend_rounded(Di=d,angle=90,fd=f);
    K += fluids.fittings.exit_normal();
    loss = fluids.core.head_from_K(K=K,V=v)
    return loss;

#yearly energy cost
def calc_en_cost(head):
    return den*q*head*en_cost*yearly_h/(3600000*pump_eff)


def calc_con_cost(mcost,d):
    con_cost = scaff;
    con_cost += mcost * sys_length
    con_cost += (d+2*thic_m)*math.pi*spots_w*speed_w*sal_w/work_eff
    con_cost += time_i*sal_i/work_eff + (d+2*thic_m+2*thic_i)*math.pi*sys_length*price_i
    con_cost += time_a*sal_a/work_eff + (d+2*thic_m+2*thic_i)*math.pi*sys_length*price_a
    
    
    return con_cost


#the children are the different dimensions
for child in root:
    dim.append(float(child.find('dim').text))
    mcost.append(float(child.find('mcost').text))


n= 0; #keeps track of which dim we are on
min_cost= None;
min_dim = None;

#loop through all the dims
for dimension in dim:

    #vel
    v = velocity(dim[n]);
    vel.append(v);
    if v<= max_v and v>= min_v:
        functional.append(True);
    else:
        functional.append(False);

    #head
    re = reynolds_number(v);
    print(re)
    if re >= 2300:
        f = Mileikovskyi(re,rough/dim[n]);
    else:
        f = laminar(re);
    print("friction coefficient: " + str(f));

    head_bend = bend_calc(dim[n],f,v);
    print("loss to bends[m]: " + str(head_bend));

   
    print("loss to friction [m]: " + str(headloss(f,dim[n],v)));
    h_loss = diff_head+headloss(f,dim[n],v)+head_bend; #real world height diff + friction loss + bend loss
    print(functional[n]);
    if h_loss > pot_head and functional[n] != False: #if the loss is greater than pump head then invalidate it if its not already invalidated
        functional[n] = False;
        
    #we save all costs in a list so it can potentially be exported to something like excel in the future 
    yearly_cost.append(calc_en_cost(h_loss));
    con_cost.append(calc_con_cost(mcost[n],dim[n]));
    energy_cost.append(yearly_cost[n]*lifespan);
    total_cost.append(energy_cost[n]+con_cost[n]);
    
    print("Total cost for "  + str(dim[n]) + ": " + str(total_cost[n]));
    
    if functional[n] == True and (min_cost == None or total_cost[n] < min_cost):
        min_cost = total_cost[n];
        min_dim = dim[n];

    n+=1;
    
print("The economical diameter is: " + str(1000*min_dim) + "mm with a total cost of: " + str(math.floor(min_cost)) + "kr");



col = [];
for valid in functional:
    if valid:
        col.append('green');
    else:
        col.append('red');

fig,ax = plt.subplots();
dim_txt = [];
for val in dim:
    dim_txt.append(str(math.floor(val*1000)) +"mm")
ax.bar(dim_txt,total_cost, color=col)       
plt.show()

df = DataFrame({'Dimmension' : dim_txt, 'Totalcost' : total_cost, 'functional' : functional, 'con cost' : con_cost, 'en cost' : energy_cost})
df.to_excel('ror_dim.xlsx', sheet_name='sheet1', index=False)

