# ***************************************************************************
# *                                                                         *
# *          AFLOWpi - Central Michigan University University, 2017         *
# *                                                                         *
# ***************************************************************************
#
#  Copyright 2017 - Andrew Supka and Marco Fornari - AFLOW.ORG consortium
#
#  This file is part of AFLOWpi software.
#
#  AFLOWpi is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ***************************************************************************

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
    def __init__(self,calcs,cond_bands=True,proj_thr=0.95,kp_factor=2.0,proj_sh=5.5,tb_kp_mult=4,exec_prefix="",band_mult=1.0):
        self.calcs=calcs
        self.plot=AFLOWpi.prep.tb_plotter(self.calcs)
        self.cond_bands=cond_bands
        self.do_ham=False
        self.step_counter=0
        self.thresh=proj_thr
        self.shift=proj_sh
        self.cond_bands_proj=True

        tb_plotter=AFLOWpi.prep.tb_plotter(calcs)

        AFLOWpi.prep.addToAll_(calcs,'PREPROCESSING',"""oneCalc,ID=AFLOWpi.prep._modifyNamelistPW(oneCalc,ID,'&control','calculation','"scf"')""")
#        AFLOWpi.prep.addToAll_(calcs,'PREPROCESSING',"""AFLOWpi.scfuj._add_paopy_header(oneCalc,ID)""")
        AFLOWpi.scfuj.paopy_header_wrapper(self.calcs,shift_type=1,shift='auto',thresh=proj_thr,tb_kp_mult=tb_kp_mult)
#        AFLOWpi.prep.addToAll_(calcs,'POSTPROCESSING',"""AFLOWpi.scfuj._get_ham_xml(oneCalc,ID)""")

        command='''if oneCalc["__execCounter__"]<=%s:
     oneCalc,ID=AFLOWpi.prep._run_tb_ham_prep(__submitNodeName__,oneCalc,ID,kp_factor=%s,band_factor=%s)
     oneCalc['__execCounter__']+=1
     AFLOWpi.prep._saveOneCalc(oneCalc,ID)'''%(self.step_counter,kp_factor,band_mult)

        AFLOWpi.prep.addToAll_(self.calcs,'RUN',command)
 
        self.step_counter+=1
        command='''if oneCalc["__execCounter__"]<=%s:
     ###_PAOFLOW_SPECIAL_###
     AFLOWpi.scfuj._run_paopy(oneCalc,ID,exec_prefix="%s")
     oneCalc['__execCounter__']+=1
     AFLOWpi.prep._saveOneCalc(oneCalc,ID)'''%(self.step_counter,exec_prefix)

        AFLOWpi.prep.addToAll_(self.calcs,'RUN',command)

