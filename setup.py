# ***************************************************************************
# *                                                                         *
# *          AFLOWpi - Central Michigan University University, 2017         *
# *                                                                         *
# ***************************************************************************
#
#  Copyright 2017 - Andrew Supka and Marco Fornari - AFLOW.ORG consortium
#
#  This file is part of AFLOW software.
#
#  AFLOW is free software: you can redistribute it and/or modify
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


import sys
import os
from distutils.core import setup, Command,Extension
from distutils.util import change_root, convert_path
from distutils.command.install import install
import shutil
sys.path.append(os.path.curdir)


#os.environ["CC"] = "gcc"
#os.environ["CXX"] = "g++"




ext_modules=[Extension("cints",sources=["src/scfuj/extensions/cints.c"]) ]


import glob
import re
import os
import inspect

orig_dir=os.path.abspath(os.curdir)
def __init__gen(src_folder):


   os.chdir('%s'%src_folder)
   files = glob.glob('./*.py')

   new_file=''

   for i in files:
       try:
           if '__init__'!=i[2:-3]:
               with open(i,'r') as pypy:
                   py_string  = pypy.read()

               file_name=os.path.basename(i)[:-3]

               functions = re.findall(r'^def\s*(\w+)\(.*\):',py_string,re.M)
               for j in functions:
                  new_file+='from  .%s import %s\n'%(file_name,j)

               classes = re.findall(r'^class (\w+)(?:\(.*?\))?:',py_string,re.M)
               for j in classes:
                  new_file+='from  .%s import %s\n'%(file_name,j)

       except Exception,e:
           print 'CRITICAL ERROR DURING GENERATION OF __init__.py' 
           print e
           raise SystemExit

   with open('./__init__.py','w') as initFile:
       initFile.write(new_file)


   os.chdir(orig_dir)

modules=['prep','run','pseudo','plot','retr','plot','aflowlib','db','scfuj',]
for j in modules:
   try:
      os.remove('./src/%s/src/__init__.py'%j)
   except:
      pass

for j in modules:
   try:
      print 'generating ./src/%s/src/__init__.py'%j
      __init__gen('./src/%s/src/'%j)

   except Exception,e:
      print e


for j in modules:
   try:
      os.remove('./src/%s/tests/__init__.py'%j)
   except:
      pass

for j in modules:
   try:

      print 'generating ./src/%s/tests/__init__.py'%j
      __init__gen('./src/%s/tests/'%j)      
   except Exception,e:
      print e




try:
   
   ISOTROPY = glob.glob('src/ISOTROPY/*')

   PAOPY_SRC = glob.glob('src/PAOpy/src/*')
   PAOPY_DEF = glob.glob('src/PAOpy/src/defs/*')

   ACBN0=['scfuj/acbn0_support/integs.py',
          'scfuj/acbn0_support/acbn0.py',
          'scfuj/acbn0_support/Molecule.py',
          'scfuj/acbn0_support/pyints.py',]

   setup(name = "AFLOWpi",
         version = "0.9.9",
         description = "Medium Throughput Framework for Quantum Espresso",
         author = "Andrew Supka,Marco Fornari",
         author_email = "supka1ar@cmich.edu",



         packages = ['AFLOWpi',
                   'AFLOWpi.qe',
                   'AFLOWpi.scfuj',
                   'AFLOWpi.pseudo',
                   'AFLOWpi.run',
                   'AFLOWpi.retr',
                   'AFLOWpi.plot',
                   'AFLOWpi.db',
                   'AFLOWpi.aflowlib',
                   'AFLOWpi.prep'],
         package_dir = {'AFLOWpi'       :'src',
                      'AFLOWpi.qe'      :'src/qe',
                      'AFLOWpi.prep'    :'src/prep/src/',
                      'AFLOWpi.run'     :'src/run/src/',
                      'AFLOWpi.scfuj'   :'src/scfuj/src/',
                      'AFLOWpi.retr'    :'src/retr/src/',
                      'AFLOWpi.plot'    :'src/plot/src/',
                      'AFLOWpi.pseudo'  :'src/pseudo/src/',
                      'AFLOWpi.db'      :'src/db/src/',
                      'AFLOWpi.aflowlib':'src/aflowlib/src/'},


                      
         package_data = {
                                  'AFLOWpi':['ISOTROPY/*','PAOpy/src/*/*','PAOpy/src/*','scfuj/acbn0_support/*'],

                                  },


       ext_modules = ext_modules,
       long_description = """Install Script for AFLOWpi""",) 
   



except Exception,e:
   print e
   print 'Something went wrong...exiting'
   exit



try:
   import AFLOWpi
   FINDSYM_EXEC = os.path.join(AFLOWpi.__path__[0],'ISOTROPY','findsym')
   COMSUBS_EXEC = os.path.join(AFLOWpi.__path__[0],'ISOTROPY','comsubs')
   SMODES_EXEC = os.path.join(AFLOWpi.__path__[0],'ISOTROPY','smodes')



   if not os.access(SMODES_EXEC,3) and not os.access(COMSUBS_EXEC,3) and not os.access(FINDSYM_EXEC,3):
      print "INSTALLING ISOTROPY"
      print
      print 'Setting permission to for the user to read and execute (733) to the ISOTROPY executables findsym, smodes, and comsubs.'
      os.chmod(FINDSYM_EXEC,733)
      os.chmod(COMSUBS_EXEC,733)
      os.chmod(SMODES_EXEC,733)
      print 
      print 'Done.'
      
except Exception,e:
   print 'Could not install ISOTROPY package:',e
   



