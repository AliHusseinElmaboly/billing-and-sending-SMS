from app import models
from app import sqlalchemy_scheduler_models as models
dse = models.DatabaseSchedulerEntry()
dse.name = 'tasks_23'
dse.task = 'app.tasks.send_bill'
dse.arguments = '[921]'  # json string
dse.keyword_arguments = '{}'  # json string

# crontab defaults to run every minute
dse.crontab = models.CrontabSchedule()
dse.crontab.minute = '14'
dse.crontab.hour = '15'

from app.sqlalchemy_scheduler import dbsession
dbsession.add(dse)
dbsession.commit()


--------------------------------------

from app import models
from app import sqlalchemy_scheduler_models as models
dse = models.DatabaseSchedulerEntry()
dse.name = 'tasks_24'
dse.task = 'app.tasks.send_bill'
dse.arguments = '[91\4\\]'  # json string
dse.keyword_arguments = '{}'  # json string

dse.interval = models.IntervalSchedule()
dse.interval.every = 2
dse.interval.period = 'seconds'


from app.sqlalchemy_scheduler import dbsession
dbsession.add(dse)
dbsession.commit()


# celery -A dev_celery_runner beat -S app.sqlalchemy_scheduler:DatabaseScheduler
celery -A dev_celery_runner beat -S app.api.scheduler.celery_scheduler:DatabaseScheduler

https://github.com/tuomur/celery_sqlalchemy_scheduler




from app import sqlalchemy_scheduler_models as models
dse = models.DatabaseSchedulerEntry()
dse.name = 'tasks'
dse.queue = 'send_sms_queue'
dse.task = 'app.tasks.send_sms'

dse.arguments = '[20]'  # json string
dse.keyword_arguments = '{}'  # json string

dse.interval = models.IntervalSchedule()
dse.interval.every = 1
dse.interval.period = 'seconds'


from app.sqlalchemy_scheduler import dbsession
dbsession.add(dse)
dbsession.commit()


