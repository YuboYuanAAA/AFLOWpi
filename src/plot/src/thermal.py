import AFLOWpi
import os
from matplotlib import pyplot
from matplotlib import pylab
import numpy
import matplotlib
import StringIO
import logging 




def __plot_gruneisen(oneCalc,ID,optical=False):
	"""
	Function to take the data files generated by the sumpdos ppBands functions and plots the electronic band structure and the projected density of states with energy shifted relative to the Fermi Energy.
	
	Arguments:
              oneCalc (dict): Single calculation that is the value of the dictionary of dictionaries of calculations
              ID (str): ID of the calculation	
	Keyword Arguments:
              postfix (str): Output filename postfix
              THz (bool): Plot the frequencies in THz or cm^-1

        Returns:
              None

	"""
        grun_ID  = AFLOWpi.prep._return_ID(oneCalc,ID,step_type='thermal')
        grun_file_name = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s.phGRUN.gp'%grun_ID)

        with open(grun_file_name,'r') as gpfo:
            grun_data_str = gpfo.read()
        postfix=''
        THz=False


	
	calcCopy = oneCalc
	calcID = ID

        calcID = AFLOWpi.prep._return_ID(oneCalc,calcID,step_type='phonon',last=True)        


	if postfix!='':
		postfix='_'+postfix

	subdir=oneCalc['_AFLOWPI_FOLDER_']
       	fileplot = os.path.join(subdir,'GRUNEISEN_%s_%s%s.pdf' % (AFLOWpi.retr._getStoicName(oneCalc,strip=True),ID,postfix))

	"""get the path to the subdirectory of the calc that you are making plots for"""

#        filebands = os.path.join(subdir,'%s.phBAND.gp'%ID)
        filebands = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s.phGRUN.gp'%grun_ID)
        filedos = os.path.join(subdir,'%s.phDOS.gp'%ID)
        filedos = os.path.join(subdir,'%s.phdos'%ID)

	'''name of file of the DOS plots is dosBandPlot_<_AFLOWPI_PREFIX_>'''
	

       #to set figure size and default fonts
	matplotlib.rc("font", family="serif")      #to set the font type
	matplotlib.rc("font", size=14)             #to set the font size

        
        width = 20
	height = 8
	pylab.figure(figsize=(width, height))#to adjust the figure size
     

	x = []
	y = []
	k_x = []
	k_y = []

	'''
        looks at the filebands file and reads in the columns for the energy of the
        band and the value of the k point to make the path. this looks at the output
        of the plot_bands.x script and when it finds a blank line in the data it 
        appends a list of k point values and energy values for each band into a list
        of the bands
	'''
        #scale for THz or cm^-1
        if THz==True:
            sf=0.0299792458
        else:
            sf=1.0

	try:
                max_val=0.0
                min_val=0.0
		with open(filebands,'r') as datafile:
			data =datafile.readlines()


		for line in data:
                    try:
                        if line.split()[0]==0.0:
                            continue
                        x_val = float(line.split()[0])
                        
                        y_val = [float(z)*sf for z in line.split()[1:]]
                        
                        x.append(x_val)
                        y.append(y_val)
                    except Exception,e:
                        continue

                k_y = numpy.asarray(y).T.tolist()

                for entry in k_y:
                    k_x.append(x)


 	except Exception,e:
 		AFLOWpi.run._fancy_error_log(e)        
 		logging.warning("output from bands calculation not found. Are you sure you ran ppBands and it completed properly?")
 		print "Are you sure you ran ppBands and it completed properly?"
 		return
	'''
        Eliminating the gaps between the paths in band structure plots by looking 
        for gaps in the data in the k point values that are greater than some value
	'''
 	gapThreshold = 2.00

 	for band in range(len(k_x)):
 		for kpoint in range(2,len(k_x[band])):
			if k_x[band][kpoint] - k_x[band][kpoint-1] > (k_x[band][kpoint-1] - k_x[band][kpoint-2])*gapThreshold:
				if k_x[band][kpoint-1] - k_x[band][kpoint-2]!=0:
					difference = k_x[band][kpoint] - k_x[band][kpoint-1]
					higher_vals = k_x[band][kpoint:]
				else:
					difference=0
			
				k_x[band][kpoint:] = [x - difference for x in k_x[band][kpoint:]]
		
				
	a=k_x[1]   # a set of k point values for one band for axis scaling purposes
	b=k_y[1]



        ax1=pylab.subplot(111)	

	'''
        Plot each band (k_x[i]),(k_y[i]) on the band structure plot from list of
        the values of energy and position from their respective list by k points
	'''
        colors =['b','g','c','r','m','y','orange']

	branch_list=['TA',"TA'",'LA','Optical']

	for i in range(len(k_x)):
