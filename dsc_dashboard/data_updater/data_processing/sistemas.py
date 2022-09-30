import pandas as pd
from datetime import datetime, timedelta
import pytz

from tickets.models import Ticket

from .constant_utils import ZAMMAD_GROUPS_TO_STD_SECTORS
from .data_cleaning import DataCleaning

       
class Sistemas(DataCleaning):

    def clean_data(self, group=None):
        if group:
            
            # converting into pandas date format 
            # and adding an offset to the hour 
            # in order to meet brazilian time
            self.tickets['created_at'] = pd.to_datetime(self.tickets['created_at']) + pd.DateOffset(hours=-3)
            self.tickets['close_at'] = pd.to_datetime(self.tickets['close_at']) + pd.DateOffset(hours=-3)
            self.tickets['updated_at'] = pd.to_datetime(self.tickets['updated_at']) + pd.DateOffset(hours=-3)

            ticket_states_to_portuguese = {
                "closed":"Fechado",
                "open":"Aberto",
                "resolvido":"Resolvido",
                "new":"Novo",
                "aguardando resposta":"Aguardando Resposta",
                "pendente":"Pendente",
                "retorno":"Retorno",
            }

            self.tickets['state'] = self.tickets['state'].map(ticket_states_to_portuguese)
            self.tickets = self.tickets[self.tickets['group'] == group]

        else:
            super().clean_data()
            self.tickets = self.tickets[self.tickets['group'] == "Sistemas"]

    def get_by_state(self, group=None):
        
        self.open_tickets_previous = self.closed_tickets_previous = self.closed_tickets_total = 0
        dates_three_months_ago_from_today = pd.period_range(pd.Timestamp.now().to_period('m')-3,freq='M', 
                                                                periods=4).strftime('%Y-%m-%d').tolist()
        last_day_three_months_ago = datetime.strptime(dates_three_months_ago_from_today[0] + " 23:59:59",
                                                        '%Y-%m-%d %H:%M:%S').replace(day=1) - timedelta(days=1)
        
        if group:
            # getting old open tickets of Sistemas to calculate the acumulados
            self.open_tickets_previous = (Ticket.objects.filter(group=group) & 
                                          Ticket.objects.filter(created_at__lte=last_day_three_months_ago.replace(tzinfo=pytz.UTC))).count()
            self.closed_tickets_previous = (Ticket.objects.filter(group=group) & 
                                            Ticket.objects.filter(close_at__lte=last_day_three_months_ago.replace(tzinfo=pytz.UTC))).count()
            self.closed_tickets_total = (Ticket.objects.filter(group=group) & 
                                            Ticket.objects.filter(state="closed")).count()


            super().get_by_state(dates_three_months_ago_from_today, self.open_tickets_previous, self.closed_tickets_previous)

        else:    
            # getting keys from values
            zammad_groups = [key for key,value in  ZAMMAD_GROUPS_TO_STD_SECTORS.items() if value == "Sistemas"]
            for group_name in zammad_groups:
                # getting old open tickets of Sistemas to calculate the acumulados
                self.open_tickets_previous += (Ticket.objects.filter(group=group_name) & 
                                              Ticket.objects.filter(created_at__lte=last_day_three_months_ago.replace(tzinfo=pytz.UTC))).count()
                self.closed_tickets_previous += (Ticket.objects.filter(group=group_name) & 
                                                Ticket.objects.filter(close_at__lte=last_day_three_months_ago.replace(tzinfo=pytz.UTC))).count()
                self.closed_tickets_total += (Ticket.objects.filter(group=group_name) & 
                                                Ticket.objects.filter(state="closed")).count()


            super().get_by_state(dates_three_months_ago_from_today, self.open_tickets_previous, self.closed_tickets_previous)

    def get_processed_data(self, group=None):
        self.get_data_from_last_four_months()
        self.clean_data(group)
        self.get_by_state(group)
        self.get_leadtime()
        self.get_satisfaction()