#        command='''AFLOWpi.prep._rename_projectability(oneCalc,ID)'''
#        AFLOWpi.prep.addToAll_(self.calcs,'POSTPROCESSING',command)
        self.step_counter+=1
        print 

    def shc(self,s_tensor=None,en_range=[0.05,5.05],de=0.05,spin_texture=False):

        if s_tensor==None:
            s_tensor = [[0,0,0],[0,1,0],[0,2,0],[1,0,0],[1,1,0],[1,2,0],[2,0,0],[2,1,0],[2,2,0], \
                            [0,0,1],[0,1,1],[0,2,1],[1,0,1],[1,1,1],[1,2,1],[2,0,1],[2,1,1],[2,2,1], \
                            [0,0,2],[0,1,2],[0,2,2],[1,0,2],[1,1,2],[1,2,2],[2,0,2],[2,1,2],[2,2,2]]
            s_tensor = [[0,1,2],]


        ne=float(en_range[1]-en_range[0])/de

        if self.step_counter==1:
            self.do_ham=True
        else:
            self.do_ham=False

	AFLOWpi.scfuj.paopy_spin_Hall_wrapper(self.calcs,s_tensor,spin_texture=spin_texture)


        calc_type='Spin Hall Conductivity'
        print AFLOWpi.run._colorize_message('ADDING TB STEP:  ',level='GREEN',show_level=False)+\
                                            AFLOWpi.run._colorize_message(calc_type,level='DEBUG',show_level=False)

        if spin_texture:
            calc_type='Spin Texture'
            print AFLOWpi.run._colorize_message('ADDING TB STEP:  ',level='GREEN',show_level=False)+\
                AFLOWpi.run._colorize_message(calc_type,level='DEBUG',show_level=False)

    def ahc(self,a_tensor=None,en_range=[0.05,5.05],de=0.05):

        # Berry curvature
        if a_tensor==None:
            a_tensor = [[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]]
            a_tensor = [[0,1],]

        ne=float(en_range[1]-en_range[0])/de

        if self.step_counter==1:
            self.do_ham=True
        else:
            self.do_ham=False
	AFLOWpi.scfuj.paopy_Berry_wrapper(self.calcs,a_tensor)



        calc_type='Anomalous Hall Conductivity'
        print AFLOWpi.run._colorize_message('ADDING TB STEP:  ',level='GREEN',show_level=False)+\
                                            AFLOWpi.run._colorize_message(calc_type,level='DEBUG',show_level=False)



    def optical(self,d_tensor=None,en_range=[0.05,5.05],de=0.05):

        if d_tensor==None:
            d_tensor = [[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]]

        ne=float(en_range[1]-en_range[0])/de

        if self.step_counter==1:
            self.do_ham=True
        else:
            self.do_ham=False
	AFLOWpi.scfuj.paopy_optical_wrapper(self.calcs,d_tensor)

        calc_type='Optical Properties'
        print AFLOWpi.run._colorize_message('ADDING TB STEP:  ',level='GREEN',show_level=False)+\
                                            AFLOWpi.run._colorize_message(calc_type,level='DEBUG',show_level=False)





    def transport(self,t_tensor=None,temperature=[300,],en_range=[-5.05,5.05],de=0.05):
        '''
        Wrapper method to call AFLOWpi.scfuj.prep_transport and AFLOWpi.scfuj.run_transport 
        in the high level user interface. Adds a new step to the workflow.



        Arguments:
              self: the _calcs_container object

        Keyword Arguments:
              epsilon (bool): if True episilon tensor will be computed 
              temperature (list): list of temperature(s) at which to calculate transport properties

        Returns:
              None

        '''		

        # Boltzmann transport
        if t_tensor==None:
            t_tensor = [[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]]


        ne=float(en_range[1]-en_range[0])/de
        AFLOWpi.scfuj.paopy_transport_wrapper(self.calcs,t_tensor)

        calc_type='Transport Properties'
        print AFLOWpi.run._colorize_message('ADDING TB STEP:  ',level='GREEN',show_level=False)+\
                                            AFLOWpi.run._colorize_message(calc_type,level='DEBUG',show_level=False)
        ## no temperature parameter for WanT bands so only run 
        ## it once if run_bands=True in the input the method.




    def dos(self,dos_range=[-5.5,5.5],k_grid=None,projected=True,de=0.05,cond_bands=True,fermi_surface=False):

        AFLOWpi.scfuj.paopy_dos_wrapper(self.calcs)
        ne=float(dos_range[1]-dos_range[0])/de

        calc_type='Density of States'
        print AFLOWpi.run._colorize_message('ADDING TB STEP:  ',level='GREEN',show_level=False)+\
                                            AFLOWpi.run._colorize_message(calc_type,level='DEBUG',show_level=False)

        if projected==True:
            AFLOWpi.scfuj.paopy_pdos_wrapper(self.calcs)
            calc_type='Projected Density of States'

            print AFLOWpi.run._colorize_message('ADDING TB STEP:  ',level='GREEN',show_level=False)+\
                AFLOWpi.run._colorize_message(calc_type,level='DEBUG',show_level=False)

            pdos_pp_str="""

try:
    AFLOWpi.prep._convert_tb_pdos(oneCalc,ID)
except: pass
try:
    AFLOWpi.prep._convert_tb_pdos(oneCalc,ID,-1)    
except: pass
try:
    AFLOWpi.prep._convert_tb_pdos(oneCalc,ID,1)    
except: pass
try:
    AFLOWpi.prep._combine_pol_pdos(oneCalc,ID)
except: pass
"""
            AFLOWpi.prep.addToAll_(self.calcs,'POSTPROCESSING',pdos_pp_str)

        if fermi_surface==True:
            calc_type='Fermi Surface'
            print AFLOWpi.run._colorize_message('ADDING TB STEP:  ',level='GREEN',show_level=False)+\
                AFLOWpi.run._colorize_message(calc_type,level='DEBUG',show_level=False)

    def bands(self,nk=1000,nbnd=None,eShift=15.0,cond_bands=True,band_topology=False,fermi_surface=False):

	AFLOWpi.scfuj.paopy_bands_wrapper(self.calcs,band_topology=band_topology,fermi_surface=fermi_surface)

        calc_type='Electronic Band Structure'
        print AFLOWpi.run._colorize_message('ADDING TB STEP:  ',level='GREEN',show_level=False)+\
                                            AFLOWpi.run._colorize_message(calc_type,level='DEBUG',show_level=False)
        if band_topology:
            calc_type='Band Topology'
            print AFLOWpi.run._colorize_message('ADDING TB STEP:  ',level='GREEN',show_level=False)+\
                AFLOWpi.run._colorize_message(calc_type,level='DEBUG',show_level=False)
        if fermi_surface:
            calc_type='Fermi Surface'
            print AFLOWpi.run._colorize_message('ADDING TB STEP:  ',level='GREEN',show_level=False)+\
                AFLOWpi.run._colorize_message(calc_type,level='DEBUG',show_level=False)