#	    k_y_prime = [k_y[i][y] for y in range(len(k_y[i])) if not y%10]
#            k_y_prime=k_y[i]

	    k_y_prime = [k_y[i][y] for y in range(len(k_y[i])) if not y%51]
	    k_x_prime = [k_x[i][x] for x in range(len(k_x[i])) if not x%51]
#            k_y_prime=k_y[i]
#            k_x_prime=k_x[i]
	    k_y_prime = numpy.ma.masked_equal(k_y_prime,0.0)


            new_min_val=numpy.amin(k_y_prime)
            new_max_val=numpy.amax(k_y_prime)
            color_choice=colors[i%len(colors)]
	    if optical==False:
		    if i<3:
			    if new_max_val>max_val:
				    max_val=new_max_val
			    if new_min_val<min_val:
				    min_val=new_min_val
	    else:
		    if new_max_val>max_val:
			    max_val=new_max_val
		    if new_min_val<min_val:
			    min_val=new_min_val
				    


#	    k_y_prime = numpy.ma.masked_outside(k_y_prime,-10.0,10.0)

	    if i<3:
 		    pylab.plot(k_x_prime,k_y_prime,color=color_choice,linestyle=' ',marker='^',label=branch_list[i])
	    if optical==True:
		    if i==3:
			    pylab.plot(k_x_prime,k_y_prime,color='k',linestyle=' ',marker='^',label=branch_list[-1])
		    else:
			    pylab.plot(k_x_prime,k_y_prime,color='k',linestyle=' ',marker='^')
		    
#            pylab.plot((k_x[i]),(k_y[i]),color=color_choice)


	    
	pylab.ylabel('$Gr\ddotuneisen$ $parameter$')


	pylab.xlim(min(k_x[1]),max(k_x[1])) 
        
	print min_val,max_val
        pylab.ylim(min_val,max_val) 

	'''
        takes in a list of k points that was used as pw.x input for the 'bands'
        calculation as a string. It puts parts of that string into lists and 
        manipulates them to display the symmetry point boundary lines on the 
        band structure plot
	'''
        ph_band_in = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_matdyn_phBand.in'%ID)
#        print ph_band_in
        with open(ph_band_in,'r') as ph_band_in_file:
            ph_band_in_file_string = ph_band_in_file.read()
        bandSym=ph_band_in_file_string.split('/')[-1]
 	bandSymSplit =  bandSym.split()

 	HSPList = []
 	HSPSymList = []
 	buf = StringIO.StringIO(bandSym)

	for line in buf:
		splitLine = line.split()
		if len(splitLine)==2: # new style kpoint path input case
			HSPList.append(splitLine[1])
			specialPointName = splitLine[0].rstrip()
			
 	                #renames gG to greek letter for capital gamma
			if specialPointName == 'G' or specialPointName == 'g' or specialPointName == 'Gamma' or specialPointName == 'gG':
				specialPointName = r"$\Gamma$"

			elif len(specialPointName) != 1:
				specialPointName = "$"+specialPointName[0]+r'_{'+specialPointName[1]+'}$' #if there is a subscript it makes the print out on the plot have the number subscripted 
			else:
				specialPointName = "$"+specialPointName[0]+"$" #formats with internal math renderer so all the labels look the same
			HSPSymList.append(specialPointName)
			
		elif len(splitLine)==7: # old style kpoint path input case with kpoint names
			HSPList.append(splitLine[3])
			specialPointName = splitLine[4][1:].rstrip()

			if specialPointName == 'G' or specialPointName == 'g' or specialPointName == 'Gamma' or specialPointName == 'gG': #renames gG to greek letter for capital gamma
				specialPointName = r"$\Gamma$"
			elif len(specialPointName) != 1:
				specialPointName = "$"+specialPointName[0]+r'_{'+specialPointName[1]+'}$' #if there is a subscript it makes the print out on the plot have the number subscripted 
			else:
				specialPointName = "$"+specialPointName[0]+"$"  #formats with internal math renderer so all the labels look the same
			HSPSymList.append(specialPointName)                     

		elif len(splitLine)==5: # old style kpoint path input case without kpoint names
			try:
				
				if HSPSymList[-1]!=splitLine[4]:
					HSPList.append(counter)
					HSPSymList.append(splitLine[4])
					counter=1

				else:
					counter+=1
			except Exception,e:
				print e
				counter=1
				HSPSymList.append(splitLine[4])


	'''
        takes the number of k points between each point in the k point paths and
        figures out if they are separate paths (where the end of one path and the 
        next begin have zero k points between them). it also takes the labels for 
        the k points that were in the bands calculation input and creates a list 
        of them and makes a special label for the path boundary e.g. X|Q. All of
        these symmetry lines and symmetry path symbols are put into their own list
        symIndex: for the symmetry line's index in the data set
        symPrint: for the symbols that represent the special symmetry path k points 
	'''

	symIndex = [0]
	totalX =0
	SymPrint = []

	for i in range(len(HSPList)-1):
		if i==0: # for the first k point in the first path
			SymPrint.append(HSPSymList[i])
		if int(HSPList[i]) == 0 and i<len(HSPList)-2: # for the end of a path (where the number of k points between one point and another is zero)
			continue
		elif int(HSPList[i+1]) == 0 and i!=len(HSPList)-2: # for the point that begins a new path where the end of the last path (which has zero k points from it to this k point)
			totalX +=(int(HSPList[i])+1)
			symIndex.append(totalX)
			mid = '|'
			pathBetweenString = HSPSymList[i+1]+mid+HSPSymList[i+2]
			SymPrint.append(pathBetweenString)
		elif int(HSPList[i+1]) != 0: # for kpoints that are not at the beginning or end of paths
			SymPrint.append(HSPSymList[i+1])
			totalX +=int(HSPList[i])
			symIndex.append(totalX)
		elif i==len(HSPList)-2: # for the end of the last path
			symIndex.append(totalX+int(HSPList[i]))
			SymPrint.append(HSPSymList[i+1])
                elif int(HSPList[i-1]) == 0 and int(HSPList[i]) == 0 and i!=len(HSPList)-2:
			logging.debug('can not find HSP in __bandPlot. This shouldnt be able to be tripped')

     #add symmetry lines to the band structure plot
