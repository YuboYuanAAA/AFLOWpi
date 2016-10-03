import AFLOWpi
import os
import re
import __main__
import logging
import shutil
import glob
import numpy
import time

class tight_binding:
    def __init__(self,calcs,unoccupied_bands=True):
        self.calcs=calcs
        self.plot=AFLOWpi.prep.tb_plotter(self.calcs)
        self.cond_bands=unoccupied_bands

        self.step_counter=0
        tb_plotter=AFLOWpi.prep.tb_plotter(calcs)

        AFLOWpi.prep.addToAll_(calcs,'PREPROCESSING',"""oneCalc,ID=AFLOWpi.prep._modifyNamelistPW(oneCalc,ID,'&control','calculation','"scf"')""")
        AFLOWpi.prep.addToAll_(calcs,'POSTPROCESSING',"""AFLOWpi.scfuj._get_ham_xml(oneCalc,ID)""")

        command='''if oneCalc["__execCounter__"]<=%s:
     oneCalc,ID=AFLOWpi.prep._run_tb_ham_prep(__submitNodeName__,oneCalc,ID,unoccupied_bands=%s)
     oneCalc['__execCounter__']+=1
     AFLOWpi.prep._saveOneCalc(oneCalc,ID)'''%(self.step_counter,unoccupied_bands)

        AFLOWpi.prep.addToAll_(self.calcs,'RUN',command)
        self.step_counter+=1
#	AFLOWpi.prep.addToAll_(calcs,block='POSTPROCESSING',addition='AFLOWpi.retr._writeEfermi(oneCalc,ID+"_nscf")')


    def dos(self,dos_range=[-10,10],k_grid=[20,20,20],projected=True,ne=2001,cond_bands=True,fermi_surface=False):
	AFLOWpi.prep.addToAll_(self.calcs,'PREPROCESSING','AFLOWpi.scfuj.want_dos_prep(oneCalc,ID)')
        command='''if oneCalc["__execCounter__"]<=%s:
     oneCalc,ID = AFLOWpi.prep._run_want_dos(__submitNodeName__,oneCalc,ID,dos_range=%s,k_grid=%s,project=%s,num_e=%s,cond_bands=%s,fermi_surface=%s)
     oneCalc['__execCounter__']+=1
     AFLOWpi.prep._saveOneCalc(oneCalc,ID)'''%(self.step_counter,dos_range,k_grid,projected,ne,cond_bands,fermi_surface)

        AFLOWpi.prep.addToAll_(self.calcs,'RUN',command)
        self.step_counter+=1

        calc_type='Calculate DOS with PAO-TB Hamiltonian'
        print '                 %s'% (calc_type)
        if projected==True:
            calc_type='Calculate PDOS with PAO-TB Hamiltonian'
            print '                 %s'% (calc_type)
        if fermi_surface==True:
            calc_type='Generate Fermi Surface data with PAO-TB Hamiltonian'
            print '                 %s'% (calc_type)

    def bands(self,nk=1000,nbnd=None,eShift=15.0,cond_bands=True):
	AFLOWpi.prep.addToAll_(self.calcs,'PREPROCESSING','AFLOWpi.scfuj.want_bands_prep(oneCalc,ID)')
        command = '''if oneCalc["__execCounter__"]<=%s:
     oneCalc,ID = AFLOWpi.prep._run_want_bands(__submitNodeName__,oneCalc,ID,eShift=%s,num_points=%s,cond_bands=%s)
     oneCalc['__execCounter__']+=1
     AFLOWpi.prep._saveOneCalc(oneCalc,ID)'''%(self.step_counter,eShift,nk,cond_bands)

        AFLOWpi.prep.addToAll_(self.calcs,'RUN',command)
        self.step_counter+=1

        calc_type='Calculate bands with PAO-TB Hamiltonian'
        print '                 %s'% (calc_type)


    def effmass(self,temperature=[300.0,300.0],step=1):

        if self.cond_bands!=True:
            print 'CANNOT DO EFFECTIVE MASS WITHOUT CONDUCTION BANDS. SKIPPING EFFECTIVE MASS CALC'
            return

	AFLOWpi.prep.addToAll_(self.calcs,'PREPROCESSING','AFLOWpi.scfuj.want_eff_mass_prep(oneCalc,ID)')

        calc_type='Calculate Effective Mass with PAO-TB Hamiltonian'
        print '                 %s'% (calc_type)


