from celery import shared_task
from .views import check_trial_period

@shared_task
def check_trial_periods():
    check_trial_period()