def _form_TB_dir(oneCalc,ID,from_ls=True):
    if from_ls:
        AFLOWpi.prep._from_local_scratch(oneCalc,ID,ext_list=['.save'])
#        AFLOWpi.prep._from_local_scratch(oneCalc,ID,ext_list=['.save/atom_proj.dat'],#%oneCalc['_AFLOWPI_PREFIX_']],
#                                         glob=True,first_node_only=True)
#        AFLOWpi.prep._from_local_scratch(oneCalc,ID,ext_list=['.save/data-file.xml'],#%oneCalc['_AFLOWPI_PREFIX_']],
#                                         glob=True,first_node_only=True)
    try:
        save_dir = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],oneCalc['_AFLOWPI_PREFIX_']+'.save')
        TB_dir = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_TB.save'%ID)
        if not os.path.exists(TB_dir):
            os.mkdir(TB_dir)
        data_file_dft = os.path.join(save_dir,'data-file.xml')
        atomic_proj_dat = os.path.join(save_dir,'atomic_proj.xml')
#        atomic_proj_dat = os.path.join(save_dir,'atomic_proj.dat')
        try:
            shutil.copy(data_file_dft,TB_dir)
        except:
            data_file_dft = os.path.join(save_dir,'data-file-schema.xml')
            shutil.copy(data_file_dft,TB_dir)

        shutil.copy(atomic_proj_dat,TB_dir)
    except Exception,e:
        print e


def _run_want_bands(__submitNodeName__,oneCalc,ID,num_points=1000,cond_bands=True,compute_ham=False,proj_thr=0.95,proj_sh=5.5):
    nscf_ID=ID+'_nscf'

    Efermi = AFLOWpi.retr._getEfermi(oneCalc,nscf_ID,directID=True)
    eShift=float(Efermi)+10.0
    
    if AFLOWpi.prep._ConfigSectionMap("run","exec_prefix") != '':
        execPrefix=AFLOWpi.prep._ConfigSectionMap("run","exec_prefix")
    else:
        execPrefix=''

    want_dict = AFLOWpi.scfuj.WanT_bands(oneCalc,ID=ID,eShift=proj_sh,num_points=num_points,cond_bands=cond_bands,compute_ham=compute_ham,proj_thr=proj_thr)



    for want_ID,want_calc in want_dict.iteritems():
        AFLOWpi.run._oneRun(__submitNodeName__,want_calc,want_ID,execPrefix=execPrefix,execPostfix='',engine='espresso',calcType='custom',execPath='./want_bands.x',)

    AFLOWpi.prep._clean_want_bands(oneCalc,ID)

    return oneCalc,ID

def _rename_projectability(oneCalc,ID):
#    nspin = int(AFLOWpi.scfuj.chkSpinCalc(oneCalc,ID))
#    if nspin==2:
        proj_up = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'projectability_dn.txt')
        proj_dn = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'projectability_up.txt')
        try:
            os.rename(proj_dn,proj_dn_new)
        except:
            pass
        proj_dn_new = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_projectability_dn.txt'%ID)
        proj_up_new = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_projectability_up.txt'%ID)        
        try:
            os.rename(proj_up,proj_up_new)
        except:
            pass
        proj = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'projectability.txt')
        proj_new = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_projectability.txt'%ID)
        try:
            os.rename(proj,proj_new)
        except:
            pass