#if oneCalc["__execCounter__"]<%s
#     oneCalc["__execCounter__"]+=1
#     AFLOWpi.prep._saveOneCalc(oneCalc,ID)
        command = '''if oneCalc["__execCounter__"]<=%s:
     oneCalc,ID = AFLOWpi.prep._run_want_eff_mass(__submitNodeName__,oneCalc,ID,temperature=%s,step=%s)
     oneCalc['__execCounter__']+=1
     AFLOWpi.prep._saveOneCalc(oneCalc,ID)'''%(self.step_counter,temperature,step)

        AFLOWpi.prep.addToAll_(self.calcs,'RUN',command)
        self.step_counter+=1
	


    def transport(self):
        pass


def _form_TB_dir(oneCalc,ID,from_ls=True):
    if from_ls:
        AFLOWpi.prep._from_local_scratch(oneCalc,ID,ext_list=['.save'])
    try:
        save_dir = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],oneCalc['_AFLOWPI_PREFIX_']+'.save')
        TB_dir = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_TB.save'%ID)
        if not os.path.exists(TB_dir):
            os.mkdir(TB_dir)
        data_file_dft = os.path.join(save_dir,'data-file.xml')
        atomic_proj_dat = os.path.join(save_dir,'atomic_proj.dat')
        shutil.copy(data_file_dft,TB_dir)
        shutil.copy(atomic_proj_dat,TB_dir)
    except Exception,e:
        print e


def _run_want_bands(__submitNodeName__,oneCalc,ID,eShift=10.0,num_points=1000,cond_bands=True):
    nscf_ID=ID+'_nscf'

    Efermi = AFLOWpi.retr._getEfermi(oneCalc,nscf_ID,directID=True)
    eShift=float(Efermi)+10.0
    
    if AFLOWpi.prep._ConfigSectionMap("run","exec_prefix") != '':
        execPrefix=AFLOWpi.prep._ConfigSectionMap("run","exec_prefix")
    else:
        execPrefix=''

    want_dict = AFLOWpi.scfuj.WanT_bands(oneCalc,ID=ID,eShift=eShift,num_points=num_points,cond_bands=cond_bands)



    for want_ID,want_calc in want_dict.iteritems():
        AFLOWpi.run._oneRun(__submitNodeName__,want_calc,want_ID,execPrefix=execPrefix,execPostfix='',engine='espresso',calcType='custom',execPath='./want_bands.x',)

    AFLOWpi.prep._clean_want_bands(oneCalc,ID)

    return oneCalc,ID


