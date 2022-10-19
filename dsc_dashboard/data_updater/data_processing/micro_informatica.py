import pandas as pd
from datetime import datetime, timedelta
import pytz

from tickets.models import Ticket

from .data_cleaning import DataCleaning

class MicroInformatica(DataCleaning):
    def clean_data(self):
        super().clean_data()
        self.tickets = self.tickets[self.tickets['group'] == "Micro Informática"]
    
    def get_by_state(self):
        
        dates_three_months_ago_from_today = pd.period_range(pd.Timestamp.now().to_period('m')-3,freq='M', 
                                                            periods=4).strftime('%Y-%m-%d').tolist()
        last_day_three_months_ago = datetime.strptime(dates_three_months_ago_from_today[0] + " 23:59:59",
                                                    '%Y-%m-%d %H:%M:%S').replace(day=1) - timedelta(days=1)

        self.open_tickets_previous = (Ticket.objects.filter(group="Micro Informática") & 
                                      Ticket.objects.filter(created_at__lte=last_day_three_months_ago.replace(tzinfo=pytz.UTC))).count()
        self.closed_tickets_previous = (Ticket.objects.filter(group="Micro Informática") & 
                                      Ticket.objects.filter(close_at__lte=last_day_three_months_ago.replace(tzinfo=pytz.UTC))).count()
        self.closed_tickets_total = (Ticket.objects.filter(group="Micro Informática") & 
                                      Ticket.objects.filter(state="closed")).count()
        
        super().get_by_state(dates_three_months_ago_from_today, self.open_tickets_previous, self.closed_tickets_previous)

    def get_tickets_opened_more_20_days(self):
        super().get_tickets_opened_more_20_days("Micro Informática")