# def _run_want_eff_mass(__submitNodeName__,oneCalc,ID,temperature=[0,800],step=10):
#     nscf_ID=ID+'_nscf'

#     if AFLOWpi.prep._ConfigSectionMap("run","exec_prefix") != '':
#         execPrefix=AFLOWpi.prep._ConfigSectionMap("run","exec_prefix")
#     else:
#         execPrefix=''



#     if '__effmass_counter__' not in oneCalc.keys():
#         #if an old effective mass data file exists delete it before we start
#         effmass_datafile_by_temp = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_WanT_effmass.dat'%ID)
#         if os.path.exists(effmass_datafile_by_temp):
#             os.remove(effmass_datafile_by_temp)
#         #set counter to zero
#         oneCalc['__effmass_counter__']=0
#         AFLOWpi.prep._saveOneCalc(oneCalc,ID)

#     cell_params = AFLOWpi.retr._getCellParams(oneCalc,ID)
#     k_grid = AFLOWpi.prep.getMPGrid(cell_params,offset=True,string=False)
#     try:
#         k_grid = [int(float(x)*10.0) for x in k_grid.split()[:3]]
#     except:
#         k_grid=[20,20,20]

#     Efermi = AFLOWpi.retr._getEfermi(oneCalc,nscf_ID,directID=True)
#     eShift=float(Efermi)+10.0

#     step_holder=step
#     step = (float(temperature[1])-float(temperature[0])+float(step_holder))/float(step)
#     temps = numpy.linspace(float(temperature[0]),float(temperature[1]),step)

#     #some constants
#     h_bar = numpy.float64(1.05457180*10.0**-34.0)
#     k_b   = numpy.float64(1.38064852*10.0**-23.0)
#     m_e   = numpy.float64(9.10938356*10.0**-31.0)

#     sf = numpy.power(k_b*m_e/(2.0*numpy.pi*numpy.power(h_bar,2.0)),(3.0/2.0))#*numpy.power((1.0/cm2m),2.0)


#     for temp_step in range(len(temps)):
#         if temp_step<oneCalc['__effmass_counter__']:
#             continue

#         want_dos_calc = AFLOWpi.scfuj.WanT_dos(oneCalc,ID,k_grid=k_grid,pdos=False,boltzmann=False,eShift=eShift,cond_bands=True,temperature=temps[temp_step])
#         this_temp = '%8.4f ' % float(temps[temp_step])
#         for want_dos_ID,want_dos in want_dos_calc.iteritems():
#             AFLOWpi.run._oneRun(__submitNodeName__,want_dos,want_dos_ID,engine='espresso',calcType='custom',execPath='./effmass.x',execPrefix=execPrefix,execPostfix='')

#             effmass_datafile = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s.dat'%want_dos_ID)
#             effmass_datafile_by_temp = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_WanT_effmass.dat'%ID)
#             with open(effmass_datafile,'r') as emdfo:
#                 data_by_line = emdfo.readlines()



#             with open(effmass_datafile_by_temp,'a+') as emdfo:

#                 for data_line in range(len(data_by_line)):
#                     if temp_step==0:
#                         if data_line==0:
#                             temp_as_str = 'Temperature '+data_by_line[data_line]

#                     else:
#                         if data_line==0:
#                             continue
#                         else:
#                             try:

#                                 emass = numpy.float64(data_by_line[data_line].strip('\n').split()[-1])


#                             except Exception,e:
#                                 print e
#                                 continue
#                             line_write = this_temp + data_by_line[data_line].strip('\n')+'\n'#+' %s\n'%(N_s)
#                             emdfo.write(line_write)

#         oneCalc['__effmass_counter__']=temp_step
#         AFLOWpi.prep._saveOneCalc(oneCalc,ID)

#     del oneCalc['__effmass_counter__']
#     AFLOWpi.prep._saveOneCalc(oneCalc,ID)

#     return oneCalc,ID

def _run_want_dos(__submitNodeName__,oneCalc,ID,dos_range=[-6,6],k_grid=None,project=True,num_e=2001,cond_bands=True,fermi_surface=False,compute_ham=False,proj_thr=0.95,proj_sh=5.5):
    nscf_ID=ID+'_nscf'

    if AFLOWpi.prep._ConfigSectionMap("run","exec_prefix") != '':
        execPrefix=AFLOWpi.prep._ConfigSectionMap("run","exec_prefix")
    else:
        execPrefix=''

    Efermi = AFLOWpi.retr._getEfermi(oneCalc,nscf_ID,directID=True)
