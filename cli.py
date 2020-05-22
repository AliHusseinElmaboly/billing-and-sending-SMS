import os
from os import path, environ
from flask import Flask, abort
from flask_cli import FlaskCLI, script_info_option
from app import create_app
from app.extensions import sql, bill, sms
from app.tasks import send_bill_request, send_sms_request
from datetime import datetime, timedelta

# default to dev config
env = os.environ.get('APP_ENV', 'dev')
app = create_app('app.config.%sConfig' % env.capitalize())

FlaskCLI(app)

@app.cli.command()
@script_info_option('-i', '--id_service', script_info_key='bill_service_id')
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

			send_bill_request.apply_async(
				kwargs= {'msisdn':msisdn, 'id_service':id_service},
				queue= queue_name
			)

		app.logger.info('All bills of service : {0} are sent successfully to the broker(Rabbit-MQ)'.format(id_service))

	return


@app.cli.command()
@script_info_option('-i', '--id_service', script_info_key='sms_service_id')
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
			send_sms_request.apply_async(
				kwargs= {'msisdn':msisdn, 'id_sms':id_sms, 'id_service':id_service},
				queue= queue_name
			)

		app.logger.info('All sms of service : {0} are sent successfully to the broker(Rabbit-MQ)'.format(id_service))

	return

if __name__ == '__main__':
	port = int(environ.get("PORT",8080))
	app.run(host='192.168.1.198', port=port, threaded=True)
	