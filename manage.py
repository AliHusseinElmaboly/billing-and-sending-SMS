import os
from flask.ext.script import Manager, Server
from app import create_app
from app.extensions import bill, sms
from app.tasks import send_bill_request, send_sms_request
from datetime import datetime
from app.models import db

from app.api.config.configuration_manager import (
	create_flower_config, 
	create_app_config, 
	create_celery_bill_config,
	create_celery_sms_config
)
from app.settings import config, CONFIG_DIR, SUPERVISOR_CONFIG_DIR 

from fabric.api import env, local, run, cd
from fabric.context_managers import settings




if os.path.exists('.env'):
	print('Importing environment from .env...')
	for line in open('.env'):
		var = line.strip().split('=')
		if len(var) == 2:
			os.environ[var[0]] = var[1]


# default to dev config
config_app_env = os.getenv('APP_CONFIG') or 'default'

app_env_prefix = config[config_app_env]

app = create_app(config_app_env)



manager = Manager(app)
manager.add_command("server", Server('0.0.0.0','5050'))


@manager.option('-i', '--id_service', dest='id_service', default=None)
def send_bill(id_service):
	if id_service is None or id_service == '':
		app.logger.error('no service id --id_servoce=?')
		return 

	if bill.is_avialable_day(id_service):
		rows = bill.get_msisdn(id_service, datetime.utcnow())

		if not rows:
			app.logger.info('no users for service : %s'%id_service)
		
		queue_name = bill.generate_queue_name(id_service)

		app.logger.info('starting sending bills of queue :%s'%	queue_name )

		for row in rows:
			msisdn = row[0]
			print(msisdn)

			send_bill_request.apply_async(
				kwargs= {'msisdn':msisdn, 'id_service':id_service},
				queue= queue_name
			)

	app.logger.info('All bills of service : {0} are sent successfully to the broker(Rabbit-MQ)'.format(id_service))

	return


@manager.option('-i', '--id_service', dest='id_service', default=None)
def send_sms(id_service):
	if id_service is None or id_service == '':
		app.logger.error('no service id --id_service=None')
		return 

	if sms.is_avialable_day(id_service):
		rows = sms.get_msisdn(id_service, datetime.utcnow())

		if not rows:
			app.logger.info('no sms for service : %s'%id_service)
			return 

		app.logger.info('starting sending sms of id_service :%s'%id_service)

		queue_name = sms.generate_queue_name(id_service)

		for row in rows:
			msisdn = row[0]
			id_sms = row[1]
			print('msisdn :{0} , id_sms:{1}'.format(msisdn, id_sms))
			send_sms_request.apply_async(
				kwargs= {'msisdn':msisdn, 'id_sms':id_sms, 'id_service':id_service},
				queue= queue_name
			)

		app.logger.info('All sms of service : {0} are sent successfully to the broker(Rabbit-MQ)'.format(id_service))

	return


# @manager.command
# def send_sms(id_service, num):
# 	if id_service is None or id_service == '':
# 		app.logger.error('no service id --id_service=None')
# 		return 

# 	if sms.is_avialable_day(id_service):
# 		rows = sms.get_msisdn(id_service, datetime.utcnow(), num)

# 		if not rows:
# 			app.logger.info('no sms for service : %s'%id_service)
# 			return 

# 		app.logger.info('starting sending sms of id_service :%s'%id_service)

# 		queue_name = sms.generate_queue_name(id_service)
# 		app.logger.info('create a queue named :%s'%queue_name)

# 		for row in rows:
# 			msisdn = row[0]
# 			id_sms = row[1]
# 			print('msisdn :{0} , id_sms:{1}'.format(msisdn, id_sms))
# 			send_sms_request.apply_async(
# 				kwargs= {'msisdn':msisdn, 'id_sms':id_sms, 'id_service':id_service},
# 				queue= queue_name
# 			)

# 		app.logger.info('All sms of service : {0} are sent successfully to the broker(Rabbit-MQ)'.format(id_service))

# 	return


@manager.command
def create_configuration_files():
	create_flower_config()
	create_app_config()
	create_celery_bill_config()
	create_celery_sms_config()
	file_dir = os.path.abspath(os.path.dirname(app.config['BASE_DIR']))
	config_dir = os.path.join(file_dir, CONFIG_DIR)

	with settings(host_string='localhost', password=app.config['SERVER_PASSWORD']):
		with cd(config_dir):
			for config_file in os.listdir(config_dir):
				if app_env_prefix in config_file:
					run("cp {0} {1}{2}".format(config_file, SUPERVISOR_CONFIG_DIR, config_file))
			return


@manager.shell
def make_shell_context():
	return dict(
		app=app, 
		db=db,
		bill=bill,
		sms=sms
	)

if __name__ == "__main__":
	manager.run()