#    eShift=float(Efermi)+10.0

    want_dos_calc = AFLOWpi.scfuj.WanT_dos(oneCalc,ID,energy_range=dos_range,k_grid=k_grid,pdos=project,boltzmann=False,num_e=num_e,eShift=proj_sh,cond_bands=cond_bands,fermi_surface=fermi_surface,compute_ham=compute_ham,proj_thr=proj_thr,)


    for want_dos_ID,want_dos in want_dos_calc.iteritems():
        AFLOWpi.run._oneRun(__submitNodeName__,want_dos,want_dos_ID,engine='espresso',calcType='custom',execPath='./want_dos.x',execPrefix=execPrefix,execPostfix='')

        if project==True:
            spin_state = want_dos_ID.split('_')[-1].strip()


    if len(want_dos_calc.keys())>1:
        AFLOWpi.prep._combine_pol_pdos(oneCalc,ID)


    return oneCalc,ID


def _convert_tb_pdos(oneCalc,ID,spin=0):
    
        want_pdos_ext_glob = '_WanT_dos-*.dat'
        

        #change the TB pdos file names so that they can be read by sumpdos
        if spin == -1:
            spin_postfix='_down'
            dat_postfix ='_1'
        elif spin == 1:
            spin_postfix='_up'
            dat_postfix ='_0'
        else:
            spin_postfix=''
            dat_postfix ='_0'


        qe_pdos_out_str = AFLOWpi.retr._getOutputString(oneCalc,ID+'_pdos')
        rename_info_re = re.compile(r'state #\s*(\d*): atom\s*(\d+)\s*\(\s*(\S*)\s*\).*wfc\s*(\d+)\s*\(l=(\d+).*\)\n')

        #first check the QE projwfc.x output for the orbital
        #and species label for each state #

        state_info_list = rename_info_re.findall(qe_pdos_out_str)
        #if it found the info on the states by their numbers
        if len(state_info_list)==0:
            rename_info_re = re.compile(r'state #\s*(\d*): atom\s*(\d+)\s*\(\s*(\S*)\s*\).*wfc\s*(\d+).*l=(\d+).*m_j=([\s-][.\d]+).*\n')
            state_info_list = rename_info_re.findall(qe_pdos_out_str)

        pdos_dict={}
        if len(state_info_list)!=0:
            for i in range(len(state_info_list)):

                    state_num = int(state_info_list[i][0].strip())
                    atom_num  = state_info_list[i][1].strip()
                    atom_spec = state_info_list[i][2].strip()
                    wfc_num   = state_info_list[i][3].strip()
                    orb_l     = int(state_info_list[i][4].strip())
                    try: 
                        orb_m_j     = state_info_list[i][5].strip().replace('-','m')
                    except: orb_m_j=-999
                    #translate atomic number "l" to orbital name (i.e. s,p,d,f)
                    orb_type=['s','p','d','f']

                    #the orig file name from WanT output
                    orig_name = '%d_pdosdk%s.dat'%(state_num-1,dat_postfix)

                    orig_path = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],orig_name)
                    if not os.path.exists(orig_path):
                        orig_name = '%d_pdos%s.dat'%(state_num-1,dat_postfix)
                        orig_path = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],orig_name)
                    #the renamed filename
                    if orb_m_j==-999:
                        new_name = '%s_TB%s.pdos_atm#%s(%s)_wfc#%s(%s)'%(ID,spin_postfix,
                                                                         atom_num,atom_spec,
                                                                         wfc_num,orb_type[orb_l])
                    else:
                        new_name = '%s_TB%s.pdos_atm#%s(%s)_wfc#%s(%s)_%s'%(ID,spin_postfix,atom_num,
                                                                            atom_spec,wfc_num,
                                                                            orb_type[orb_l],orb_m_j)

                    
                    try:
                        pdos_dict[new_name].append(orig_name)
                    except Exception,e:
                        pdos_dict[new_name]=[orig_name]

        for k,v in pdos_dict.iteritems():
            old_name_path = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],v[0])
            dat = numpy.loadtxt(old_name_path)                    
            for i in xrange(1,len(v)):
                old_name_path = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],v[i])
                dat[:,1] += numpy.loadtxt(old_name_path)[:,1]
            new_name_path = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],k)
            numpy.savetxt(new_name_path,dat)






