import pandas as pd
from datetime import datetime, timedelta

from ..mongo_utils import count_tickets

from .constant_utils import ZAMMAD_GROUPS_TO_STD_SECTORS
from .data_cleaning import DataCleaning

       
class Sistemas(DataCleaning):
    def clean_data(self):
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
