import os
from config import Config
from app.settings import config, VIRTUAL_ENV_DIR, PATH_DIR
from flask import current_app

class Config_Celery(Config):
	def __init__(self, config_file_name, type_config, country_name, carrier_name, id_service, min_concurrency, max_concurrency, celery_name, user, autostart, autorestart):
		Config.__init__(self, config_file_name, user, autostart, autorestart)
		self.celery_dir = os.path.join(PATH_DIR, VIRTUAL_ENV_DIR+'celery')

		self.type = type_config
		self.country_name = country_name
		self.carrier_name = carrier_name
		self.id_service = id_service
		self.min_concurrency = min_concurrency
		self.max_concurrency = max_concurrency
		self.celery_name = config[current_app.config['CONFIG_APP_ENV']]+"_"+celery_name
		self.config_commands = self.generate_celery_commands()

	def generate_queue_name(self):
		name_queue = self.type + "_" + self.country_name + "_" + self.carrier_name + "_" + str(self.id_service) 
		return name_queue

	def generate_command(self,name_queue,celery_name):
		name_queue_worker = name_queue +"_worker"
		command = 'command='+self.celery_dir+' -A ' + celery_name + ' worker -Q '+ name_queue +" --autoscale=" + str(self.max_concurrency)+","+ str(self.min_concurrency) +' --loglevel=info '+" -n " + name_queue_worker
		# command = 'command='+self.celery_dir+' -A ' + celery_name + ' worker -Q '+ name_queue +" --autoscale=" + str(self.max_concurrency)+","+ str(self.min_concurrency) + " -n " + name_queue_worker
		return command

	def generate_celery_commands(self):
		name_queue = self.generate_queue_name()
		app_env_prefix = config[current_app.config['CONFIG_APP_ENV']]
		title ='[program:%s]' %(app_env_prefix + "_" + name_queue)
		celery_name = self.celery_name
		command = self.generate_command(name_queue, celery_name)
		directory = 'directory=' + self.directory
		user = 'user=' + self.user
		stdout_logfile = 'stdout_logfile= ' + os.path.join(self.dir_logfile, name_queue + '.log')
		stderr_logfile = 'stderr_logfile= ' + os.path.join(self.dir_logfile, name_queue + '.log')
		autostart = 'autostart= ' + str(self.autostart)
		autorestart = 'autorestart= ' + str(self.autorestart)
		result = title + '\n' + command + '\n' + directory + '\n' + user + '\n' + stdout_logfile + '\n' + stderr_logfile + '\n' + autostart + '\n' + autorestart
		return result

