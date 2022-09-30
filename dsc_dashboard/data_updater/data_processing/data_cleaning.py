import pandas as pd
import os
import pytz

from datetime import datetime, timedelta

from tickets.models import Ticket

from .constant_utils import AMOUNT_MONTHS_IN_DAYS, MONTH_NUMBER_TO_NAME, ZAMMAD_GROUPS_TO_STD_SECTORS

class DataCleaning:

    def get_data_from_last_four_months(self):
        """
        Get the ticket data.

        Get the last four-month ticket data from the MongoDB.

        Returns
        -------
        tickets : pd.DataFrame
            Pandas Dataframe with the Zammad tickets from MongoDB.
        """ 
        tickets = (Ticket.objects.filter(created_at__gte=(datetime.now() - timedelta(days=AMOUNT_MONTHS_IN_DAYS)).replace(tzinfo=pytz.UTC)) | 
                  Ticket.objects.filter(close_at__gte=(datetime.now() - timedelta(days=AMOUNT_MONTHS_IN_DAYS)).replace(tzinfo=pytz.UTC)))
        
        self.tickets = pd.DataFrame(list(tickets.values()))
    
    def clean_data(self):
        """
        Clean the ticket data.

        Convert MongoDB date into Pandas Datetime,
        map the tickets states.

        Returns
        -------
        tickets : pd.DataFrame
            Pandas Dataframe with the clean data of the Zammad tickets.
        """ 
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
        self.tickets['group'] = self.tickets['group'].map(ZAMMAD_GROUPS_TO_STD_SECTORS)

    
    def get_by_state(self, dates_three_months_ago_from_today, open_tickets_previous, closed_tickets_previous):
        """
        Group data by state.

        Separate the data by states of the tickets, then
        return the grouped data.

        Parameters
        ----------
        tickets : pd.DataFrame
            Pandas Dataframe with the clean data of the Zammad tickets.
        DATES_FROM_LAST_FOUR_MONTHS : list of str
            List of strings that represent the date of the last 4 months.

        Returns
        -------
        estados : pd.DataFrame
            Pandas Dataframe the amount of tickets grouped by ticket states
            and month of the year (last four months).
        abertos_mes_atual : int
            Integer that represents how many open tickets the current months has.
        fechados_mes_atual : int
            Integer that represents how many closed tickets the current months has.
        total_fechados : int
            Integer that represents the number of tickets that 
            was closed.
        acumulados : int
            Integer represents the number of tickets that is still open.
        """
        # open tickets
        open_tickets = self.tickets.copy(deep=True)
        open_tickets = open_tickets[(open_tickets['created_at'] <= pd.to_datetime(datetime.now(), unit="ns", utc=True))]
        open_tickets = open_tickets[['created_at', 'state', 'id']]
        
        open_dict = {}
        for date in dates_three_months_ago_from_today:
            date_aux = pd.to_datetime(date).date().strftime('%y-%m')
            open_dict[
                    MONTH_NUMBER_TO_NAME[int(date_aux.split('-')[1])] + '/' +  date_aux.split('-')[0]
                ] = open_tickets[
                            (open_tickets['created_at'].dt.month == pd.to_datetime(date).month)
                        ]['id'].count()

        open_tickets = pd.DataFrame(open_dict.values(), index=open_dict.keys(), columns=['qnt'])
        open_tickets.index.name = 'mes/ano'

        self.open_tickets_current_month = open_tickets['qnt'][-1]
        
        # closed tickets
        closed_tickets = self.tickets.copy(deep=True)
        closed_tickets = closed_tickets[(closed_tickets['close_at'] <= pd.to_datetime(datetime.now(), unit="ns", utc=True)) & (closed_tickets['state'] == "Fechado")]
        closed_tickets = closed_tickets[['close_at', 'state', 'id']]
        
        closed_dict = {}
        for date in dates_three_months_ago_from_today:
            date_aux = pd.to_datetime(date).date().strftime('%y-%m')
            closed_dict[
                    MONTH_NUMBER_TO_NAME[int(date_aux.split('-')[1])] + '/' +  date_aux.split('-')[0]
                ] = closed_tickets[
                            (closed_tickets['close_at'].dt.month == pd.to_datetime(date).month)
                        ]['id'].count()
        
        closed_tickets = pd.DataFrame(closed_dict.values(), index=closed_dict.keys(), columns=['qnt'])
        closed_tickets.index.name = 'mes/ano'
        
        self.closed_tickets_current_month = closed_tickets['qnt'][-1]
        
        # accumulated
        accumulated_tickets = open_tickets.copy(deep=True)
        accumulated_tickets.iloc[0, 0] += open_tickets_previous - (closed_tickets.iloc[0, 0] + closed_tickets_previous)
        
        for i in range(1, len(dates_three_months_ago_from_today)):
            accumulated_tickets.iloc[i, 0] += accumulated_tickets.iloc[i - 1, 0] - closed_tickets.iloc[i, 0]

        self.num_accumulated_tickets = accumulated_tickets['qnt'][-1]

        # COMPLETE DATAFRAME
        self.num_tickets_by_state = pd.merge(open_tickets,closed_tickets, on='mes/ano',how='inner')
        self.num_tickets_by_state = pd.merge(self.num_tickets_by_state,accumulated_tickets, on='mes/ano',how='inner')
        self.num_tickets_by_state.columns = ['abertos', 'fechados', 'acumulados']    
    
    
    def get_leadtime(self):
        self.leadtime_scatter_plot = self.tickets.copy(deep=True)
        self.leadtime_scatter_plot = self.leadtime_scatter_plot.dropna(axis=0, subset=['close_at'])
        
        self.leadtime_scatter_plot = self.leadtime_scatter_plot[self.leadtime_scatter_plot['state'] == 'Fechado']
        self.leadtime_scatter_plot = self.leadtime_scatter_plot[['number','state', 'group', 'created_at', 'close_at']]
        
        # keeping tickets from last 6 months only
        self.leadtime_scatter_plot = self.leadtime_scatter_plot[self.leadtime_scatter_plot['close_at'] > pd.to_datetime(datetime.now() - timedelta(days=210), unit="ns", utc=True)]

        self.leadtime_scatter_plot['diff'] = self.leadtime_scatter_plot['close_at'] - self.leadtime_scatter_plot['created_at']
        self.leadtime_scatter_plot['diff'] = self.leadtime_scatter_plot['diff'].astype('timedelta64[h]')

        self.leadtime_scatter_plot["mes/ano"] = self.leadtime_scatter_plot['close_at'].dt.strftime('%y-%m')
        self.leadtime_scatter_plot = self.leadtime_scatter_plot.sort_values(by='mes/ano').reset_index(drop=True)
        self.leadtime_scatter_plot["mes/ano"] = self.leadtime_scatter_plot["mes/ano"].apply(lambda x: MONTH_NUMBER_TO_NAME[int(x.split('-')[1])] + '/' + x.split('-')[0])

        self.leadtime_scatter_plot['diff'] = self.leadtime_scatter_plot['diff']/24
        self.leadtime_scatter_plot['diff'] = self.leadtime_scatter_plot['diff'].astype(int)

        self.leadtime_bar_plot = pd.DataFrame.from_dict({"mes/ano":self.leadtime_scatter_plot['close_at'].dt.strftime('%y-%m'), "diff": self.leadtime_scatter_plot['diff']})

        self.leadtime_bar_plot = self.leadtime_bar_plot.groupby(['mes/ano']).mean().reset_index()
        self.leadtime_bar_plot['mes/ano'] = self.leadtime_bar_plot['mes/ano'].apply(lambda x: MONTH_NUMBER_TO_NAME[int(x.split('-')[1])] + '/' + x.split('-')[0])
        self.leadtime_bar_plot['diff'] = self.leadtime_bar_plot['diff'].astype(int)

    def get_satisfaction(self):
        """
        Get the customers' satisfaction data.

        Get the customers' satisfaction data from the
        Google Forms.

        Returns
        -------
        tickets_satisfacao : pd.DataFrame
            Pandas Dataframe with the customers' satisfaction
            information.
        """
        satisfaction_customers_aux = self.tickets.copy(deep=True)
        
        url = f"https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEET_ID')}/gviz/tq?tqx=out:csv&sheet={os.getenv('GOOGLE_SHEET_NAME')}"
        tickets_aux = pd.read_csv(url)
        score_column = tickets_aux.columns[1]
        ticket_number_column = tickets_aux.columns[-1]
        tickets_aux = tickets_aux.drop_duplicates(subset=ticket_number_column, keep="last")
        self.satisfaction_customers = pd.DataFrame(None, index =[0,1,2,3,4,5,6,7,8,9,10], columns =['qnt'])

        satisfaction_customers_aux['number'], tickets_aux[ticket_number_column] = satisfaction_customers_aux['number'].astype(str), tickets_aux[ticket_number_column].astype(str)
        satisfaction_customers_aux = pd.merge(satisfaction_customers_aux, tickets_aux, left_on='number', right_on=ticket_number_column,how='inner')
        
        self.satisfaction_customers['qnt'] = self.satisfaction_customers.index.map(satisfaction_customers_aux[score_column].value_counts()).fillna(0).astype(int)
        self.satisfaction_customers['percentage'] = self.satisfaction_customers.index.map(satisfaction_customers_aux[score_column].value_counts(normalize=True) * 100).fillna(0).astype(float)

    def get_processed_data(self):
        self.get_data_from_last_four_months()
        self.clean_data()
        self.get_by_state()
        self.get_leadtime()
        self.get_satisfaction()
