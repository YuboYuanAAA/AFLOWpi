import AFLOWpi.prep
import os
import numpy as np 

def _run_paopy(oneCalc,ID):
    paopy_path = os.path.join(AFLOWpi.__path__[0],'PAOpy/src','test.py')
    exec_prefix=''
    paopy_output = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_PAOpy.out'%ID)
#    paopy_input = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'inputfile.py')
    paopy_input = 'inputfile.py'
    try:
        command = '%s python %s %s > %s' % (exec_prefix,paopy_path,paopy_input,paopy_output)
        print command
        os.system(command)
    except Exception,e:
        print e



    


def paopy_header_wrapper(calcs,shift_type=1,shift='auto',thresh=0.90,tb_kp_mult=4):
    content = """AFLOWpi.scfuj._add_paopy_header(oneCalc,ID,shift_type=%s,shift='auto',thresh=%s,tb_kp_mult=%s)""" % \
        (shift_type,thresh,tb_kp_mult)
        
    AFLOWpi.prep.addToAll_(calcs,'PREPROCESSING',content)

def paopy_dos_wrapper(calcs):
    AFLOWpi.prep.addToAll_(calcs,'PREPROCESSING',"""AFLOWpi.scfuj._add_paopy_dos(oneCalc,ID)""")

def paopy_pdos_wrapper(calcs):
    AFLOWpi.prep.addToAll_(calcs,'PREPROCESSING',"""AFLOWpi.scfuj._add_paopy_pdos(oneCalc,ID)""")

def paopy_bands_wrapper(calcs):
    AFLOWpi.prep.addToAll_(calcs,'PREPROCESSING',"""AFLOWpi.scfuj._add_paopy_bands(oneCalc,ID)""")

def paopy_transport_wrapper(calcs):
        AFLOWpi.prep.addToAll_(calcs,'PREPROCESSING',"""AFLOWpi.scfuj._add_paopy_transport(oneCalc,ID)""")

def paopy_optical_wrapper(calcs):
        AFLOWpi.prep.addToAll_(calcs,'PREPROCESSING',"""AFLOWpi.scfuj._add_paopy_optical(oneCalc,ID)""")

def paopy_acbn0_wrapper(calcs):
    pass


def _add_paopy_header(oneCalc,ID,shift_type=1,shift='auto',thresh=0.90,tb_kp_mult=4,acbn0=False,ovp=False):
    
    paopy_input = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'inputfile.py')
    ibrav=int(AFLOWpi.retr._splitInput(oneCalc['_AFLOWPI_INPUT_'])['&system']['ibrav'])

    nk1,nk2,nk3 = AFLOWpi.scfuj._mult_kgrid(oneCalc,mult=tb_kp_mult)


    with open(paopy_input,'w') as ifo:
        ifo.write('fpath = "%s_TB.save"\n'%ID)
        if shift=="auto":
            ifo.write('shift="auto"\n')
        else:
            ifo.write('shift=%s\n'%shift)
        ifo.write('shift_type = %s\n'%shift_type)
        ifo.write('ibrav = %s\n'%ibrav)
        ifo.write('pthr = %s\n'%thresh)
        ifo.write('verbose = True\n')
        if float(tb_kp_mult)!=1.0:
            ifo.write('double_grid = True\n')
            ifo.write('nfft1 = %s\n'%nk1)
            ifo.write('nfft2 = %s\n'%nk2)
            ifo.write('nfft3 = %s\n'%nk3)
        if acbn0==True:
            ifo.write('write2file = True\n')
            ifo.write('write_binary = True\n')
        if ovp==True:
            ifo.write('non_ortho = True\n')
def _add_paopy_dos(oneCalc,ID):
    paopy_input = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'inputfile.py')
    with open(paopy_input,'a') as ifo:
        ifo.write('do_dos = True\n')
        ifo.write('delta = 0.05\n')
        ifo.write('emin = -10.0\n')
        ifo.write('emax =  10.0\n')
def _add_paopy_pdos(oneCalc,ID):
    paopy_input = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'inputfile.py')
    with open(paopy_input,'a') as ifo:
        ifo.write('do_pdos = True\n')
        ifo.write('delta = 0.05\n')
        ifo.write('delta = 0.05\n')
        ifo.write('emin = -10.0\n')
        ifo.write('emax =  10.0\n')

def _add_paopy_bands(oneCalc,ID,nk=5000):
    dk = AFLOWpi.retr._getPath_nk2dk(nk, oneCalc,ID=ID)
    paopy_input = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'inputfile.py')
    with open(paopy_input,'a') as ifo:
        ifo.write('do_bands = True\n')
        ifo.write('nk = 5000\n')

def _add_paopy_transport(oneCalc,ID):
    paopy_input = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'inputfile.py')
    with open(paopy_input,'a') as ifo:
        ifo.write('Boltzmann = True\n')
    



def _add_paopy_optical(oneCalc,ID):
    paopy_input = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'inputfile.py')
    with open(paopy_input,'a') as ifo:
        ifo.write('epsilon = True\n')
    
    





def _mult_kgrid(oneCalc,mult=5.0):

    inputDict=AFLOWpi.retr._splitInput(oneCalc['_AFLOWPI_INPUT_'])
    kpt_str  = inputDict['K_POINTS']['__content__']    
    k_grid = [int(np.ceil(float(x)*mult)) for x in kpt_str.split()[:3]]

    return k_grid[0],k_grid[1],k_grid[2]
    

    
