from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
import pytz

from .data_zammad import interval_tickets, all_tickets

def start():
    """
    Call :func:`interval_tickets` periodically.

    Update periodically the data for the dashboard, this
    routine runs in background, from Monday through Friday,
    every two hours from 6am to 6pm, based on America/Recife
    timezone.
    """
    REC = pytz.timezone("America/Recife")
    scheduler = BackgroundScheduler()
    trigger = OrTrigger([CronTrigger(day_of_week='mon-fri',hour='6-18/2',timezone=REC)])
    scheduler.add_job(all_tickets, trigger)
    #trigger2 = OrTrigger([CronTrigger(day_of_week='sat',hour='23',timezone=REC)])
    #scheduler.add_job(all_tickets, trigger2)
    scheduler.start()