def _run_want_eff_mass(__submitNodeName__,oneCalc,ID,temperature=[0,800],step=10):
    nscf_ID=ID+'_nscf'

    if AFLOWpi.prep._ConfigSectionMap("run","exec_prefix") != '':
        execPrefix=AFLOWpi.prep._ConfigSectionMap("run","exec_prefix")
    else:
        execPrefix=''



    if '__effmass_counter__' not in oneCalc.keys():
        #if an old effective mass data file exists delete it before we start
        effmass_datafile_by_temp = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_WanT_effmass.dat'%ID)
        if os.path.exists(effmass_datafile_by_temp):
            os.remove(effmass_datafile_by_temp)
        #set counter to zero
        oneCalc['__effmass_counter__']=0
        AFLOWpi.prep._saveOneCalc(oneCalc,ID)

    cell_params = AFLOWpi.retr._getCellParams(oneCalc,ID)
    k_grid = AFLOWpi.prep.getMPGrid(cell_params,offset=True,string=False)
    try:
        k_grid = [int(float(x)*10.0) for x in k_grid.split()[:3]]
    except:
        k_grid=[20,20,20]

    Efermi = AFLOWpi.retr._getEfermi(oneCalc,nscf_ID,directID=True)
    eShift=float(Efermi)+10.0

    step_holder=step
    step = (float(temperature[1])-float(temperature[0])+float(step_holder))/float(step)
    temps = numpy.linspace(float(temperature[0]),float(temperature[1]),step)

    #some constants
    h_bar = numpy.float64(1.05457180*10.0**-34.0)
    k_b   = numpy.float64(1.38064852*10.0**-23.0)
    m_e   = numpy.float64(9.10938356*10.0**-31.0)

    sf = numpy.power(k_b*m_e/(2.0*numpy.pi*numpy.power(h_bar,2.0)),(3.0/2.0))#*numpy.power((1.0/cm2m),2.0)


    for temp_step in range(len(temps)):
        if temp_step<oneCalc['__effmass_counter__']:
            continue

        want_dos_calc = AFLOWpi.scfuj.WanT_dos(oneCalc,ID,k_grid=k_grid,pdos=False,boltzmann=False,eShift=eShift,cond_bands=True,temperature=temps[temp_step])
        this_temp = '%8.4f ' % float(temps[temp_step])
        for want_dos_ID,want_dos in want_dos_calc.iteritems():
            AFLOWpi.run._oneRun(__submitNodeName__,want_dos,want_dos_ID,engine='espresso',calcType='custom',execPath='./effmass.x',execPrefix=execPrefix,execPostfix='')

            effmass_datafile = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s.dat'%want_dos_ID)
            effmass_datafile_by_temp = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_WanT_effmass.dat'%ID)
            with open(effmass_datafile,'r') as emdfo:
                data_by_line = emdfo.readlines()



            with open(effmass_datafile_by_temp,'a+') as emdfo:

                for data_line in range(len(data_by_line)):
                    if temp_step==0:
                        if data_line==0:
                            temp_as_str = 'Temperature '+data_by_line[data_line]

                    else:
                        if data_line==0:
                            continue
                        else:
                            try:

                                emass = numpy.float64(data_by_line[data_line].strip('\n').split()[-1])


                            except Exception,e:
                                print e
                                continue
                            line_write = this_temp + data_by_line[data_line].strip('\n')+'\n'#+' %s\n'%(N_s)
                            emdfo.write(line_write)

        oneCalc['__effmass_counter__']=temp_step
        AFLOWpi.prep._saveOneCalc(oneCalc,ID)

    del oneCalc['__effmass_counter__']
    AFLOWpi.prep._saveOneCalc(oneCalc,ID)

    return oneCalc,ID

def _run_want_dos(__submitNodeName__,oneCalc,ID,dos_range=[-10,10],k_grid=[40,40,40],project=True,num_e=2001,cond_bands=True,fermi_surface=False):
    nscf_ID=ID+'_nscf'

    if AFLOWpi.prep._ConfigSectionMap("run","exec_prefix") != '':
        execPrefix=AFLOWpi.prep._ConfigSectionMap("run","exec_prefix")
    else:
        execPrefix=''

    Efermi = AFLOWpi.retr._getEfermi(oneCalc,nscf_ID,directID=True)
    eShift=float(Efermi)+10.0

    want_dos_calc = AFLOWpi.scfuj.WanT_dos(oneCalc,ID,energy_range=dos_range,k_grid=k_grid,pdos=project,boltzmann=False,num_e=num_e,eShift=eShift,cond_bands=cond_bands,fermi_surface=fermi_surface)


    for want_dos_ID,want_dos in want_dos_calc.iteritems():
        AFLOWpi.run._oneRun(__submitNodeName__,want_dos,want_dos_ID,engine='espresso',calcType='custom',execPath='./want_dos.x',execPrefix=execPrefix,execPostfix='')

        if project==True:
            spin_state = want_dos_ID.split('_')[-1].strip()
            if spin_state=='down':
                AFLOWpi.prep._convert_tb_pdos(oneCalc,ID,-1)    
            if spin_state=='up':
                AFLOWpi.prep._convert_tb_pdos(oneCalc,ID,1)    
            else:
                AFLOWpi.prep._convert_tb_pdos(oneCalc,ID)

    if len(want_dos_calc.keys())>1:
        AFLOWpi.prep._combine_pol_pdos(oneCalc,ID)


    return oneCalc,ID


