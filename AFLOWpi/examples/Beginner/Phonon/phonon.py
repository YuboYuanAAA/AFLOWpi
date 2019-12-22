import AFLOWpi

# Define the values to the keywords
# in the reference input file
allvars={}
allvars.update(
_AFLOWPI_A_ = ('Si',),
_AFLOWPI_B_ = ('Si',),)
# Create AFLOWpi session
session = AFLOWpi.prep.init('Phonon', 'Si_soun3',
                            config='./phonon.config')
# Generate a calculation set from a reference input file
calcs = session.scfs(allvars,'phonon.ref')
# relax the structure and prepare for Finite Diff. Phonons
#calcs.vcrelax()
calcs.scf()
# calculate one phonon frequency
calcs.phonon(mult_jobs=True,nrx1=2,nrx2=2,nrx3=2,
             innx=1,de=0.01,LOTO=False,disp_sym=True)


calcs.update_cell()
# plot phonon dispersion and DOS
calcs.plot.phonon(postfix='222_inCM',THz=False)
calcs.plot.phonon(postfix='222_THz')
# submit the calcs to run
#calcs.submit()



