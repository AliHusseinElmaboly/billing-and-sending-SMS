from .config_celery import Config_Celery
from .config_flower import Config_Flower
from .config_app import Config_App
from .config import Config
from app.models import db, ConfigFlower, ConfigApp, ConfigCelery
from app.settings import (
	flower_config_name,
	app_config_name,
	celery_bill_config_name,
	celery_sms_config_name,
	bill_service_type, 
	sms_service_type
)


def create_flower_config():
	flower_config = ConfigFlower.query.first()
	remove_config_file(flower_config_name)

	config_flower = Config_Flower(
		flower_config_name, 
		flower_config.celery_name,
		flower_config.user,
		flower_config.port,
		flower_config.autostart,
		flower_config.autorestart,
		flower_config.priority
	)

	config_flower.generate_config_file()	


def create_app_config():
	app_config = ConfigApp.query.first()
	remove_config_file(app_config_name)

	config_app = Config_App(
		app_config_name, 
		app_config.application_name, 
		app_config.user, 
		app_config.port,
		app_config.autostart,
		app_config.autorestart, 
		app_config.url
	)

	config_app.generate_config_file()


def create_celery_bill_config():
	type_config = bill_service_type
	bill_rows = ConfigCelery.query.filter_by(type=type_config).all()
	remove_config_file(celery_bill_config_name)

	for bill_config in bill_rows:
		deploy_celery_config(celery_bill_config_name,bill_config)


def create_celery_sms_config():
	type_config = sms_service_type
	sms_rows = ConfigCelery.query.filter_by(type=type_config).all()

	remove_config_file(celery_sms_config_name)
	for sms_config in sms_rows:
		deploy_celery_config(celery_sms_config_name, sms_config)


def deploy_celery_config(celery_config_name, celery_config):
	config_celery_service = Config_Celery(
		celery_config_name, 
		celery_config.type, 
		celery_config.country_name.replace (" ", "_"), 
		celery_config.carrier_name.replace (" ", "_"), 
		celery_config.id_service, 
		celery_config.min_concurrency, 
		celery_config.max_concurrency, 
		celery_config.celery_name,
		celery_config.user, 
		celery_config.autostart, 
		celery_config.autorestart, 
	)

	config_celery_service.generate_config_file()


def remove_config_file(app_config_name):
	Config.remove_config_file(app_config_name)


def read_config_file(app_config_name):
	return Config.read_config_file(app_config_name)






