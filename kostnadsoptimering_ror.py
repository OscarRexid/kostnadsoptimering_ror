import re
import xml.etree.ElementTree as ET
import math
import fluids
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame
import tkinter as tk


class calculations:
    def velocity(d,q):
        return (q/3600)/(((d/2)**2)*math.pi);
    
    def headloss(f,dim,v):
        hl = f*(sys_length/dim)*2*den*(v**2);
        return hl;
        
    #friction coeffecient for laminar flow
    def laminar(re):
        f = 64/re;
        return f;

    def reynolds_number(v,den,sys_length,dyn_vis):
        rey = den*v*sys_length/dyn_vis;
        return rey;
        
    #calculate friction coeffecient for turbulent flow using some fancy method
    def Mileikovskyi(re,rr): 
        A0 = -0.79638*math.log((rr/8.298)+(7.3357/re));
        A1 = re*rr+9.3120665*A0;
        f=((8.128943+A1)/(8.128943*A0-0.86859209*A1*math.log(A1/(3.7099535*re))))**2;
        return f;

    #use fluids to calculate headloss from bends
    def bend_calc(d,f,v,sys_length,bends,den):
        K = fluids.fittings.entrance_sharp();
        for n in range(math.floor(bends)):
            K += fluids.fittings.bend_rounded(Di=d,angle=90,fd=f);
        K += fluids.fittings.exit_normal();
        K += fluids.core.K_from_f(fd=f, L=sys_length, D=d)
        loss = fluids.core.dP_from_K(K=K,rho=den,V=v);
        return loss;

    #yearly energy cost
    def calc_en_cost(head,q,pump_eff,en_cost,yearly_h):
        kw= q*head/(3599000*pump_eff);
        print("kw: " + str(kw));
        return en_cost*kw*yearly_h;


    def calc_con_cost(mcost,d,sys_length,spots_w,speed_w,sal_w,sal_i,sal_a,time_i,time_a,price_i,price_a,work_eff,scaff,thic_m,thic_i):
        con_cost = scaff;
        con_cost += mcost * sys_length;
        con_cost += (d+2*thic_m)*math.pi*spots_w*speed_w*sal_w/work_eff;
        con_cost += time_i*sal_i/work_eff + (d+2*thic_m+2*thic_i)*math.pi*sys_length*price_i;
        con_cost += time_a*sal_a/work_eff + (d+2*thic_m+2*thic_i)*math.pi*sys_length*price_a;
        
        print("con cost: " + str(con_cost))
        return con_cost

 


class OutputFrame(tk.Frame):
    def __init__(self,master):
        super().__init__();
        self.master = master;
        self.columnconfigure(0, weight=1);
        self.columnconfigure(1, weight=3);
        self.__create_widgets();
        
    def __create_widgets(self):
        self.resultbutton = tk.Button(self, text="Generate Results",width=30, height=5, command = self.result_button_click);
        self.resultbutton.grid(column=0, row=0, padx=5, pady=10);
        
        self.warninglabel = tk.Label(self, text="e");
        self.warninglabel.grid(column=0, row=1, padx=5, pady=10);
        
        
    def result_button_click(self):
        failures = 0;
        for data in self.master.shared_data:
            if self.master.shared_data[data].get():
                print("success");
            else:
                failures +=1;
                print("Missing: " + data);
                self.master.shared_data[data].set(0)
        if failures > 30:
             self.warninglabel['text'] = "Failure, missing input";
             self.warninglabel['fg'] = "red";
        else:
           self.master.calculate()
            
