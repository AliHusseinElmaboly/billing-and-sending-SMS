import os
from fabric.api import env, local, run, cd
from fabric.context_managers import settings
from app.settings import config, SUPERVISOR_CONFIG_DIR

PROJECT_DIR = '127.0.0.1'
SERVER_PASSWORD = 'BCysSgqpA2uU'

if os.path.exists('.env'):
	print('Importing environment from .env...')
	for line in open('.env'):
		var = line.strip().split('=')
		if len(var) == 2:
			os.environ[var[0]] = var[1]

app_env = os.getenv('APP_CONFIG')
app_env_prefix = config[app_env]

def prod():
	env.hosts =['X.X.X.X'] # replace with IP address or hostname
	env.user = 'user'
	env.password = 'password'

def staging():
	env.hosts = ['192.168.1.198'] # replace with IP address or hostname
	env.user = 'root'
	env.password = 'kitmaker123'


def upgrade_libs():
	run("apt-get update")
	run("apt-get upgrade")


def setup():
	upgrade_libs()
	
	sudo("apt-get install -y build-essential")
	sudo("apt-get install -y git")

	sudo("apt-get install -y python")
	sudo("apt-get install -y python-pip")
	sudo("apt-get install -y python-all-dev")

	with settings(warn_only=True):
		result = run('id deploy')
	if result.failed:
		run("useradd -d /home/deploy/ deploy")
		run("gpasswd -a deploy sudo")

	sudo("chown -R deploy /usr/local/")
	sudo("chown -R deploy /usr/lib/python2.7/")

	run("git config --global credential.helper store")

	with cd("/home/deploy/"):
		run("git clone http://yourgitrepo.com")

	with cd('/home/deploy/webapp'):
		run("pip install -r requirements.txt")
		run("python manage.py createdb")


def deploy():
	test()
	with cd(PROJECT_DIR):
		# run("git pull")
		run("pip install -r requirements.txt")
		# sudo("cp supervisord.conf /etc/supervisor/conf.d/webapp.conf")

	run('service supervisor restart')
	# run('supervisorctl restart all')


# def deploy():
#     with cd(PROJECT_DIR):
#         run('git pull')
#         run('bin source/activate')
#         run('pip install -r requirements.txt')
#         run('touch %s' % WSGI_SCRIPT)


def test():
	# local('python -m unittest discover')
	pass


def cli_send_bill(id_service):
	# fab cli_sernd_bill:14 or fab cli_send_bill:id_service=14,other args
	local('flask --app=cli send_bill -i %s'%id_service)


def cli_send_sms(id_service):
	# fab cli_sernd_sms:14 or fab cli_send_sms:id_service=14,other args
	local('flask --app=cli send_sms -i %s'%id_service)


def grep_all_celery_consumers():
	with settings(host_string=PROJECT_DIR, password=SERVER_PASSWORD):
		run("ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9")

def grep_all_python():
	with settings(host_string=PROJECT_DIR, password=SERVER_PASSWORD):

		run("ps auxww | grep 'python' | awk '{print $2}' | xargs kill -9")


def supervisord_start():
	with settings(host_string=PROJECT_DIR, password=SERVER_PASSWORD):
		run("supervisord")




def supervisorctl_update():
	with settings(host_string=PROJECT_DIR, password=SERVER_PASSWORD):
		run("supervisorctl reread")
		run("supervisorctl update")


def supervisorctl_status(program_name=None):
	with settings(host_string=PROJECT_DIR, password=SERVER_PASSWORD):
		if program_name is None:
			run("supervisorctl status")
		else:
			run("supervisorctl status %s"%program_name)



def supervisorctl_start(program_name=None):
	with settings(host_string=PROJECT_DIR, password=SERVER_PASSWORD):
		if program_name is None:
			print('program_name parameter is Empty')
		else:
			if app_env_prefix in program_name:
				run('supervisorctl start  %s'%program_name)
			else:
				print('program <{0}> cannot start in the configuration setting of <{1}>\nyou have to change the environment to the correct configuation option to start the program'.format(program_name, app_env))



def supervisorctl_restart(program_name=None):
	with settings(host_string=PROJECT_DIR, password=SERVER_PASSWORD):
		if program_name is None:
			print('program_name parameter is Empty')
		else:
			if app_env_prefix in program_name:
				run('supervisorctl restart  %s'%program_name)
			else:
				print('program <{0}> cannot restart in the configuration setting of <{1}>\nyou have to change the environment to the correct configuation optionto restart the program'.format(program_name, app_env))




def supervisorctl_stop(program_name=None):
	with settings(host_string=PROJECT_DIR, password=SERVER_PASSWORD):
		if program_name is None:
			print('program_name parameter is Empty')
		else:
			if app_env_prefix in program_name:
				run('supervisorctl stop %s'%program_name)
			else:
				print('program <{0}> cannot stop in the configuration setting of <{1}>\nyou have to change the environment to the correct configuation option to stop the program'.format(program_name, app_env))




def tail_log(log_file):
	with settings(host_string=PROJECT_DIR, password=SERVER_PASSWORD):
		run('tail -f /var/log/billing_api/{0}/{1}'.format(app_env, log_file))