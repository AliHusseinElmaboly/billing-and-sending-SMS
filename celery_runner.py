import os
from app import create_app
from celery import Celery

def make_celery(app):
	celery = Celery(
		app.import_name,
		broker=app.config['CELERY_BROKER_URL'],
		backend=app.config['CELERY_RESULT_BACKEND']
	)
	celery.conf.update(app.config)
	TaskBase = celery.Task

	class ContextTask(TaskBase):
		abstract = True

		def __call__(self, *args, **kwargs):
			with app.app_context():
				return TaskBase.__call__(self, *args, **kwargs)

	celery.Task = ContextTask

	return celery


if os.path.exists('.env'):
	print('Importing environment from .env...')
	for line in open('.env'):
		var = line.strip().split('=')
		if len(var) == 2:
			os.environ[var[0]] = var[1]

env = os.getenv('APP_CONFIG') or 'default'
flask_app = create_app( env )

celery = make_celery(flask_app)