def _convert_tb_pdos(oneCalc,ID,spin=0):
    
        want_pdos_ext_glob = '_WanT_dos-*.dat'
        

        #change the TB pdos file names so that they can be read by sumpdos
        if spin == -1:
            spin_postfix='_down'
        elif spin == 1:
            spin_postfix='_up'
        else:
            spin_postfix=''

        rename_info_re = re.compile(r'state #\s*(\d*): atom\s*(\d+)\s*\(\s*(\S*)\s*\).*wfc\s*(\d+)\s*\(l=(\d+).*\)\n')
        #first check the QE projwfc.x output for the orbital
        #and species label for each state #
        try:
            qe_pdos_out_str = AFLOWpi.retr._getOutputString(oneCalc,ID+'_pdos')
            state_info_list = rename_info_re.findall(qe_pdos_out_str)
            #if it found the info on the states by their numbers
            if len(state_info_list)!=0:
                for i in range(len(state_info_list)):
                    state_num = int(state_info_list[i][0].strip())
                    atom_num  = state_info_list[i][1].strip()
                    atom_spec = state_info_list[i][2].strip()
                    wfc_num   = state_info_list[i][3].strip()
                    orb_l     = int(state_info_list[i][4].strip())
                    #translate atomic number "l" to orbital name (i.e. s,p,d,f)
                    orb_type=['s','p','d','f']
             
                    #the orig file name from WanT output
                    orig_name = '%s_TB_WanT_dos-%04d.dat'%(ID,state_num)
                    orig_path = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],orig_name)
                    if not os.path.exists(orig_path ):
                        orig_name = '%s_TB_WanT_dos-%04d.dat'%(ID,state_num)
                        orig_path = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],orig_name)
                    #the renamed filename
                    rename = '%s_TB%s.pdos_atm#%s(%s)_wfc#%s(%s)'%(ID,spin_postfix,atom_num,atom_spec,wfc_num,orb_type[orb_l])
                    rename_path = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],rename)
                    #finally we rename it
                    os.rename(orig_path, rename_path)
        except Exception,e:
            AFLOWpi.run._fancy_error_log(e)



def _combine_pol_pdos(oneCalc,ID):
    glob_ID =  AFLOWpi.prep._return_ID(oneCalc,ID,step_type='PAO-TB',last=True,straight=False)
    glob_ID +='_TB'

    glob_ID_up=glob_ID+'_up'
    glob_ID_dn=glob_ID+'_down'

    subdir=oneCalc['_AFLOWPI_FOLDER_']

    pdos_files_up = glob.glob(os.path.join(subdir,'%s.pdos_atm*' % (glob_ID_up)))
    pdos_files_dn = glob.glob(os.path.join(subdir,'%s.pdos_atm*' % (glob_ID_dn)))
                             
    for pdos_file in range(len(pdos_files_up)):
        output_list=[]
        pdos_file_up = pdos_files_up[pdos_file]
        pdos_file_dn = pdos_files_dn[pdos_file]

        with open(pdos_file_up) as pdfuo:
            pdos_string_up = pdfuo.readlines()
        with open(pdos_file_dn) as pdfdo:
            pdos_string_dn = pdfdo.readlines()

        for entry in range(len(pdos_string_up)):
            try:
                entry_up = pdos_string_up[entry].split()
                entry_dn = pdos_string_dn[entry].split()
                energy = entry_up[0]
                val_up = entry_up[1]
                val_dn = entry_dn[1]
            
                output_list.append('%s %s %s' % (energy,val_up,val_dn))
            except:
                pass



        output_str = '\n'.join(output_list)

        input_file_name = os.path.basename(pdos_file_up)
        input_file_name_split = input_file_name.split('.')[-1]
        output_file_name = ID+'_TB.'+input_file_name_split
        output_file_path = os.path.join(subdir,output_file_name)        

        with open(output_file_path,'w') as pdfco:
            pdfco.write(output_str)


class tb_plotter:
	'''
	Class for adding common plotting functions from AFLOWpi.plot module to the high level user 
	interface. 

	'''
	def __init__(self,calcs):
		self.calcs=calcs

	def opdos(self,yLim=[-10,10],runlocal=False,postfix=''):
            AFLOWpi.plot.opdos(self.calcs,yLim=yLim,runlocal=runlocal,postfix=postfix,tight_binding=True)

            calc_type='Plot Orbital Projected DOS of PAO-TB Representation'
            print '                 %s'% (calc_type)




	def bands(self,yLim=[-10,10],DOSPlot='',runlocal=False,postfix=''):
            AFLOWpi.plot.bands(self.calcs,yLim=yLim,DOSPlot=DOSPlot,runlocal=runlocal,postfix=postfix,tight_banding=True)

            calc_type='Plot Electronic Band Structure of PAO-TB Representation'
            if DOSPlot=='DOS':
                    calc_type+=' with Density of States'
            if DOSPlot=='APDOS':
                    calc_type+=' with APDOS'
            print '                 %s'% (calc_type)

	def dos(self,yLim=[-10,10],runlocal=False,postfix=''):
            pass


