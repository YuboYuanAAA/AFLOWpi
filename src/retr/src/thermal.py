import AFLOWpi
import re
import numpy
import scipy.integrate
import collections
import os


def _increase_celldm1(oneCalc,ID,amount):
    if ID in oneCalc['prev']:
        return oneCalc,ID

    #change prefix in input file so it doesn't conflict with later calculations after thermal

    oneCalc,ID = AFLOWpi.prep._modifyNamelistPW(oneCalc,ID,'&control','prefix','"%s_vol"'%oneCalc['_AFLOWPI_PREFIX_'])
    oneCalc["_AFLOWPI_PREFIX_"]=oneCalc["_AFLOWPI_PREFIX_"]+"_vol"

    inp_file = AFLOWpi.retr._getInputFileString(oneCalc,ID)
    celldm1 = float(AFLOWpi.retr._splitInput(inp_file)['&system']['celldm(1)'])

    new_celldm1=celldm1*amount


    oneCalc,ID = AFLOWpi.prep._modifyNamelistPW(oneCalc,ID,'&system','celldm(1)',new_celldm1)

    return oneCalc,ID


def _get_gruneisen(oneCalc,ID,band=True):
    norm_ID  = AFLOWpi.prep._return_ID(oneCalc,ID,step_type='phonon')
    expn_ID  = AFLOWpi.prep._return_ID(oneCalc,ID,step_type='thermal')

    expn_vol_ID = AFLOWpi.prep._return_ID(oneCalc,ID,step_type='thermal_relax')

    norm_vol = AFLOWpi.retr.getCellVolume(oneCalc,norm_ID,string=False,conventional=False)
    expn_vol = AFLOWpi.retr.getCellVolume(oneCalc,expn_vol_ID,string=False,conventional=False)

    bohr2meter=5.29177e-11
    norm_vol*=bohr2meter**3.0
    expn_vol*=bohr2meter**3.0


#    print expn_vol/norm_vol
#    print 
    if band==True:
        extension='phBAND.gp'
    else:
        extension='phDOS.gp'

    norm_freq,q_point_old = AFLOWpi.retr._get_ph_data(oneCalc,norm_ID,extension=extension)
    expn_freq,q_point_old = AFLOWpi.retr._get_ph_data(oneCalc,expn_ID,extension=extension)



    grun=[]
    q_point=[]
    omega=[]

    for i in range(len(norm_freq)):
        if band:
            q_point.append(q_point_old[i])
        for j in range(len(norm_freq[i])):
            try:
                    deriv  = (expn_freq[i][j]-norm_freq[i][j])/(expn_vol-norm_vol)
                    deriv *= -1.0*norm_vol/norm_freq[i][j]
                    if not numpy.isnan(deriv) and not numpy.isinf(deriv):
                        try:
                            grun[i].append(deriv)
                        except Exception,e:
                            grun.append([])
                            grun[i].append(deriv)
                        try:
                            omega[i].append(norm_freq[i][j])
                        except Exception,e:
                            omega.append([])
                            omega[i].append(norm_freq[i][j])
                    else:

                        try:
                            grun[i].append(0.0)
                        except Exception,e:
                            grun.append([])
                            grun[i].append(0.0)
                        try:
                            omega[i].append(norm_freq[i][j])
                        except Exception,e:
                            omega.append([])
                            omega[i].append(norm_freq[i][j])
                        continue
            except Exception,e:
                AFLOWpi.run._fancy_error_log(e)

#                print e


#    print len(grun)
#    print len(q_point_old)
#    print len(q_point)


#   raise SystemExit
    if band:
        grun_data_str='%s          %s                  %s                 %s'%('q','TA',"TA'",'LA')
        for i in range(len(grun)):
            try:
                if len(grun[i]) == len(grun[12]):
                    grun_data_str+='\n%10.8f '%q_point[i]

                    for j in range(len(grun[i])):
                        grun_data_str+='%16.16f '%grun[i][j]
            except:
                continue
    else:
        grun_data_str=""
        for i in range(len(grun)):
            try:
                for j in range(len(grun[i])):
