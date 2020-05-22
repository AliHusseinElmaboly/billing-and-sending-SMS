import os
from flask import current_app
from config import Config
from app.settings import config, VIRTUAL_ENV_DIR, PATH_DIR


class Config_App(Config):
	def __init__(self, config_file_name, application_name, user, port, autostart, autorestart, url):
		Config.__init__(self, config_file_name, user, autostart, autorestart)
		self.url = url
		self.port = port

		gunicorn_dir = os.path.join(PATH_DIR, VIRTUAL_ENV_DIR+'gunicorn')
		self.gunicorn_dir = gunicorn_dir

		self.application_name = application_name
		self.config_commands = self.generate_app_commands()



	def generate_command(self):
		command = 'command=' + self.gunicorn_dir + ' -b ' + self.url + ":" + str(self.port) +" "+ config[current_app.config['CONFIG_APP_ENV']]+"_"+self.application_name
		return command

	def generate_app_commands(self):
		app_env_prefix = config[current_app.config['CONFIG_APP_ENV']]
		title ='[program:%s]' %(app_env_prefix + "_" + self.application_name)
		command = self.generate_command()
		directory = "directory= " + self.directory
		user = 'user= ' + str(self.user)
		autostart = 'autostart= ' + str(self.autostart)
		autorestart = 'autorestart= ' + str(self.autorestart)
		stderr_logfile = 'stderr_logfile= ' + os.path.join(self.dir_logfile, "app.error.log")
		stdout_logfile = 'stdout_logfile= ' + os.path.join(self.dir_logfile, "app.out.log")
		result = title + '\n' + command + '\n' + directory + '\n' + user + '\n' + autostart + '\n' + autorestart + '\n' + stderr_logfile + '\n' + stdout_logfile
		return result