import pandas as pd
from datetime import datetime, timedelta

from ..mongo_utils import count_tickets

from .constant_utils import ZAMMAD_GROUPS_TO_STD_SECTORS
from .data_cleaning import DataCleaning

       
class Sistemas(DataCleaning):

    def clean_data(self, group=None):
        if group:
            # substituing null values for None
            self.tickets['created_at'] = self.tickets['created_at'].map(lambda x: x if x != "null" else None)
            self.tickets['close_at'] = self.tickets['close_at'].map(lambda x: x if x != "null" else None)
            self.tickets['updated_at'] = self.tickets['updated_at'].map(lambda x: x if x != "null" else None)
            
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

    def get_by_state(self):
        
        self.open_tickets_previous = self.closed_tickets_previous = self.closed_tickets_total = 0
        dates_three_months_ago_from_today = pd.period_range(pd.Timestamp.now().to_period('m')-3,freq='M', 
                                                            periods=4).strftime('%Y-%m-%d').tolist()
        last_day_three_months_ago = datetime.strptime(dates_three_months_ago_from_today[0] + " 23:59:59",
                                                    '%Y-%m-%d %H:%M:%S').replace(day=1) - timedelta(days=1)

        # getting keys from values
        zammad_groups = [key for key,value in  ZAMMAD_GROUPS_TO_STD_SECTORS.items() if value == "Sistemas"]
        for group in zammad_groups:
            # getting old open tickets of Sistemas to calculate the acumulados
            self.open_tickets_previous += count_tickets(
                { "$and": [ 
                            {"group": group}, { "created_at": { "$lte": last_day_three_months_ago } } 
                    ] 
                } )
            self.closed_tickets_previous += count_tickets(
                { "$and": [ 
                            {"group": group}, { "close_at": { "$lte": last_day_three_months_ago } } 
                    ] 
                })
            self.closed_tickets_total += count_tickets(
                { "$and": [ 
                            {"group": group}, { "state": "closed" } 
                    ] 
                })


        super().get_by_state(dates_three_months_ago_from_today, self.open_tickets_previous, self.closed_tickets_previous)

    def get_processed_data(self, group=None):
        self.get_data_from_last_four_months()
        self.clean_data(group)
        self.get_by_state()
        self.get_leadtime()
        self.get_satisfaction()