#        print symIndex

	for sym in symIndex:
		try:
			pylab.axvline(a[sym], color = 'k')
		except Exception,e:

                    pass
     #Print path labels to band structure x-axis
	try:
            labs=[]
            for index in range(len(symIndex)):
                if index!=0:
                    labs.append(a[symIndex[index]-1])
                else:
                    labs.append(0)

            pylab.xticks(labs,SymPrint)
	except Exception,e:
#            print 'asdfasdfasdfasdf'
            print e
            pass
    #        return
	pylab.axhline(0.0, color = 'k', linestyle='dashed', linewidth = 1.3) #Femi level line
	locs, labels = pylab.xticks()

##########################################################################################################


        print 'Plotting q resolved Gruneisen Parameter of  %s ' % (AFLOWpi.retr._getStoicName(oneCalc,strip=True))
        logging.info('Plotting q resolved Gruneisen Parameter of %s ' % (AFLOWpi.retr._getStoicName(oneCalc,strip=True)))

#        ax2=pylab.subplot(122)

        try:
                data = open(filedos,'r').readlines()
        except Exception:
                logging.warning("output from dos calculation not found. Are you sure you ran ppDOS and it completed properly?")
                print "Are you sure you ran ppDOS and it completed properly?"
                return
        

        freq_dos=[]
        dos=[]
        plot_dos_x=[]
        for i in range(len(data)):      #convert to floats
            dat = [float(x) for x in data[i].split()]
            freq_dos.append(dat[0]*sf)

            dos.append(dat[1])

        plot_dos_x=[]
        plot_dos_y=[]
        pre_sort=[]
	#smooth the phDOS
	dos = AFLOWpi.plot.__smoothGauss(dos)   
	freq_dos = AFLOWpi.plot.__smoothGauss(freq_dos)   

#        pylab.plot(dos,freq_dos,'k',linestyle='-') #to plot the smoothed data
        pylab.ylim(min_val,max_val) 

#        ax2.spines['bottom'].set_linewidth(1.5)
#        ax2.spines['left'].set_linewidth(1.5)
#        ax2.spines['right'].set_linewidth(1.5)
#        ax2.spines['top'].set_linewidth(1.5)
#        ax1.yaxis.set_ticks([])
#        ax1.xaxis.set_ticks([])
#        ax2.yaxis.set_ticks_position('left')
#        pylab.xlabel('Phonon Density of States (arb. units)')
#        pylab.axhline(0.0, color = 'k', linestyle='dashed', linewidth = 1.3) #Fermi level line


#        ax1.set_position([0.07,0.1,0.67,0.8]) #[left,bottom,width,height]
#        ax2.set_position([0.75,0.1,0.20,0.8])

 	figtitle = '$Gr\ddotuneisen$ $Parameter$: %s' % (AFLOWpi.retr._getStoicName(oneCalc,strip=True)) 
 	t = pylab.gcf().text(0.5,0.92, figtitle,fontsize=14,horizontalalignment='center') #[x,y]

	handles, labels = ax1.get_legend_handles_labels()
	ax1.legend(handles, labels,numpoints=1)

  	matplotlib.pyplot.savefig(fileplot,bbox_inches='tight')

        pyplot.cla()
 	pyplot.clf()
 	pyplot.close()