def _combine_pol_pdos(oneCalc,ID):
    glob_ID =  AFLOWpi.prep._return_ID(oneCalc,ID,step_type='PAO-TB',last=True,straight=False)
    glob_ID +='_TB'

    glob_ID_up=glob_ID#+'_up'
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

	def topology(self):
            AFLOWpi.plot.band_topology(self.calcs,yLim=[-10,10],DOSPlot='',runlocal=False,postfix='',tight_banding=False)

            calc_type='Plot Band Topology'
            print '                 %s'% (calc_type)


	def ahc(self):
            addit = "AFLOWpi.plot.__plot_dichroism(oneCalc,ID,spin=False,real=False)"
            AFLOWpi.prep.addToAll_(self.calcs,"PLOT",addit)
            addit = "AFLOWpi.plot.__plot_dichroism(oneCalc,ID,spin=False,real=True)"
            AFLOWpi.prep.addToAll_(self.calcs,"PLOT",addit)
            addit = "AFLOWpi.plot.__plot_berry_cond(oneCalc,ID,spin=False)"
            AFLOWpi.prep.addToAll_(self.calcs,"PLOT",addit)

            calc_type='Plot Anomalous Hall Conductivity'
            print '                 %s'% (calc_type)

	def shc(self):
            addit = "AFLOWpi.plot.__plot_dichroism(oneCalc,ID,spin=True,real=False)"
            AFLOWpi.prep.addToAll_(self.calcs,"PLOT",addit)
            addit = "AFLOWpi.plot.__plot_dichroism(oneCalc,ID,spin=True,real=True)"
            AFLOWpi.prep.addToAll_(self.calcs,"PLOT",addit)
            addit = "AFLOWpi.plot.__plot_berry_cond(oneCalc,ID,spin=True)"
            AFLOWpi.prep.addToAll_(self.calcs,"PLOT",addit)

            calc_type='Plot Spin Hall Conductivity'
            print '                 %s'% (calc_type)

	def opdos(self,yLim=[-5,5],runlocal=False,postfix=''):
            AFLOWpi.plot.opdos(self.calcs,yLim=yLim,runlocal=runlocal,postfix=postfix,tight_binding=True)

            calc_type='Plot Orbital Projected DOS of PAO-TB Representation'
            print '                 %s'% (calc_type)


	def transport(self,runlocal=False,postfix='',x_range=None):
		'''
		Wrapper method to call AFLOWpi.plot.epsilon in the high level user interface.

		Arguments:
		      self: the plotter object

		Keyword Arguments:
		      nm (bool): whether to plot in nanometers for spectrum or eV for energy
		      runlocal (bool): a flag to choose whether or not to run the wrapped function now
	                                or write it to the _ID.py to run during the workflow
		
		Returns:
		      None

		'''

		AFLOWpi.plot.transport_plots(self.calcs,runlocal=runlocal,postfix=postfix,x_range=x_range)
		
		calc_type='Plot Optical and Transport properties'
		print '                 %s'% (calc_type)


	def optical(self,runlocal=False,postfix='',x_range=None):
		'''
		Wrapper method to call AFLOWpi.plot.epsilon in the high level user interface.

		Arguments:
		      self: the plotter object

		Keyword Arguments:
		      nm (bool): whether to plot in nanometers for spectrum or eV for energy
		      runlocal (bool): a flag to choose whether or not to run the wrapped function now
	                                or write it to the _ID.py to run during the workflow
		
		Returns:
		      None

		'''


		AFLOWpi.plot.optical_plots(self.calcs,runlocal=runlocal,postfix=postfix,x_range=x_range)
		
		calc_type='Plot Optical  properties'
		print '                 %s'% (calc_type)



	def bands(self,yLim=[-5,5],DOSPlot='',runlocal=False,postfix=''):
            AFLOWpi.plot.bands(self.calcs,yLim=yLim,DOSPlot=DOSPlot,runlocal=runlocal,postfix=postfix,tight_banding=True)

            calc_type='Plot Electronic Band Structure of PAO-TB Representation'
            if DOSPlot=='DOS':
                    calc_type+=' with Density of States'
            if DOSPlot=='APDOS':
                    calc_type+=' with APDOS'
            print '                 %s'% (calc_type)

	def dos(self,yLim=[-5,5],runlocal=False,postfix=''):
            pass


