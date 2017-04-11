from datetime import timedelta
CELERY_TIMEZONE = 'Asia/Shanghai'
from celery.schedules import crontab
CELERYBEAT_SCHEDULE = {
    # Executes every Monday morning at 7:30 A.M
    'add-every-monday-morning': {
            'task': 'main.add',
#            'schedule': crontab(hour=7, minute=30, day_of_week=1),
        'schedule':timedelta(seconds=30),

        },
}


CELERYBEAT_SCHEDULE = ''

