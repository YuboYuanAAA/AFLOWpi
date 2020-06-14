import os
import json
import logging

class EnvironConfig():
	def __init__(self, mode='setup', configfile=None, projectname=None, setname=None):
		# read from AFLOW config file and save important things
		self.calcs = None
		if mode == 'setup':
			if not projectname:
				print('projectname must be given in setup phase')
				raise Exception()
			if not setname:
				print('setname must be given in setup phase')
				raise Exception()
			if configfile is None:
				print('configfile needs to be given in setup phase')
				raise Exception()
			wpre = ""
			try:
				with open(configfile, 'r') as f:
					for line in f:
						if 'work_dir' in line:
							wpre = line.split()[2].strip()
			except OSError:
				print((os.path.abspath(configfile)))
				print('configfile not found, check directory is set correctly')
				raise Exception
			if wpre[-1] != '/':
				wpre += '/'
			workdir = wpre + projectname + '/' + setname + '/'
			self.config = {}
			self.config['pdict'] = {}
			self.config['workdir'] = workdir

			# by default set to fa-ionic, maybe change
			self.config['solvent'] = 'water'
			self.config['interface'] = 'fa-ionic'
			self.config['diffuse'] = 'none'

		# read from existing environ-config file 
		elif mode == 'run':
			setdir = os.path.abspath(os.path.join(os.getcwd(), '..'))
			# TODO change to onecalc
			with open(os.path.join(setdir, "AFLOWpi", "environ_config.json")) as f:
				self.config = json.load(f)

	def init_calcs(self, calcs):
		self.calcs = calcs
		print(calcs)
		quit()


	def add_loop(self, param, rangelist):
		self.config['pdict']['loopidx'] = 0
		self.config['pdict'][param] = rangelist
		self.config['mode'] = 'loop'
		self.config['param'] = param

	def edit(self, key, val):
		if 'edit' in self.config:
			self.config['edit'].append([key, val])
		else:
			self.config['edit'] = [[key, val]]

	def set_interface(self, interface):
		self.config['interface'] = interface

	def set_diffuse(self, diffuse):
		self.config['diffuse'] = diffuse

	def write_to_file(self):
		oneCalc['__runList__'].append('environ_scf')
		AFLOWpi.prep._saveOneCalc(oneCalc,ID)	
		with open(os.path.join(self.config['workdir'], 'AFLOWpi', 'environ.json'), 'w') as f:
			json.dump(self.config, f, sort_keys=True, indent=4)



def set_params(config):
	astr = ""
	for key, val in list(config.config['pdict'].items()):
		astr += "%s = %s\n"%(str(key), str(val))
	print(('set_params output: %s'%(astr)))
	return astr

def set_workflow(config, mode, execPrefix, execPostfix):
	scfsingle = '''oneCalc, ID = AFLOWpi.environ._run_environ_single(__submitNodeName__, oneCalc, ID,
		mode={}, execPrefix="{}", execPostfix="{}")
oneCalc['__execCounter__']+=1
AFLOWpi.prep._saveOneCalc(oneCalc, ID)'''.format(mode, execPrefix, execPostfix)

	astr = ""
	if 'mode' in config.config and config.config['mode'] == 'loop':
		# 1D loop add to script
		param = config.config['param']
		plist = config.config['pdict'][param]
		for _ in plist:
			astr += ("AFLOWpi.environ.get_environ_input('from_config', loopparam='%s', "
					 "loopval=%s[loopidx], loopidx=loopidx)\n"%(param, param))
			astr += ("loopidx += 1\n")
			astr += scfsingle + '\n'
			astr += ("shutil.copy(ID+'.out', 'STEP_%02d'%loopidx)\n")
	else:
		# no loops
		astr += "AFLOWpi.environ.get_environ_input('from_config')\n"
		astr += scfsingle + '\n'
	print(('set_workflow output: {}'.format(astr)))
	return astr

