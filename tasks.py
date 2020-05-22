import requests
import cx_Oracle
from app.extensions import celery, bill, sms
from celery import Task, states, current_app
from celery.utils.log import get_task_logger
from celery.exceptions import Ignore, MaxRetriesExceededError
from datetime import datetime, timedelta
from celery.result import AsyncResult
from requests.exceptions import ConnectionError, Timeout, HTTPError, TooManyRedirects, RequestException
from celery import group

logger = get_task_logger(__name__)

class CallbackTask(Task):

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		error_msg = 'Task Failed : {0} id {1}, args: {2}, kwargs: {3}, error message: {4}'.format(self.name, task_id,args, kwargs, exc)
		logger.warn(error_msg)


@celery.task(
	bind=True,
	ignore_result=True,
	default_retry_delay= 3,
	max_retries=10)
def send_bill(self, id_service):
	logger.info('Executing task:send_bill id {0.id}, args: {0.args!r} kwargs: {0.kwargs!r}'.format( self.request))
	
	if id_service is None or id_service == '':
		logger.warn('no service id --id_servoce=?')
		return 

	try:
		if bill.is_avialable_day(id_service):
			
			bill_count = bill.get_msisdn_count(id_service, datetime.utcnow())
			if bill_count == 0:
				logger.info('no users for service : %s'%id_service)
				return
			
			rows = bill.get_msisdn(id_service, datetime.utcnow())

			queue_name = bill.generate_queue_name(id_service)
			logger.info('starting sending bills(bill_count: {0}) of id_service: {1} to queue: {2}'.format(bill_count, id_service, queue_name))

			for row in rows:
				msisdn = row[0]
				logger.info('send_bill : args (msisdn : {0}, id_service : {1})'.format(msisdn, id_service))

				send_bill_request.apply_async(
					kwargs= {'msisdn':msisdn, 'id_service':id_service},
					queue= queue_name
				)


			logger.info('All bills of service : {0} are sent successfully to the broker(Rabbit-MQ)'.format(id_service))

		return
	except Exception as e:

		try:
			logger.info('Database connection error:{0}, Retry Task:send_bill id {1.id}, args: {1.args!r} kwargs: {1.kwargs!r}'.format( e, self.request))
			self.retry()
		except MaxRetriesExceededError, e:
			logger.info('Exceed Max retries of task:send_bill id {0.id}, args: {0.args!r} kwargs: {0.kwargs!r}'.format( self.request))


@celery.task(
	bind=True,
	ignore_result=True,
	default_retry_delay= 3,
	max_retries=10)
def send_sms(self, id_service):
	logger.info('Executing task:send_sms id {0.id}, args: {0.args!r} kwargs: {0.kwargs!r}'.format( self.request))

	if id_service is None or id_service == '':
		logger.warn('no service id --id_service=None')
		return 

	try:
		if sms.is_avialable_day(id_service):
			sms_count = sms.get_msisdn_count(id_service, datetime.utcnow())

			if sms_count == 0:
				logger.info('no sms for service : %s'%id_service)
				return 

			rows = sms.get_msisdn(id_service, datetime.utcnow())

			queue_name = sms.generate_queue_name(id_service)
			logger.info('starting sending sms(sms_count: {0}) of id_service: {1} to queue:{2}'.format(sms_count, id_service, queue_name))

			for row in rows:
				msisdn = row[0]
				id_sms = row[1]
				logger.info('send_sms : args (msisdn : {0}, id_sms : {1}, id_service : {2})'.format(msisdn, id_sms, id_service))

				send_sms_request.apply_async(
					kwargs= {'msisdn':msisdn, 'id_sms':id_sms, 'id_service':id_service},
					queue= queue_name
				)

			logger.info('All sms of service : {0} are sent successfully to the broker(Rabbit-MQ)'.format(id_service))

		return
	except Exception as e:
			try:
				logger.info('Database connection error:{0}, Retry Task:send_sms id {1.id}, args: {1.args!r} kwargs: {1.kwargs!r}'.format( e, self.request))
				self.retry()
			except MaxRetriesExceededError:
				logger.info('Exceed Max retries of task:send_sms id {0.id}, args: {0.args!r} kwargs: {0.kwargs!r}'.format( self.request))


@celery.task(
	bind=True, 
	base=CallbackTask, 	
	ignore_result=True, 
	throws=(ConnectionError, Timeout, HTTPError, TooManyRedirects, RequestException)
	)
def send_bill_request(self, msisdn, id_service):
	logger.info('Executing task:send_bill_request id {0.id}, args: {0.args!r} kwargs: {0.kwargs!r}'.format( self.request))
	send_bill_url = current_app.conf.SEND_BILL_URL
	url = send_bill_url.format(msisdn, id_service)
	logger.info('url:%s'%url)

	r = requests.get(url)

	logger.info("task result:send_bill_request id {0.id}, kwargs: {0.kwargs!r}"\
				"\nresponse status_code: {1}\nresponse headers: {2}\nresponse content: {3}".format(self.request ,r.status_code, r.headers, r.content))
	if r.status_code != requests.codes.ok:
		r.raise_for_status()
		
	result  = "status_code: {0}, {1.kwargs!r}".format(r.status_code, self.request )
	return result


@celery.task(
	bind=True, 
	base=CallbackTask, 
	ignore_result=True,
	throws=(ConnectionError, Timeout, HTTPError, TooManyRedirects, RequestException)
	)
def send_sms_request(self, msisdn, id_sms, id_service):
	logger.info('Executing task:send_sms_request id {0.id}, args: {0.args!r} kwargs: {0.kwargs!r}'.format( self.request))
	send_sms_url = current_app.conf.SEND_SMS_URL
	url = send_sms_url.format(msisdn, id_service, id_sms)
	logger.info('url:%s'%url)

	r = requests.get(url)
	

	logger.info("task result:send_sms_request id {0.id}, kwargs: {0.kwargs!r}"\
			"\nresponse status_code: {1}\nresponse headers: {2}\nresponse content: {3}".format(self.request ,r.status_code, r.headers, r.content))
	if r.status_code != requests.codes.ok:
		r.raise_for_status()
	
	result  = "status_code: {0}, {1.kwargs!r}".format(r.status_code, self.request )
	return result