class InputFrame(tk.Frame):
    def __init__(self,master):
        super().__init__();
        
        self.columnconfigure(0, weight=1);
        self.columnconfigure(1, weight=3);
        self.columnconfigure(2, weight=5);
        self.__create_widgets();
        
    def __create_widgets(self):
        
        ##Column 0
        
        flowlabel = tk.Label(self, text='Flöde [m³/h]');
        flowlabel.grid(column=0,row=0,sticky=tk.W,padx=5,pady=(10,0));
        flowentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["flowvar"]);
        flowentry.grid(column=0,row=1,sticky=tk.W,padx=5,pady=(5,10));
        
        label1 = tk.Label(self, text='Densitet [kg/m³]');
        label1.grid(column=0,row=2,sticky=tk.W,padx=5,pady=(10,0));
        entry1 = tk.Entry(self, width=25, textvariable=self.master.shared_data["denvar"]);
        entry1.grid(column=0,row=3,sticky=tk.W,padx=5,pady=(5,10));
        
        dynvislabel = tk.Label(self, text='Dynamisk viskositet [Pa*s]');
        dynvislabel.grid(column=0,row=4,sticky=tk.W,padx=5,pady=(10,0));
        dynvisentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["dynvisvar"]);
        dynvisentry.grid(column=0,row=5,sticky=tk.W,padx=5,pady=(5,10));
        
        minvlabel = tk.Label(self, text='Min hastighet [m/s]');
        minvlabel.grid(column=0,row=6,sticky=tk.W,padx=5,pady=(10,0));
        minventry = tk.Entry(self, width=25, textvariable=self.master.shared_data["minvvar"]);
        minventry.grid(column=0,row=7,sticky=tk.W,padx=5,pady=(5,10));
        
        maxvlabel = tk.Label(self, text='Max hastighet [m/s]');
        maxvlabel.grid(column=0,row=8,sticky=tk.W,padx=5,pady=(10,0));
        maxventry = tk.Entry(self, width=25, textvariable=self.master.shared_data["maxvvar"]);
        maxventry.grid(column=0,row=9,sticky=tk.W,padx=5,pady=(5,10));
        
        pumpefflabel = tk.Label(self, text='Pump verkningsgrad [0-1]');
        pumpefflabel.grid(column=0,row=10,sticky=tk.W,padx=5,pady=(10,0));
        pumpeffentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["pumpeffvar"]);
        pumpeffentry.grid(column=0,row=11,sticky=tk.W,padx=5,pady=(5,10));
        
        potheadlabel = tk.Label(self, text='Pump uppfodringshöjd [m]');
        potheadlabel.grid(column=0,row=12,sticky=tk.W,padx=5,pady=(10,0));
        potheadentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["potheadvar"]);
        potheadentry.grid(column=0,row=13,sticky=tk.W,padx=5,pady=(5,10));
        
        heightlabel = tk.Label(self, text='Höjdskillnad [m]');
        heightlabel.grid(column=0,row=14,sticky=tk.W,padx=5,pady=(10,0));
        heightentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["heightvar"]);
        heightentry.grid(column=0,row=15,sticky=tk.W,padx=5,pady=(5,10));
        
        yearlylabel = tk.Label(self, text='Årsförbrukning [h]');
        yearlylabel.grid(column=0,row=16,sticky=tk.W,padx=5,pady=(10,0));
        yearlyentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["yearlyhvar"]);
        yearlyentry.grid(column=0,row=17,sticky=tk.W,padx=5,pady=(5,10));
        
        encostlabel = tk.Label(self, text='Elkostnad [kr/kwh]');
        encostlabel.grid(column=0,row=18,sticky=tk.W,padx=5,pady=(10,0));
        encostentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["encostvar"]);
        encostentry.grid(column=0,row=19,sticky=tk.W,padx=5,pady=(5,10));
        
        lifespanlabel = tk.Label(self, text='Livslängd [år]');
        lifespanlabel.grid(column=0,row=20,sticky=tk.W,padx=5,pady=(10,0));
        lifespanentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["lifespanvar"]);
        lifespanentry.grid(column=0,row=21,sticky=tk.W,padx=5,pady=(5,10));
        
        
        ##Column 1
        
        
        lengthlabel = tk.Label(self, text='Rörlängd [m]');
        lengthlabel.grid(column=1,row=8,sticky=tk.W,padx=5,pady=(10,0));
        lengthentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["lengthvar"]);
        lengthentry.grid(column=1,row=9,sticky=tk.W,padx=5,pady=(5,10));
        
        scafflabel = tk.Label(self, text='Ställningskostnad [kr]');
        scafflabel.grid(column=1,row=0,sticky=tk.W,padx=5,pady=(10,0));
        scaffentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["scaffvar"]);
        scaffentry.grid(column=1,row=1,sticky=tk.W,padx=5,pady=(5,10));
        
        salwlabel = tk.Label(self, text='Lön svets [kr/h]');
        salwlabel.grid(column=1,row=2,sticky=tk.W,padx=5,pady=(10,0));
        salwentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["salwvar"]);
        salwentry.grid(column=1,row=3,sticky=tk.W,padx=5,pady=(5,10));
        
        salilabel = tk.Label(self, text='Lön isolering [kr/h]');
        salilabel.grid(column=1,row=4,sticky=tk.W,padx=5,pady=(10,0));
        salientry = tk.Entry(self, width=25, textvariable=self.master.shared_data["salivar"]);
        salientry.grid(column=1,row=5,sticky=tk.W,padx=5,pady=(5,10));
        
        salalabel = tk.Label(self, text='Lön isolerskal [kr/h]');
        salalabel.grid(column=1,row=6,sticky=tk.W,padx=5,pady=(10,0));
        salaentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["salavar"]);
        salaentry.grid(column=1,row=7,sticky=tk.W,padx=5,pady=(5,10));
        
        speedwlabel = tk.Label(self, text='Svetshastighet [m/s]');
        speedwlabel.grid(column=1,row=10,sticky=tk.W,padx=5,pady=(10,0));
        speedwentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["speedwvar"]);
        speedwentry.grid(column=1,row=11,sticky=tk.W,padx=5,pady=(5,10));
        
        spotswlabel = tk.Label(self, text='Mängden fogar [n]');
        spotswlabel.grid(column=1,row=12,sticky=tk.W,padx=5,pady=(10,0));
        spotswentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["spotswvar"]);
        spotswentry.grid(column=1,row=13,sticky=tk.W,padx=5,pady=(5,10));
        
        mthicclabel = tk.Label(self, text='Godstjocklek [m]');
        mthicclabel.grid(column=1,row=14,sticky=tk.W,padx=5,pady=(10,0));
        mthiccentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["mthiccvar"]);
        mthiccentry.grid(column=1,row=15,sticky=tk.W,padx=5,pady=(5,10));
        
        ithicclabel = tk.Label(self, text='Isolering tjocklek [m]');
        ithicclabel.grid(column=1,row=16,sticky=tk.W,padx=5,pady=(10,0));
        ithiccentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["ithiccvar"]);
        ithiccentry.grid(column=1,row=17,sticky=tk.W,padx=5,pady=(5,10));
        
        atimelabel = tk.Label(self, text='Isolerskalstid [h]');
        atimelabel.grid(column=1,row=18,sticky=tk.W,padx=5,pady=(10,0));
        atimeentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["atimevar"]);
        atimeentry.grid(column=1,row=19,sticky=tk.W,padx=5,pady=(5,10));
    
        itimelabel = tk.Label(self, text='Isoleringstid [h]');
        itimelabel.grid(column=1,row=20,sticky=tk.W,padx=5,pady=(10,0));
        itimeentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["itimevar"]);
        itimeentry.grid(column=1,row=21,sticky=tk.W,padx=5,pady=(5,10));
        
        
    
        ##Column2
    
        apricelabel = tk.Label(self, text='Isolerskalskostnad [kr/m²]');
        apricelabel.grid(column=2,row=0,sticky=tk.W,padx=5,pady=(10,0));
        apriceentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["apricevar"]);
        apriceentry.grid(column=2,row=1,sticky=tk.W,padx=5,pady=(5,10));
        
        ipricelabel = tk.Label(self, text='Isoleringskostnad [kr/m²]');
        ipricelabel.grid(column=2,row=2,sticky=tk.W,padx=5,pady=(10,0));
        ipriceentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["ipricevar"]);
        ipriceentry.grid(column=2,row=3,sticky=tk.W,padx=5,pady=(5,10));
        
        workefflabel = tk.Label(self, text='Arbetseffektivitet [0-1]');
        workefflabel.grid(column=2,row=4,sticky=tk.W,padx=5,pady=(10,0));
        workeffentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["workeffvar"]);
        workeffentry.grid(column=2,row=5,sticky=tk.W,padx=5,pady=(5,10));
        
        bendlabel = tk.Label(self, text='Mängdböjar [n] (antas 90 grader)');
        bendlabel.grid(column=2,row=6,sticky=tk.W,padx=5,pady=(10,0));
        bendentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["bendvar"]);
        bendentry.grid(column=2,row=7,sticky=tk.W,padx=5,pady=(5,10));
        
        roughlabel = tk.Label(self, text='Absolut ytojämnhet [m]');
        roughlabel.grid(column=2,row=8,sticky=tk.W,padx=5,pady=(10,0));
        roughentry = tk.Entry(self, width=25, textvariable=self.master.shared_data["roughvar"]);
        roughentry.grid(column=2,row=9,sticky=tk.W,padx=5,pady=(5,10));
    
    