#                    print grun[i][j]
#                    print grun[i][j]**2.0
                    grun_data_str+='%16.16f %16.16f\n'%(omega[i][j],grun[i][j]**2.0)
            except:
                continue
 #   if len(grun)==3:
 #       pass
    # else:
    #     for i in range(len(grun[0][3:-1])):
    #         grun_data_str+='Optical             '
    #     for i in range(len(q_point)):
    #         grun_data_str+='\n%10.8f %16.16f %16.16f  %16.16f'%(q_point[i],grun[0][i],grun[1][i],grun[2][i])
    #         for j in range(len(grun[i][3:-1])):
    #             grun_data_str+='%16.16f'%(grun[i][j])
        

    if band:
        grun_file_name = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s.phGRUN.gp'%ID)
    else:
        grun_file_name = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s.phSCATTER.gp'%ID)

    with open(grun_file_name,'w') as gpfo:
        gpfo.write(grun_data_str)
    
    av_TA       = sum(grun[0])/len(grun[0])
    av_TA_prime = sum(grun[1])/len(grun[1])
    av_LA      = sum(grun[2])/len(grun[2])
        
    return [av_TA,av_TA_prime,av_LA]
        
    
            

#    frequency = 
#    delta_vol_frequency= 
def _get_ph_data(oneCalc,ID,extension='phBAND.gp',postfix=''):

    data_file_name = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s%s.%s'%(ID,postfix,extension))


    data =numpy.loadtxt(data_file_name,dtype=numpy.float64,)

    return data[:,1:],data[:,0]



    

def _get_gamma_velocity(freq,q):
    return (freq[0]-freq[10])/(q[0]-q[10])

def _get_debye_freq(oneCalc,ID):


    path_str = AFLOWpi.run._phonon_band_path(oneCalc,ID)

    path_pts_list = [int(i.split()[1]) for i in path_str.split('\n')[1:] if len(i.strip())!=0]
#    print path_pts_list
    freq,q_vals = AFLOWpi.retr._get_ph_data(oneCalc,ID)
    TA       = freq[:,0]
    TA_prime = freq[:,1]
    LA       = freq[:,2]
#    q_vals   = freq[-1]

    total=0
#    for i in range(len(path_pts_list)):
    path_index= []
    for i in range(len(path_pts_list)):
        if path_pts_list[i]==0:
            continue
        if path_pts_list[i+1]==0:
            path_index.append([sum(path_pts_list[:i]),sum(path_pts_list[:i+1])+1])
        else:
            path_index.append([sum(path_pts_list[:i]),sum(path_pts_list[:i+1])])
    


    
#    index = for i in path_pts_list
#    print path_index
#    print TA
    average_freq_TA       = numpy.average([max(TA[i[0]:i[1]]) for i in path_index])
    average_freq_TA_prime = numpy.average([max(TA_prime[i[0]:i[1]]) for i in path_index])
    average_freq_LA       = numpy.average([max(LA[i[0]:i[1]]) for i in path_index])
    return average_freq_TA,average_freq_TA_prime,average_freq_LA

def _get_debye_temp(oneCalc,ID):
    #get the frequencies for TA, TA', and LA
    frequencies,q_vals = AFLOWpi.retr._get_ph_data(oneCalc,ID)

    #q vals so we can find v_debye near gamma
#    q_vals = frequencies[-1]

    
#    frequencies[0] = [i*0.0299792458 for i in frequencies[0]]
#    frequencies[1] = [i*0.0299792458 for i in frequencies[1]]
#    frequencies[2] = [i*0.0299792458 for i in frequencies[2]]
    #get volume of original cell
    norm_ID  = AFLOWpi.prep._return_ID(oneCalc,ID,step_type='phonon')
    cell_vol = AFLOWpi.retr.getCellVolume(oneCalc,norm_ID,string=False,conventional=False)
    #convert to meters
    bohr2meter=5.29177e-11
    V=cell_vol*bohr2meter**3.0

    #get num atoms in cell
    N = float(AFLOWpi.retr._splitInput(oneCalc['_AFLOWPI_INPUT_'])['&system']['nat'])

    #some constants
    h_bar=1.0545718*10**-34 
    k_b=1.38064852*10**-23

    #get v_debye for each branch
    v_i = AFLOWpi.retr._get_debye_freq(oneCalc,ID)
    v_s_TA       = v_i[0]
    v_s_TA_prime = v_i[1]
    v_s_LA       = v_i[2]


    #calculate debye temperature for each branch
    wo_v           = 2.0*numpy.pi*h_bar/k_b#*(6.0*numpy.pi**2.0*N/V)**(1.0/3.0)
    debye_TA       = wo_v*v_s_TA
    debye_TA_prime = wo_v*v_s_TA_prime
    debye_LA       = wo_v*v_s_LA


#    print debye_TA
#    print debye_TA_prime
#    print debye_LA

    return debye_TA,debye_TA_prime,debye_LA



