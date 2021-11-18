from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
import pytz

from .data_zammad import interval_tickets

def start():
    REC = pytz.timezone("America/Recife")
    scheduler = BackgroundScheduler()
    trigger = OrTrigger([CronTrigger(day_of_week='mon-fri',hour='6-18/2',timezone=REC)])
    scheduler.add_job(interval_tickets, trigger)
    scheduler.start()