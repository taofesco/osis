from celery.schedules import crontab

from backoffice.celery import app as celery_app
from base.business.learning_units.automatic_postponement import fetch_learning_unit_to_postpone, \
    serialize_postponement_results

celery_app.conf.beat_schedule.update({
    'Extend learning units': {
        'task': 'base.tasks.extend_learning_units',
        'schedule': crontab(minute=0, hour=0, day_of_month=15, month_of_year=7)
    },
})


@celery_app.task
def extend_learning_units():
    return serialize_postponement_results(*fetch_learning_unit_to_postpone())