def _therm_pp(oneCalc,ID):
    grun_i  = AFLOWpi.retr._get_gruneisen(oneCalc,ID)
    AFLOWpi.retr._get_gruneisen(oneCalc,ID,band=False)

    theta_i = AFLOWpi.retr._get_debye_temp(oneCalc,ID)
#    print theta_i
    #get volume of original cell
    norm_ID  = AFLOWpi.prep._return_ID(oneCalc,ID,step_type='phonon')
    cell_vol = AFLOWpi.retr.getCellVolume(oneCalc,norm_ID,string=False,conventional=False)
    #convert to meters
    bohr2meter=5.29177e-11
    V=cell_vol*bohr2meter**3.0


    #get num atoms in cell
    N = float(AFLOWpi.retr._splitInput(oneCalc['_AFLOWPI_INPUT_'])['&system']['nat'])


    cell_mass = AFLOWpi.retr._get_cell_mass(oneCalc,ID)
    
    #convert amu to kg
    M=cell_mass*1.66054e-27
    Mass=M/float(N)
    Vol=V/float(N)

    #get the frequencies for TA, TA', and LA
    frequencies,q_vals = AFLOWpi.retr._get_ph_data(oneCalc,ID)

    v_i=AFLOWpi.retr._get_debye_freq(oneCalc,ID)

    print Vol
    print Mass
    print grun_i
    print v_i
    print theta_i


    therm_cond_data_str="T       Total        TA           TA'          La"
    TEMP = numpy.linspace(0.0,2000.0,400.0)

    Vol   = 375.60264000000006 # volume of one cell in angstrom^3                                                      
    Vol  *= 10.0**(-30.0) # convert angstrom to m^3                                                                    
    Vol  /= 8.0 # do volume per atom                                                                                   

    Mass   = 63.5463*3.0  # 3 Cu                                                                                       
    Mass += 78.9718*4.0  # 4 Se                                                                                        
    Mass += 121.760*1.0  # 1 Antimony                                                                                  
    Mass *= 1.66054e-27 # convert amu to kg                                                                            
    Mass /= 8.0        # average mass per atom      

    v_i     = [1485.0, 1699.0, 3643.0] #TA, TA', LA                                                                         
    theta_i = [60.0,   65.0,   78.0  ] #TA, TA', LA                                                                      
    grun_i  = [1.27,   1.14,   1.26, ] #TA, TA', LA     


    for T in TEMP:
        total,TA_cont,TA_prime_cont,LA_cont = AFLOWpi.retr._do_therm(v_i,theta_i,grun_i,Mass,Vol,T)
        
        therm_cond_data_str+='\n%7.1f %12.3f %12.3f %12.3f %12.3f'%(T,total,TA_cont,TA_prime_cont,LA_cont)

    therm_file_name = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_thermal_cond.dat'%ID)
    with open(therm_file_name,'w') as tcfo:
        tcfo.write(therm_cond_data_str) 


def _test_therm_pp():

    therm_cond_data_str="T       Total        TA           TA'          La"
#   TEMP = numpy.linspace(1.0,2001.0,2000.0)
    TEMP = [80.0,
            87.3333333333333,
            94.6666666666667 ,
            102,
            109.333333333333,
            116.666666666667,
            124,
            131.333333333333,
            138.666666666667,
            146,
            153.333333333333,
            160.666666666667,
            168,
            175.333333333333,
            182.666666666667,
            190,
            197.333333333333,
            204.666666666667,
            212,
            219.333333333333,
            226.666666666667,
            234,
            241.333333333333,
            248.666666666667,
            256,
            263.333333333333,
            270.666666666667,
            278,
            285.333333333333,
            292.666666666667,
            300,
            ]

    Vol   = 375.60264000000006 # volume of one cell in angstrom^3                                                      
    Vol  *= 10.0**(-30.0) # convert angstrom to m^3                                                                    
    Vol  /= 8.0 # do volume per atom                                                                                   

    Mass   = 63.5463*3.0  # 3 Cu                                                                                       
    Mass += 78.9718*4.0  # 4 Se                                                                                        
    Mass += 121.760*1.0  # 1 Antimony                                                                                  
    Mass *= 1.66054e-27 # convert amu to kg                                                                            
    Mass /= 8.0        # average mass per atom      

    v_i     = [1485.0, 1699.0, 3643.0] #TA, TA', LA                                                                         
    theta_i = [60.0,   65.0,   78.0  ] #TA, TA', LA                                                                      
    grun_i  = [1.27,   1.14,   1.26, ] #TA, TA', LA     


    for T in TEMP:
        total,TA_cont,TA_prime_cont,LA_cont = AFLOWpi.retr._do_therm(v_i,theta_i,grun_i,Mass,Vol,T)
        
        therm_cond_data_str+='\n%7.1f %12.3f %12.3f %12.3f %12.3f'%(T,total,TA_cont,TA_prime_cont,LA_cont)

    therm_file_name = os.path.join('./','test_thermal_cond.dat')
    with open(therm_file_name,'w') as tcfo:
        tcfo.write(therm_cond_data_str) 