def _run_tb_ham_prep(__submitNodeName__,oneCalc,ID,config=None,kp_factor=2.0,cond=1,ovp=False,band_factor=1.25):
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
            



            nscf_calc,nscf_ID= AFLOWpi.scfuj.nscf_nosym_noinv(oneCalc,ID,kpFactor=kp_factor,unoccupied_states=cond,band_factor=band_factor)  



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
                    nscf_calc,nscf_ID= AFLOWpi.scfuj.nscf_nosym_noinv(oneCalc,ID,kpFactor=kp_factor,
                                                                      band_factor=band_factor)	

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

            AFLOWpi.run._oneRun(__submitNodeName__,nscf_calc,nscf_ID,execPrefix=execPrefix,
                                execPostfix=execPostfix,engine='espresso',calcType='scf',executable=None)
            AFLOWpi.retr._writeEfermi(nscf_calc,nscf_ID)

            abortIFRuntimeError(subdir, nscf_ID)
            AFLOWpi.prep._saveOneCalc(oneCalc,ID)
            oneCalc['__runList__'].append('nscf')
	
##################################################################################################################
        pdos_calc,pdos_ID = AFLOWpi.scfuj.projwfc(oneCalc,ID,paw=False,ovp=ovp)


        if not re.match('northo',execPostfix) or not re.match('no',execPostfix):
            execPostfix+=' -northo 1'

        execPrefix_LOCAL = AFLOWpi.prep._ConfigSectionMap('run','exec_prefix')
        execPostfix_LOCAL = AFLOWpi.prep._ConfigSectionMap('run','exec_postfix')            
        
        if 'pdos' not in oneCalc['__runList__']:
            pdosPath = os.path.join(AFLOWpi.prep._ConfigSectionMap('prep','engine_dir'),'projwfc.x')

            AFLOWpi.run._oneRun(__submitNodeName__,pdos_calc,pdos_ID,execPrefix=execPrefix,
                                execPostfix=execPostfix,engine='espresso',calcType='custom',
                                executable='projwfc.x',execPath=pdosPath)
#############
            oneCalc['__runList__'].append('pdos')
            AFLOWpi.prep._saveOneCalc(oneCalc,ID)
            abortIFRuntimeError(subdir, pdos_ID)



	eFermi=0.0


        AFLOWpi.prep._form_TB_dir(oneCalc,ID)
	eFermi=10.0

        splitInput = AFLOWpi.retr._splitInput(nscf_calc['_AFLOWPI_INPUT_'])
        del oneCalc['__runList__']

        dos_fermi = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_WanT_dos.efermi'%ID)

        with open(dos_fermi,'w') as ifo:
                ifo.write(str(0.0))

        return oneCalc,ID




def _clean_want_bands(oneCalc,ID):


    try:
        want_stdout_path = glob.glob(oneCalc['_AFLOWPI_FOLDER_']+'/%s_WanT_bands.out'%ID)[-1]
    except:
        want_stdout_path = glob.glob(oneCalc['_AFLOWPI_FOLDER_']+'/%s_WanT_bands_up.out'%ID)[-1]

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
#    num = [int(x) for x in re.findall('line.*:\W+(\d+)',gg[0])]
    num = [int(x) for x in re.findall('line\s*\d+:\s*(\d+)\s*\n',in_string)]
    total = 0
    include=[]
    #print path_name
    output_path_string = ''
    for i in range(len(num)):
        total+=num[i]+1
        try:
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
        except:
            pass
    print include
    #    print print_out
    output_path_string+='%s %s' %(path_name[-1],0)+'\n' 
    
    want_bands_data_path = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_bands_want.dat'%ID)
    if os.path.exists(want_bands_data_path):
        data_file_list=[want_bands_data_path]
    else:
        want_bands_data_path_up = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_bands_want_up.dat'%ID)
        want_bands_data_path_dn = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_bands_want_down.dat'%ID)
        data_file_list=[want_bands_data_path_up,want_bands_data_path_dn,]



    ret_data=[]
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
            
        ret_data.append(final_data)
        want_bands_data_path_new = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],want_bands_data_path[:-4]+'_cleaned.dat')
        print want_bands_data_path_new
#        want_bands_data_path_new=want_bands_data_path
        with open(want_bands_data_path_new,'w') as in_file_obj:
            in_file_obj.write(final_data)

#    return ret_data
#def _get_pp_nawf(oneCalc,ID):
    