def __gruneisen_of_omega(oneCalc,ID,projected=True):
    matplotlib.rc("font", size=24)             #to set the font size

    therm_ID  = AFLOWpi.prep._return_ID(oneCalc,ID,step_type='thermal')

    therm_file_name = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s.phSCATTER.gp'%therm_ID)
#    therm_data =numpy.loadtxt(therm_file_name,dtype=numpy.float64,)

    therm_data=[]

    with open(therm_file_name,"r") as fo:
        data = fo.read()

    data=data.split('\n')
    therm_data = numpy.asarray([map(float,x.split()) for x in data if len(x.strip())!=0])
    
    therm_data=numpy.asarray(therm_data)
    therm_data[:,0]=numpy.around(therm_data[:,0],decimals=0)
    therm_data[:,1]=numpy.around(therm_data[:,1],decimals=2)

#    therm_data = numpy.unique(b).view(therm_data.dtype).reshape(-1, therm_data.shape[1])
    
    therm_data  = numpy.vstack({tuple(row) for row in therm_data})
#   therm_data[:,0] = numpy.ma.masked_where(therm_data[:,0] <= 1.0, therm_data, copy=False)
    for i in range(len(therm_data)):
	    if therm_data[i][0]<1.1:
		    therm_data[i][1]=0.0
	    



    therm_data[:,1] = numpy.ma.masked_equal(therm_data[:,1],0.0)
#    therm_data = numpy.ma.masked_equal(therm_data,0.0)
    therm_data[:,1] = numpy.ma.masked_greater(therm_data[:,1],100.0)
#    therm_data[:,0] = numpy.ma.masked_less_equal(therm_data[:,0],1.0)
    print therm_data.shape
    width = 10.0
    height = 8.0
    pylab.figure(figsize=(width, height))#to adjust the figure size
    
    ax1=pylab.subplot(111)	
    pylab.ylabel('$\gamma^{2}$')
    pylab.xlabel('$\omega$ $(cm^{-1})$')
    pylab.plot(therm_data[:,0],therm_data[:,1],'k',linestyle=' ',marker='o',fillstyle='none')

    figtitle = '$Gr\ddotuneisen$ $Parameter:$ %s' % (AFLOWpi.retr._getStoicName(oneCalc,strip=True,latex=True)) 
    t = pylab.gcf().text(0.5,0.92, figtitle,fontsize=24,horizontalalignment='center') #[x,y]
    pylab.xlim([0.0,numpy.amax(therm_data[:,0])])
    fileplot = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'SCATTER_%s_%s.pdf' % (AFLOWpi.retr._getStoicName(oneCalc,strip=True),ID,))
	
    matplotlib.pyplot.savefig(fileplot,bbox_inches='tight')

    pyplot.cla()
    pyplot.clf()
    pyplot.close()

    

# def __plot_thermal_conductivity(oneCalc,ID):

#     therm_ID  = AFLOWpi.prep._return_ID(oneCalc,ID,step_type='thermal')
#     therm_file_name = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_thermal_cond.dat'%therm_ID)

#     with open(therm_file_name,'r') as tcfo:
#         therm_data_str = tcfo.read()


import 	matplotlib.pyplot

def _plot_lattice_TC(oneCalc,ID,temp_range=[80.0,800.0]):

	fname = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],)

	therm_ID  = AFLOWpi.prep._return_ID(oneCalc,ID,step_type='thermal')
	therm_file_name = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],'%s_thermal_cond.dat'%therm_ID)

	data=numpy.loadtxt(therm_file_name, dtype=numpy.float, comments='#',)
	matplotlib.pyplot.plot(data[:,0],data[:,1])

	data_cut = scipy.where(data[0]>temp_range[0] and data[0]<temp_range[1],data)
	max_y = numpy.amax(data_cut[:,1])*1.1
	matplotlib.pyplot.ylim([0.0,max_y])

	matplotlib.pyplot.xlim(temp_range)
	matplotlib.pyplot.xlabel('T (K)')

	figtitle = 'Lattice Thermal Conductivity: %s' % (AFLOWpi.retr._getStoicName(oneCalc,strip=True,latex=True)) 
	t = pylab.gcf().text(0.5,0.92, figtitle,fontsize=14,horizontalalignment='center') #[x,y]

	matplotlib.pyplot.ylabel('$\kappa_{lat}$ $(\frac{W}{m\cdotK})$')


	fig_file_name = os.path.join(oneCalc['_AFLOWPI_FOLDER_'],"LATTICE_TC_%s_%s.pdf"%(AFLOWpi.retr._getStoicName(oneCalc,strip=True),ID))
	matplotlib.pyplot.savefig(fig_file_name,bbox_inches='tight')