######################################################################################################################                                                                                               
######################################################################################################################                                                                                               

def _do_therm(v_i,theta_i,grun_i,Mass,Vol,T):
    ######################################################################################################################
    def calc_tau_N_TA(x,grun,velocity,vol,mass,T):
        #Relax Temp Scattering TA'                                                                                                                                          
        h_bar = numpy.float64(1.0545718*(10.0**(-34.0))) # hbar
        k_b   = numpy.float64(1.38064852*(10.0**(-23.0))) #boltzmann                                               

        one_over_tau_N_TA  = k_b**4.0
        one_over_tau_N_TA *= grun**2.0
        one_over_tau_N_TA *= vol
        one_over_tau_N_TA /= mass
        one_over_tau_N_TA /= h_bar**3.0
        one_over_tau_N_TA /= velocity**5.0

        one_over_tau_N_TA *= k_b/h_bar
        one_over_tau_N_TA *= x
        one_over_tau_N_TA *= T**5.0

        tau_N_TA  = 1.0/one_over_tau_N_TA

        return tau_N_TA
    ######################################################################################################################
    def calc_tau_N_LA(x,grun,velocity,vol,mass,T):
        #Relax Temp Scattering LA                                                                                                         
        h_bar = numpy.float64(1.0545718*(10.0**(-34.0))) # hbar
        k_b   = numpy.float64(1.38064852*(10.0**(-23.0))) #boltzmann                                                                                                                                                                                                      
        one_over_tau_N_LA  = k_b**3.0
        one_over_tau_N_LA *= grun**2.0
        one_over_tau_N_LA *= vol
        one_over_tau_N_LA /= mass
        one_over_tau_N_LA /= h_bar**2.0
        one_over_tau_N_LA /= velocity**5.0

        one_over_tau_N_LA *= (k_b/h_bar)**2.0
        one_over_tau_N_LA *= x**2.0
        one_over_tau_N_LA *= T**5.0

        tau_N_LA  = 1.0/one_over_tau_N_LA

        return tau_N_LA
    ######################################################################################################################                                                                                   
    def calc_tau_U(x,grun,velocity,debye_temp,mass,T):
        #Relax Temp Umklamp LA                                                                                     
        h_bar = numpy.float64(1.0545718*(10.0**(-34.0))) # hbar
        k_b   = numpy.float64(1.38064852*(10.0**(-23.0))) #boltzmann                                                                                            

        one_over_tau_U  = h_bar
        one_over_tau_U *= grun**2.0
        one_over_tau_U /= mass
        one_over_tau_U /= velocity**2.0
        one_over_tau_U /= debye_temp

        one_over_tau_U *= (k_b/h_bar)**2.0
        one_over_tau_U *= x**2.0
        one_over_tau_U *= T**3.0

        one_over_tau_U *= numpy.exp(-1.0*debye_temp/(3.0*T))

        tau_U = 1.0/one_over_tau_U

        return tau_U
    ######################################################################################################################
    def first_int(x,grun,velocity,debye_temp,vol,mass,T,trans):
        #do first integral in DB model
        tau_U=calc_tau_U(x,grun,velocity,debye_temp,mass,T)
        if trans:
            tau_N=calc_tau_N_TA(x,grun,velocity,vol,mass,T)
        else:
            tau_N=calc_tau_N_LA(x,grun,velocity,vol,mass,T)

        Tc = 1.0/(1.0/tau_U + 1.0/tau_N)

        sol  = Tc
        sol *= x**4.0
        sol *= numpy.exp(x)/(numpy.exp(x)-1.0)**2.0


        return sol
    ######################################################################################################################      
    def second_int(x,grun,velocity,debye_temp,vol,mass,T,trans):
        #do second integral in DB model
        tau_U=calc_tau_U(x,grun,velocity,debye_temp,mass,T)
        if trans:
            tau_N=calc_tau_N_TA(x,grun,velocity,vol,mass,T)
        else:
            tau_N=calc_tau_N_LA(x,grun,velocity,vol,mass,T)

        Tc = 1.0/(1.0/tau_U + 1.0/tau_N)

        #Tc/tau_N
        Tc_mod = tau_U/(tau_U + tau_N)


        sol  = Tc_mod
        sol *= x**4.0
        sol *= numpy.exp(x)/(numpy.exp(x)-1.0)**2.0


        return sol
    ######################################################################################################################
    def third_int(x,grun,velocity,debye_temp,vol,mass,T,trans):
        #do third integral in DB model
        tau_U=calc_tau_U(x,grun,velocity,debye_temp,mass,T)
        if trans:
            tau_N=calc_tau_N_TA(x,grun,velocity,vol,mass,T)
        else:
            tau_N=calc_tau_N_LA(x,grun,velocity,vol,mass,T)


        #Tc/(tau_U*tau_N)
        Tc_mod = 1.0/(tau_U + tau_N)

        sol  = Tc_mod
        sol *= x**4.0
        sol *= numpy.exp(x)/(numpy.exp(x)-1.0)**2.0

        return sol



    ######################################################################################################################
    #define constants
    h_bar = numpy.float64(1.0545718*(10.0**(-34.0))) # hbar
    k_b   = numpy.float64(1.38064852*(10.0**(-23.0))) #boltzmann  

    #define a constant from other constants
    C_PHON_CONST  = 1.0/3.0
    C_PHON_CONST *= k_b**4.0
    C_PHON_CONST *= T**3.0
    C_PHON_CONST /= 2.0*numpy.pi**2.0
    C_PHON_CONST /= h_bar**3.0

    #speed of sound for each accoustic branch
    vel_TA    = v_i[0]
    vel_TA1   = v_i[1]
    vel_LA    = v_i[2]
    #scaling constants for each accoustic branch
    C_TA      = C_PHON_CONST/vel_TA
    C_T1      = C_PHON_CONST/vel_TA1
    C_LA      = C_PHON_CONST/vel_LA
    #debye temp for each accoustic branch
    theta_TA  = theta_i[0]
    theta_TA1 = theta_i[1]
    theta_LA  = theta_i[2]
    #gruneisen parameter for each accoustic branch
    grun_TA   = grun_i[0]
    grun_TA1  = grun_i[1]
    grun_LA   = grun_i[2]
    #upper limit of integration for a given T for the integrals for each accoustic branch
    max_TA    = theta_TA/T
    max_TA1   = theta_TA1/T
    max_LA    = theta_LA/T
    print max_TA,max_TA1,max_LA
    print 
    print 
    
    ##################################################################################
    #calculate the three integrals for TA phonon and find lattice k for TA
    TA_1 =  scipy.integrate.quad(first_int, 0.00,max_TA,(grun_TA,vel_TA,theta_TA,Vol,Mass,T,True),epsabs=0, epsrel=1.49e-6)[0]
    TA_2 =  scipy.integrate.quad(second_int,0.00,max_TA,(grun_TA,vel_TA,theta_TA,Vol,Mass,T,True),epsabs=0, epsrel=1.49e-6)[0]
    TA_3 =  scipy.integrate.quad(third_int, 0.00,max_TA,(grun_TA,vel_TA,theta_TA,Vol,Mass,T,True),epsabs=0, epsrel=1.49e-6)[0]

    klattice_TA  = C_TA * (TA_1 + TA_2**2.0/TA_3)           
    #calculate the three integrals for TA' phonon and find lattice k for TA'
    T1_1 = scipy.integrate.quad(first_int, 0.00,max_TA1,(grun_TA1,vel_TA1,theta_TA1,Vol,Mass,T,True),epsabs=0, epsrel=1.49e-6)[0]
    T1_2 = scipy.integrate.quad(second_int,0.00,max_TA1,(grun_TA1,vel_TA1,theta_TA1,Vol,Mass,T,True),epsabs=0, epsrel=1.49e-6)[0]
    T1_3 = scipy.integrate.quad(third_int, 0.00,max_TA1,(grun_TA1,vel_TA1,theta_TA1,Vol,Mass,T,True),epsabs=0, epsrel=1.49e-6)[0]

    klattice_T1  = C_T1 * (T1_1 + T1_2**2.0/T1_3)           
    #calculate the three integrals for LA phonon and find lattice k for LA
    LA_1 =  scipy.integrate.quad(first_int, 0.00,max_LA,(grun_LA,vel_LA,theta_LA,Vol,Mass,T,False),epsabs=0, epsrel=1.49e-6)[0]
    LA_2 =  scipy.integrate.quad(second_int,0.00,max_LA,(grun_LA,vel_LA,theta_LA,Vol,Mass,T,False),epsabs=0, epsrel=1.49e-6)[0]
    LA_3 =  scipy.integrate.quad(third_int, 0.00,max_LA,(grun_LA,vel_LA,theta_LA,Vol,Mass,T,False),epsabs=0, epsrel=1.49e-6)[0]

