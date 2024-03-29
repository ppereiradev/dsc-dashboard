import pandas as pd
import os
import pytz

from datetime import datetime, timedelta
from dateutil.parser import parse

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
        ticket_states_to_portuguese = {
            "closed":"Fechado",
            "open":"Aberto",
            "resolvido":"Resolvido",
            "new":"Novo",
            "aguardando resposta":"Aguardando Resposta",
            "pendente":"Pendente",
            "retorno":"Retorno",
            "merged":"merged",
        }

        self.tickets = self.tickets[self.tickets['state'] != 'merged']

        self.tickets['state'] = self.tickets['state'].map(ticket_states_to_portuguese)
        self.tickets['group'] = self.tickets['group'].map(ZAMMAD_GROUPS_TO_STD_SECTORS)

    
    def get_by_state(self, dates_three_months_ago_from_today, open_tickets_previous, closed_tickets_previous, group):
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

        # accumulated provisorio
        if group == "Diretoria":
            tickets = Ticket.objects.all()
        elif type(group) is list:
            tickets = Ticket.objects.filter(group__in=group)
        elif type(group) is str:
            tickets = Ticket.objects.filter(group=group)


        df_tickets = pd.DataFrame(list(tickets.values()))
        df_tickets = df_tickets[df_tickets["state"] != "merged"]

        # recuperando os tickets abertos por mês durante os últimos meses
        aux_open_tickets = self._get_tickets_monthly_by_state(
            df_tickets[
                df_tickets["created_at"]
                > pd.to_datetime(
                    parse("2021-09-30 00:00:00-03:00"),
                    unit="ns",
                    utc=True,
                )
            ],
            "created_at",
        )

        aux_open_tickets.drop("created_at", inplace=True, axis=1)
        aux_open_tickets.rename(columns={"id_ticket": "qnt"}, inplace=True)
        
        # recuperando os tickets fechados por mês durante os últimos meses
        aux_closed_tickets = df_tickets.dropna(axis=0, subset=["close_at"])
        aux_closed_tickets = self._get_tickets_monthly_by_state(aux_closed_tickets, "close_at")
        
        aux_closed_tickets.drop("close_at", inplace=True, axis=1)
        aux_closed_tickets.rename(columns={"id_ticket": "qnt"}, inplace=True)

        accumulated_tickets = aux_open_tickets.copy(deep=True)
        accumulated_tickets = accumulated_tickets.assign(qnt=0)
        
        # accumulated
        for i in range(len(aux_open_tickets)):
            if i < 1:
                accumulated_tickets.at[i, "qnt"] = (
                    aux_open_tickets["qnt"][i] - aux_closed_tickets["qnt"][i]
                )
            else:
                accumulated_tickets.at[i, "qnt"] = (
                    aux_open_tickets["qnt"][i]
                    - aux_closed_tickets["qnt"][i]
                    + accumulated_tickets["qnt"][i - 1]
                )

        inner_merge = pd.merge(aux_open_tickets, aux_closed_tickets, on=["mes/ano"])
        
        # COMPLETE DATAFRAME
        self.num_tickets_by_state = pd.merge(
            inner_merge, accumulated_tickets, on=["mes/ano"]
        )

        self.num_tickets_by_state.rename(
            columns={
                "qnt_x": "abertos",
                "qnt_y": "fechados",
                "qnt": "acumulados",
            },
            inplace=True,
        )
        
        # setting mes/ano as index and getting last 5 months
        self.num_tickets_by_state.set_index('mes/ano', inplace=True)
        self.num_tickets_by_state = self.num_tickets_by_state.iloc[-5:]

        self.open_tickets_current_month = self.num_tickets_by_state['abertos'].iloc[-1]
        self.closed_tickets_current_month = self.num_tickets_by_state['fechados'].iloc[-1]
        self.num_accumulated_tickets = self.num_tickets_by_state['acumulados'].iloc[-1]
    
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

    def get_tickets_opened_more_20_days(self, group=None):
        ticket_states_to_portuguese = {
                "closed":"Fechado",
                "open":"Aberto",
                "resolvido":"Resolvido",
                "new":"Novo",
                "aguardando resposta":"Aguardando Resposta",
                "pendente":"Pendente",
                "retorno":"Retorno",
                "merged":"merged",
            }
        if group:
            tickets = Ticket.objects.filter(group=group)
        else:
            tickets = Ticket.objects.all()
        self.tickets_opened_more_20_days = pd.DataFrame(list(tickets.values()))
        self.tickets_opened_more_20_days['state'] = self.tickets_opened_more_20_days['state'].map(ticket_states_to_portuguese)

        self.tickets_opened_more_20_days = self.tickets_opened_more_20_days[self.tickets_opened_more_20_days["id_ticket"] != '2']
        self.tickets_opened_more_20_days['group'] = self.tickets_opened_more_20_days['group'].map(ZAMMAD_GROUPS_TO_STD_SECTORS)

        self.tickets_opened_more_20_days = self.tickets_opened_more_20_days[
                                                        (self.tickets_opened_more_20_days['created_at'] < pd.to_datetime(datetime.now() - timedelta(days=20), unit="ns", utc=True))
                                                         & (self.tickets_opened_more_20_days['state'] != "Fechado")
                                                         & (self.tickets_opened_more_20_days['state'] != "merged")
                                                         & (self.tickets_opened_more_20_days['state'].notnull())]
        
        self.tickets_opened_more_20_days["idade"] = pd.to_datetime(datetime.now(), unit="ns", utc=True) - self.tickets_opened_more_20_days['created_at']
        self.tickets_opened_more_20_days["idade"] = self.tickets_opened_more_20_days["idade"].dt.days

    def get_processed_data(self):
        self.get_data_from_last_four_months()
        self.clean_data()
        self.get_by_state()
        self.get_leadtime()
        self.get_satisfaction()
        self.get_tickets_opened_more_20_days()


    # métodos internos para limpar, e transformar os dados dos tickets
    def _close_date_to_month_year(self, df_temp):
        MONTH_NUMBER_TO_WORD = {
            1: "Janeiro",
            2: "Fevereiro",
            3: "Março",
            4: "Abril",
            5: "Maio",
            6: "Junho",
            7: "Julho",
            8: "Agosto",
            9: "Setembro",
            10: "Outubro",
            11: "Novembro",
            12: "Dezembro",
        }
        df_temp = df_temp.sort_values(by="mes/ano").reset_index(drop=True)
        df_temp["mes/ano"] = df_temp["mes/ano"].apply(
            lambda x: MONTH_NUMBER_TO_WORD[int(x.split("-")[1])] + "/" + x.split("-")[0]
        )

        return df_temp

    def _get_tickets_monthly_by_state(self, df_temp, state):
        df_temp = df_temp.set_index(state)
        df_temp = df_temp.groupby(pd.Grouper(freq="M"))
        df_temp = df_temp["id_ticket"].count().reset_index()

        df_temp["mes/ano"] = df_temp[state].dt.strftime("%y-%m")
        df_temp = self._close_date_to_month_year(df_temp)

        return df_temp