def _run_tb_ham_prep(__submitNodeName__,oneCalc,ID,unoccupied_bands=True,config=None):
	execPrefix = ''
	execPostfix = ''
        oneCalcID = ID


        def abortIFRuntimeError(subdir, ID):
            outfile = file(os.path.join(subdir, "%s.out"%ID)).read()
            errorList = re.findall(r'from (.*) : error #.*\n',outfile)
            if len(errorList) > 0:        
                logging.error("Error in %s.out -- ABORTING ACBN0 LOOP"%ID)
                print "Error in %s.out -- ABORTING ACBN0 LOOP"%ID                    
                raise SystemExit



        if '__runList__' not in oneCalc.keys():
            oneCalc['__runList__']=[]

            
	if config!=None:
		AFLOWpi.prep._forceGlobalConfigFile(config)
		logging.debug('forced config %s' % config)
	else:
		try:
			config = AFLOWpi.prep._getConfigFile()
			AFLOWpi.prep._forceGlobalConfigFile(config)
		except Exception,e:
			AFLOWpi.run._fancy_error_log(e)


	if AFLOWpi.prep._ConfigSectionMap("run","exec_prefix") != '':
            execPrefix=AFLOWpi.prep._ConfigSectionMap("run","exec_prefix")

	else:
            execPrefix=''


	if AFLOWpi.prep._ConfigSectionMap("run","exec_postfix") != '':
		execPostfix = AFLOWpi.prep._ConfigSectionMap("run","exec_postfix")
	else:
		execPostfix=''


	if AFLOWpi.prep._ConfigSectionMap('run','engine') == '':
		engine = AFLOWpi.prep._ConfigSectionMap('run','engine')
	else:
		engine = 'espresso'


        subdir = oneCalc['_AFLOWPI_FOLDER_']
	oneCalc['_AFLOWPI_CONFIG_']=config

        if 'scf' not in oneCalc['__runList__']:

            try:
                npool=AFLOWpi.retr._get_pool_num(oneCalc,ID)        

                if npool!=1:
                    if len(re.findall(r'npool[s]*\s*(?:\d*)',execPostfix))!=0:
                        execPostfixPrime=re.sub(r'npool[s]*\s*(?:\d*)','npool %s'%npool,execPostfix)
                        logging.debug(execPostfixPrime)

            except Exception,e:
                AFLOWpi.run._fancy_error_log(e)


##################################################################################################################
            AFLOWpi.run._oneRun(__submitNodeName__,oneCalc,ID,execPrefix=execPrefix,execPostfix=execPostfix,engine='espresso',calcType='scf',executable=None)


            oneCalc['__runList__'].append('scf')
            AFLOWpi.prep._saveOneCalc(oneCalc,ID)
            

            nscf_calc,nscf_ID= AFLOWpi.scfuj.nscf_nosym_noinv(oneCalc,ID,1.5,unoccupied_states=unoccupied_bands)	



        else:
            '''if we are restarting from a job killed from going walltime 
            try to load ID_nscf and if we can't then just make a new one'''
            try:
                nscf_ID='%s_nscf' % ID
                nscf_calc = AFLOWpi.prep._loadOneCalc(oneCalc['_AFLOWPI_FOLDER_'],nscf_ID)                
                '''we have to make sure nscf step has the correct walltime and start time if it's a restart'''
                nscf_calc['__walltime_dict__']=oneCalc['__walltime_dict__']
            except Exception,e:
                try:
                    nscf_calc,nscf_ID= AFLOWpi.scfuj.nscf_nosym_noinv(oneCalc,ID,1.5)	

                except Exception,e:
                    AFLOWpi.run._fancy_error_log(e)



##################################################################################################################
        if 'nscf' not in oneCalc['__runList__']:


            try:
                npool=AFLOWpi.retr._get_pool_num(nscf_calc,nscf_ID)        

                if npool!=1:
                    if len(re.findall(r'npool\s*(?:\d+)',execPostfix))!=0:
                        execPostfixPrime=re.sub(r'npool\s*(?:\d+)','npool %s'%npool,execPostfix)
                        logging.debug(execPostfixPrime)

            except Exception,e:
                AFLOWpi.run._fancy_error_log(e)


            AFLOWpi.run._oneRun(__submitNodeName__,nscf_calc,nscf_ID,execPrefix=execPrefix,execPostfix=execPostfix,engine='espresso',calcType='scf',executable=None)
            AFLOWpi.retr._writeEfermi(nscf_calc,nscf_ID)


            abortIFRuntimeError(subdir, nscf_ID)
            AFLOWpi.prep._saveOneCalc(oneCalc,ID)
            oneCalc['__runList__'].append('nscf')
	