#   LA_3 =  scipy.integrate.quad(third_int, 0.001,max_LA,(grun_LA,vel_LA,theta_LA,Vol,Mass,T,False),epsabs=1.49e-20, epsrel=1.49e-20)[
#   print LA_3.message
#   LA_3 = LA_3[0]


    klattice_LA  =  C_LA * (LA_1 + LA_2**2.0/LA_3)
    ##################################################################################                                           
    #sum over all contibutions for lattice k at Temp T 
    klattice_total  = 0.0
    klattice_total += klattice_TA
    klattice_total += klattice_T1
    klattice_total += klattice_LA

    return klattice_total,klattice_TA,klattice_T1,klattice_LA

#def  _get_long_phon(oneCalc,ID,optical=True):

#     band_file_name = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s.phBAND.gp'%ID)

#     with open(band_file_name,'r') as bdfo:
#         bdfs = bdfo.read()



#     gg=re.findall('^\s*0.00.*\n',bdfs,re.M)
#     split_at_gamma = gg[0].split()[1:]

#     long_phon_ind = [i+1 for i in range(len(split_at_gamma)) if abs(float(split_at_gamma[i]))==0.00]
# #    print long_phon_ind 
# #    print long_phon_ind 
# #    print long_phon_ind 

#     phon=[list(),list(),list()]
#     q_vals=[]
#     opt=[[]]
# #     for i in bdfs.split('\n'):
# # #        print i