class App(tk.Tk):
    def __init__(self):
        super().__init__();
        self.columnconfigure(0, weight=1);
        self.columnconfigure(1, weight=3);
        
        self.shared_data ={
            "flowvar" : tk.DoubleVar(),
            "denvar" : tk.DoubleVar(),
            "dynvisvar" : tk.DoubleVar(),
            "minvvar" : tk.DoubleVar(),
            "maxvvar" : tk.DoubleVar(),
            "pumpeffvar" : tk.DoubleVar(),
            "potheadvar" : tk.DoubleVar(),
            "heightvar" : tk.DoubleVar(),
            "yearlyhvar" : tk.IntVar(),
            "encostvar" : tk.DoubleVar(),
            "lifespanvar" : tk.IntVar(),
            "lengthvar" : tk.DoubleVar(),
            "scaffvar" : tk.IntVar(),
            "salwvar" : tk.DoubleVar(),
            "salivar" : tk.DoubleVar(),
            "salavar" : tk.DoubleVar(),
            "speedwvar" : tk.DoubleVar(),
            "spotswvar" : tk.DoubleVar(),
            "mthiccvar" : tk.DoubleVar(),
            "ithiccvar" : tk.DoubleVar(),
            "atimevar" : tk.DoubleVar(),
            "itimevar" : tk.DoubleVar(),
            "apricevar" : tk.DoubleVar(),
            "ipricevar" : tk.DoubleVar(),
            "workeffvar" : tk.DoubleVar(),
            "bendvar" : tk.IntVar(),
            "roughvar" : tk.DoubleVar()
            }
        self.__set_default_values();
        self.__create_widgets();
    
    def __set_default_values(self):
        self.shared_data["denvar"].set(997);
        self.shared_data["dynvisvar"].set(0.001);
        self.shared_data["roughvar"].set(0.002);
        self.shared_data["pumpeffvar"].set(0.7);
        self.shared_data["encostvar"].set(0.5);
        self.shared_data["lifespanvar"].set(30);
        self.shared_data["mthiccvar"].set(0.005);
        self.shared_data["ithiccvar"].set(0.02);
        self.shared_data["apricevar"].set(10000);
        self.shared_data["ipricevar"].set(30000);
        self.shared_data["minvvar"].set(0);
        self.shared_data["maxvvar"].set(6);
        self.shared_data["yearlyhvar"].set(8520);
        self.shared_data["salavar"].set(300);
        self.shared_data["salivar"].set(300);
        self.shared_data["salwvar"].set(300);
        self.shared_data["speedwvar"].set(0.005);
        self.shared_data["flowvar"].set(300);
        self.shared_data["workeffvar"].set(0.65);
        self.shared_data["scaffvar"].set(150000);
    
    def __create_widgets(self):
        input_frame = InputFrame(self);
        input_frame.grid(column=0, row=0);
        
        output_frame = OutputFrame(self);
        output_frame.grid(column=1, row=0);
        
    def calculate(self):
        q= self.shared_data["flowvar"].get();
        den = self.shared_data["denvar"].get();
        dyn_vis = self.shared_data["dynvisvar"].get();
        min_v = self.shared_data["minvvar"].get();
        max_v = self.shared_data["maxvvar"].get();
        pump_eff = self.shared_data["pumpeffvar"].get();
        pot_head = self.shared_data["potheadvar"].get();
        diff_head = self.shared_data["heightvar"].get();
        yearly_h = self.shared_data["yearlyhvar"].get();
        en_cost = self.shared_data["encostvar"].get();
        sys_length = self.shared_data["lengthvar"].get();
        lifespan = self.shared_data["lifespanvar"].get();
        scaff = self.shared_data["scaffvar"].get();
        sal_w = self.shared_data["salwvar"].get();
        sal_i = self.shared_data["salivar"].get();
        sal_a = self.shared_data["salavar"].get();
        speed_w = self.shared_data["speedwvar"].get();
        spots_w = self.shared_data["spotswvar"].get();
        thic_m = self.shared_data["mthiccvar"].get();
        thic_i = self.shared_data["ithiccvar"].get();
        time_i = self.shared_data["itimevar"].get();
        time_a = self.shared_data["atimevar"].get();
        price_i = self.shared_data["ipricevar"].get();
        price_a = self.shared_data["apricevar"].get();
        work_eff = self.shared_data["workeffvar"].get();
        bends = self.shared_data["bendvar"].get();
        rough = self.shared_data["roughvar"].get();
        
        
        tree = ET.parse('ror_dim.xml');
        root = tree.getroot();

        #arrays for storing data from all the materials
        dim = [];
        mcost = [];
        vel = [];
        con_cost = [];
        total_cost = [];
        yearly_cost = [];
        energy_cost = [];
        functional = [];
        
        for child in root:
            dim.append(float(child.find('dim').text));
            mcost.append(float(child.find('mcost').text));


        n= 0; #keeps track of which dim we are on
        min_cost= None;
        min_dim = None;
        
        for dimension in dim:
            #vel
            v = calculations.velocity(dim[n],q);
            vel.append(v);
            print("Velocity: " + str(v))
            if v<= max_v and v>= min_v:
                functional.append(True);
            else:
                functional.append(False);

            #head   
            re = calculations.reynolds_number(v,den,sys_length,dyn_vis);
            if re >= 2300:
                f = calculations.Mileikovskyi(re,rough/dim[n]);
            else:
                f = calculations.laminar(re);
            print("friction coefficient: " + str(f));

            head_bend = calculations.bend_calc(dim[n],f,v,sys_length,bends,den);

           
           # print("loss to friction [kpa]: " + str(headloss(f,dim[n],v)/1000));  headloss(f,dim[n],v)
            
            diff_head_loss = diff_head*den*9.81 #converting to pascal
            
            h_loss = diff_head_loss+head_bend; #real world height diff + friction loss + bend loss
            print("loss in head [kpa]: " + str(h_loss/1000));

            if h_loss > (pot_head*den*9.81) and functional[n] != False: #if the loss is greater than pump head then invalidate it if its not already invalidated
                functional[n] = False;
            print(functional[n]);    
            #we save all costs in a list so it can potentially be exported to something like excel in the future 
            yearly_cost.append(calculations.calc_en_cost(h_loss,q,pump_eff,en_cost,yearly_h));
            con_cost.append(calculations.calc_con_cost(mcost[n],dim[n],sys_length,spots_w,speed_w,sal_w,sal_i,sal_a,time_i,time_a,price_i,price_a,work_eff,scaff,thic_m,thic_i));
            energy_cost.append(yearly_cost[n]*lifespan);
            total_cost.append(energy_cost[n]+con_cost[n]);
            
            print("Total cost for "  + str(dim[n]) + ": " + str(total_cost[n]));
            
            if functional[n] == True and (min_cost == None or total_cost[n] < min_cost):
                min_cost = total_cost[n];
                min_dim = dim[n];
    
            n+=1;
            
        print("The economical diameter is: " + str(1000*min_dim) + "mm with a total cost of: " + str(math.floor(min_cost)) + "kr");
        print("pot head [kpa]: " + str(pot_head*den*9.81/1000));
        dim_txt = []; #convert to text so that matplotlib does not interpret the dim as a value axis and scales it to that
        for val in dim:
            dim_txt.append(str(math.floor(val*1000)));
            
        valid_dim = [];
        valid_cost = [];
        col = [];
        x_time = []; # list of time lists will be (1ifespan x amount of valids) matrix
        y_cost = []; # same as above but energy cost for a certain year per valid
        nr=0; #what dim we are currently on
        j=0; # how many valids we have

        #go through and mark all the valid dims
        for valid in functional:
            if valid:
                col.append('green'); 
                valid_dim.append(dim_txt[nr]);
                valid_cost.append(total_cost[nr]/1000000);
                time =[];
                cost = [];
                for i in range(math.floor(lifespan+1)): #this is to calculate a cost for each year for the valid dims
                    time.append(i);
                    cost.append((yearly_cost[nr]*(i) + con_cost[nr])/1000000);
                x_time.append(time);
                y_cost.append(cost);
                j +=1
            else:
                col.append('red');
            nr +=1;

        #matplot lib setup
        fig,ax = plt.subplots(nrows=2,ncols=2);

        #graph for all dimmensions
        ax[0,0].bar(dim_txt,total_cost, color=col);

        #graph for only valid dimmensions
        ax[0,1].bar(valid_dim,valid_cost, color='green');
        ax[0,1].set_xlabel("Rör dim mm");
        ax[0,1].set_ylabel("Livscykelkostnad MSek");

        #plot one line for each valid dimension
        nr = 0
        for lists in x_time:
            ax[1,0].plot(lists,y_cost[nr], label=valid_dim[nr])
            nr +=1
        ax[1,0].legend();
        ax[1,0].set_ylim(bottom=0);

        ax[1,1].bar(dim_txt,vel)
        plt.show();

        #print to excel(more data could be output in the future)
        df = DataFrame({'Dimmension' : dim_txt, 'Totalcost' : total_cost, 'functional' : functional, 'construction cost' : con_cost, 'energy cost' : energy_cost});
        df.to_excel('ror_dim.xlsx', sheet_name='sheet1', index=False);
            

if __name__=="__main__":
    app = App()
    app.mainloop()

'''
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

'''