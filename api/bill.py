from app.api.service import Service
from app.settings import bill_service_type
from app.models import db
from flask import current_app

class Bill(Service):
	def __init__(self):
		Service.__init__(self, bill_service_type)

	def get_msisdn(self, id_service, date):
		db_connection = db.engine.connect()

		user_table = current_app.config['USER_TABLE']

		fmt = '%Y-%m-%d %H:%M:%S %Z'
		date_format = date.strftime(fmt)

		# data = []
		try :
			result = db_connection.execute(
				"""SELECT "msisdn" 
					from {0} 
					WHERE "id_service" = {1} 
					AND "next_try" <= TO_DATE('{2}', 'YYYY-MM-DD HH24:MI:SS') 
					AND "status" = 1 
					ORDER BY "next_try"
				""".format(user_table, id_service, date_format)
			)

		finally:
			db_connection.close()

		return result