# #         per_q = [float(j) for j in i.split() ]
# #         try:
# # #            phon[0].append(per_q[long_phon_ind[0]])
# # #            phon[1].append(per_q[long_phon_ind[1]])
# # #            phon[2].append(per_q[long_phon_ind[2]]) 
# #             q_vals.append(per_q[0])
# #             phon[0].append(per_q[1])
# #             phon[1].append(per_q[2])
# #             phon[2].append(per_q[3]) 


# #             if optical==True:
# #                 for k in range(len(per_q))[4:]:
# #                     try:
# # #                        print k-4
# #                         opt[k-4].append(per_q[k])
# #                     except Exception,e:
# #                         opt[k-4]=[]
# #                         opt[k-4]=[per_q[k]]

# #         except:
# #             pass


# #     v0 = _get_gamma_velocity(phon[0],q_vals)
# #     v1 = _get_gamma_velocity(phon[1],q_vals)
# #     v2 = _get_gamma_velocity(phon[2],q_vals)
# # #    grad_first_phon  = numpy.gradient(phon[0])
# # #    grad_second_phon  =numpy.gradient(phon[1])
# # #    grad_third_phon  = numpy.gradient(phon[2])


# #   #  sums= {0:sum(grad_first_phon[:30]),1:sum(grad_second_phon[:30]),2:sum(grad_third_phon[:30]),}
# #     sums = {0:v0,1:v1,2:v2}
# # #    print grad_first_phon[:50]
# # #    print grad_second_phon[:50]
# # #    print grad_third_phon[:50]


# #     sorted_ind = [i[0] for i in  sorted(sums.items())]

# #     #convert cm^-1 to rad/s
#      sf = 0.0299792458*10.0**12
# # #    print sf
# # #    print sf
# # #    print sf
# #     #scale frequencies to meters
#      phon[sorted_ind[0]]=[i*sf for i in phon[sorted_ind[0]]]
#      phon[sorted_ind[1]]=[i*sf for i in phon[sorted_ind[1]]]
#      phon[sorted_ind[2]]=[i*sf for i in phon[sorted_ind[2]]]
# # #    print q_vals
# # #    return [phon[0],phon[1],phon[2],q_vals]
# #     if optical==True:
# #         ret_list = [phon[sorted_ind[0]],phon[sorted_ind[1]],phon[sorted_ind[2]],]
# #         ret_list.extend(opt)
# #         ret_list.append(q_vals)
# #         return ret_list
# #     else:
# #         return [phon[sorted_ind[0]],phon[sorted_ind[1]],phon[sorted_ind[2]],q_vals]