##################################################################################################################
        pdos_calc,pdos_ID = AFLOWpi.scfuj.projwfc(oneCalc,ID)


        if not re.match('northo',execPostfix) or not re.match('no',execPostfix):
            execPostfix+=' -northo 1'

        if 'pdos' not in oneCalc['__runList__']:
            pdosPath = os.path.join(AFLOWpi.prep._ConfigSectionMap('prep','engine_dir'),'projwfc.x')

            AFLOWpi.run._oneRun(__submitNodeName__,pdos_calc,pdos_ID,execPrefix=execPrefix,execPostfix=execPostfix,engine='espresso',calcType='custom',executable='projwfc.x',execPath=pdosPath)
#############
            oneCalc['__runList__'].append('pdos')
            AFLOWpi.prep._saveOneCalc(oneCalc,ID)
            abortIFRuntimeError(subdir, pdos_ID)



	eFermi=0.0


        AFLOWpi.prep._form_TB_dir(oneCalc,ID)
	eFermi=10.0

        splitInput = AFLOWpi.retr._splitInput(nscf_calc['_AFLOWPI_INPUT_'])
        del oneCalc['__runList__']
        return oneCalc,ID
#        nbnd = int(splitInput['&system']['nbnd'])





def _clean_want_bands(oneCalc,ID):


    try:
        want_stdout_path = glob.glob(oneCalc['_AFLOWPI_FOLDER_']+'/*_WanT_bands.out')[-1]
    except:
        want_stdout_path = glob.glob(oneCalc['_AFLOWPI_FOLDER_']+'/*_WanT_bands_up.out')[-1]

    with open(want_stdout_path,'r') as in_file_obj:
        in_string = in_file_obj.read()

    path = AFLOWpi.retr._getPath(0.01,oneCalc,ID=ID)

    plot_bool=[]
    path_name=[]
    path_split = [x for x in  path.split('\n')[1:] if len(x.strip())]
    for i in path_split:
        path_name.append(i.split()[-1])
        if  int(i.split()[3]):

            plot_bool.append(True)
        else:
            plot_bool.append(False)

    gg = re.findall("  Number of kpts in each segment\n((?:.*:\W+(?:\d*)\n)*)",in_string)
    num = [int(x) for x in re.findall('line.*:\W+(\d+)',gg[0])]

    total = 0
    include=[]
    #print path_name
    output_path_string = ''
    for i in range(len(num)):
        total+=num[i]+1
        if plot_bool[i]:
            if i==0:
                output_path_string+='%s %s\n' %(path_name[i],num[i])
            else:
                output_path_string+='%s %s\n' %(path_name[i],num[i]+1)
        else:
            output_path_string+='%s %s\n' %(path_name[i],0)
        for j in range(num[i]):
            include.append(plot_bool[i])

        include.append(True)
    #    print print_out
    output_path_string+='%s %s' %(path_name[-1],0)+'\n' 
    
    want_bands_data_path = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_bands_want.dat'%ID)
    if os.path.exists(want_bands_data_path):
        data_file_list=[want_bands_data_path]
    else:
        want_bands_data_path_up = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_bands_want_up.dat'%ID)
        want_bands_data_path_dn = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_bands_want_down.dat'%ID)
        data_file_list=[want_bands_data_path_up,want_bands_data_path_dn,]

    for want_bands_data_path in data_file_list:
        with open(want_bands_data_path,'r') as in_file_obj:
            bands_dat = in_file_obj.read()
        split_bands = bands_dat.split('\n')

        split_data = []
        per_band=[]
        for i in split_bands:
        #    print len(i.strip())
            if not len(i.strip()):
                if len(per_band)!=0:
                    split_data.append(per_band)
                per_band=[]
            else:
                per_band.append(i)


        final_data=''
        for i in range(len(split_data)):
            for j in range(len(split_data[i])):
                if include[j]:
                    final_data+= split_data[i][j]+'\n'

            final_data+='\n'


#        want_bands_data_path_new = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_bands_want.dat'%ID)
        want_bands_data_path_new=want_bands_data_path
        with open(want_bands_data_path_new,'w') as in_file_obj:
            in_file_obj.write(final_data)

