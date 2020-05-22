import os
from app import create_app

if os.path.exists('.env'):
	print('Importing environment from .env...')
	for line in open('.env'):
		var = line.strip().split('=')
		if len(var) == 2:
			os.environ[var[0]] = var[1]


# default to dev config
app_env = os.getenv('APP_CONFIG') or 'default'

application = create_app(app_env)
