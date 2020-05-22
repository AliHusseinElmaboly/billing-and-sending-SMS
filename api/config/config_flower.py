import os
from flask import current_app
from os import path, environ
from config import Config
from app.settings import config, VIRTUAL_ENV_DIR, PATH_DIR

class Config_Flower(Config):
	def __init__(self, config_file_name, celery_name, user, port, autostart, autorestart, priority):
		Config.__init__(self, config_file_name, user, autostart, autorestart)
		
		self.celery_dir = os.path.join(PATH_DIR, VIRTUAL_ENV_DIR+'celery')

		self.celery_name = config[current_app.config['CONFIG_APP_ENV']]+"_"+celery_name
		self.port = port
		self.priority = priority

		self.config_commands = self.generate_flower_commands()


	def generate_command(self):
		command = 'command='+ self.celery_dir + ' -A ' + self.celery_name + ' flower ' + " --port=" + current_app.config['CELERY_FLOWER_PORT'] + " --broker=" +current_app.config['CELERY_BROKER_URL']
		return command


	def generate_flower_commands(self):
		app_env_prefix = config[current_app.config['CONFIG_APP_ENV']]
		title ='[program:%s_celery_flower]'%app_env_prefix
		command = self.generate_command()
		directory = 'directory=' + self.directory
		autostart = 'autostart= ' + str(self.autostart)
		autorestart = 'autorestart= ' + str(self.autorestart)
		stdout_logfile = 'stdout_logfile= ' + os.path.join(self.dir_logfile, "flower.err.log")
		stderr_logfile = 'stderr_logfile= ' + os.path.join( self.dir_logfile, "flower.out.log")
		priority = "priority="+str(self.priority)
		result = title + '\n' + command + '\n' + directory + '\n' + autostart + '\n' + autorestart + '\n' + stderr_logfile + '\n' + stdout_logfile + '\n' + priority
		return result

