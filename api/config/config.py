import os
from flask import current_app
from app.settings import config, CONFIG_DIR, LOG_CONFIG_DIR, PATH_DIR

class Config(object):
	def __init__(self, config_file_name, user, autostart, autorestart):
		self.config_file_name = config_file_name
		
		self.directory =  PATH_DIR

		self.user = user

		self.dir_logfile = os.path.join(LOG_CONFIG_DIR, current_app.config['CONFIG_APP_ENV'])

		if autostart == 1:
			self.autostart = True
		else:
			self.autostart = False
		
		if autorestart == 1:
			self.autorestart = True
		else:
			self.autorestart = False
		self.config_commands =""


	def generate_config_file(self):

		app_env_prefix = config[current_app.config['CONFIG_APP_ENV']]

		name_file = app_env_prefix + "_" + self.config_file_name  +".conf"
		
		current_app.logger.info(self.config_file_name+' is created successfuly')

		filepath = os.path.join(PATH_DIR, CONFIG_DIR+name_file)

		# if not os.path.exists(file_dir):
		# 	os.makedirs(file_dir)
		
		file=open(filepath,'a')
		file.write( self.config_commands )
		file.write('\n\n')
		file.close()

	
	@staticmethod
	def remove_config_file(name_file):
		app_env_prefix = config[current_app.config['CONFIG_APP_ENV']]


		name_file = app_env_prefix + "_" + name_file + ".conf"

		filepath = os.path.join(PATH_DIR, CONFIG_DIR+name_file)

		if os.path.exists(filepath ):
			os.remove(filepath)
		else:
			print("Exception : can't remove  %s file." % name_file)


	@staticmethod
	def read_config_file(name_file):
		app_env_prefix = config[current_app.config['CONFIG_APP_ENV']]

		name_file = app_env_prefix + "_" + name_file + ".conf"

		filepath = os.path.join(PATH_DIR, CONFIG_DIR+name_file)

		if os.path.exists(filepath ):
			file = open(filepath, 'r')
			return file.read()
		else:
			print("Exception : can't read %s file." % name_file)


		

