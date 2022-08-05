import pandas as pd
import os
from datetime import datetime, timedelta

from .mongo_utils import count_tickets, get_tickets_from_db

# constants
AMOUNT_MONTHS_IN_DAYS = 120
MONTH_NUMBER_TO_NAME = {
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
ZAMMAD_GROUPS_TO_STD_SECTORS = {
    "SIG@": "Sistemas",
    "SIGAA": "Sistemas",
    "SIPAC": "Sistemas",
    "SIGRH": "Sistemas",
    "Sistemas Diversos": "Sistemas",
    "Web Sites": "Sistemas",
    "Triagem": "Suporte ao Usuário",
    "Serviços Computacionais": "Serviços Computacionais",
    "Micro Informática": "Micro Informática",
    "Conectividade": "Conectividade",
    "CODAI": "CODAI",
    "UABJ": "UABJ",
    "UAST": "UAST",
    "UACSA": "UACSA",
    "UAEADTec": "UAEADTec"
}

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
        self.tickets = get_tickets_from_db({ "$or": [ {"created_at":{"$gte": (datetime.now() - timedelta(days=AMOUNT_MONTHS_IN_DAYS)) }},
                                             {"close_at":{"$gte": (datetime.now() - timedelta(days=AMOUNT_MONTHS_IN_DAYS)) }} ]})
    
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
        open_tickets = open_tickets[(open_tickets['created_at'] <= datetime.now())]
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
        closed_tickets = closed_tickets[(closed_tickets['close_at'] <= datetime.now()) & (closed_tickets['state'] == "Fechado")]
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
        self.leadtime_scatter_plot = self.leadtime_scatter_plot[['state', 'group', 'created_at', 'close_at']]
        
        # keeping tickets from last 6 months only
        self.leadtime_scatter_plot = self.leadtime_scatter_plot[self.leadtime_scatter_plot['close_at'] > (datetime.now() - timedelta(days=210))]

        self.leadtime_scatter_plot['diff'] = self.leadtime_scatter_plot['close_at'] - self.leadtime_scatter_plot['created_at']
        self.leadtime_scatter_plot['diff'] = self.leadtime_scatter_plot['diff'].astype('timedelta64[h]')

        self.leadtime_scatter_plot["mes/ano"] = self.leadtime_scatter_plot['close_at'].dt.strftime('%y-%m')
        self.leadtime_scatter_plot = self.leadtime_scatter_plot.sort_values(by='mes/ano').reset_index(drop=True)
        self.leadtime_scatter_plot["mes/ano"] = self.leadtime_scatter_plot["mes/ano"].apply(lambda x: MONTH_NUMBER_TO_NAME[int(x.split('-')[1])] + '/' + x.split('-')[0])

        self.leadtime_scatter_plot['diff'] = self.leadtime_scatter_plot['diff']/24
        self.leadtime_scatter_plot['diff'] = self.leadtime_scatter_plot['diff'].astype(int)

        self.leadtime_bar_plot = pd.DataFrame(columns=['mes/ano', 'diff'])
        for i in range(0, len(self.leadtime_scatter_plot['diff'])):
            self.leadtime_bar_plot.loc[i] = [self.leadtime_scatter_plot['close_at'].iloc[i].date().strftime('%y-%m'), self.leadtime_scatter_plot['diff'].iloc[i]]

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

        satisfaction_customers_aux['number'], tickets_aux[ticket_number_column] = satisfaction_customers_aux['number'].astype(int), tickets_aux[ticket_number_column].astype(int)
        satisfaction_customers_aux = pd.merge(satisfaction_customers_aux, tickets_aux, left_on='number', right_on=ticket_number_column,how='inner')
        
        self.satisfaction_customers['qnt'] = self.satisfaction_customers.index.map(tickets_aux[score_column].value_counts()).fillna(0).astype(int)
        self.satisfaction_customers['percentage'] = self.satisfaction_customers.index.map(tickets_aux[score_column].value_counts(normalize=True) * 100).fillna(0).astype(float)


    def get_processed_data(self):
        self.get_data_from_last_four_months()
        self.clean_data()
        self.get_by_state()
        self.get_leadtime()
        self.get_satisfaction()


class Diretoria(DataCleaning):

    def get_by_state(self):

        dates_three_months_ago_from_today = pd.period_range(pd.Timestamp.now().to_period('m')-3,freq='M', 
                                                            periods=4).strftime('%Y-%m-%d').tolist()
        last_day_three_months_ago = datetime.strptime(dates_three_months_ago_from_today[0] + " 23:59:59",
                                                    '%Y-%m-%d %H:%M:%S').replace(day=1) - timedelta(days=1)


        self.open_tickets_previous = count_tickets(
            { "created_at": { "$lte": last_day_three_months_ago } }
        )

        self.closed_tickets_previous = count_tickets(
            { "close_at": { "$lte": last_day_three_months_ago } }
        )
        
        self.closed_tickets_total = count_tickets({ "state": "closed" })
        
        super().get_by_state(dates_three_months_ago_from_today, self.open_tickets_previous, self.closed_tickets_previous)

    
    def get_leadtime(self):
        """
        Calculate the leadtime of the tickets.

        Get the tickets then calculate the 
        leadtime of each sector. Also map sectors name.

        Parameters
        ----------
        tickets : pd.DataFrame
            Pandas Dataframe with the clean data of the Zammad tickets.
        MONTH_NUMBER_TO_NAME : dict of {int : str}
            Dictionary with the number of month and its name in portuguese.

        Returns
        -------
        tickets_setores : pd.DataFrame
            Pandas Dataframe with the leadtime of each sector.
        tickets_unidades : pd.DataFrame
            Pandas Dataframe with the leadtime of each campus of 
            UFRPE.
        """
        self.leadtime_scatter_plot = self.tickets.copy(deep=True)
        self.leadtime_scatter_plot = self.leadtime_scatter_plot.dropna(axis=0, subset=['close_at'])
        
        self.leadtime_scatter_plot = self.leadtime_scatter_plot[self.leadtime_scatter_plot['state'] == 'Fechado']
        self.leadtime_scatter_plot = self.leadtime_scatter_plot[['state', 'group', 'created_at', 'close_at']]
        
        # keeping tickets from last 6 months only
        self.leadtime_scatter_plot = self.leadtime_scatter_plot[self.leadtime_scatter_plot['close_at'] > (datetime.now() - timedelta(days=210))]

        self.leadtime_scatter_plot['diff'] = self.leadtime_scatter_plot['close_at'] - self.leadtime_scatter_plot['created_at']
        self.leadtime_scatter_plot['diff'] = self.leadtime_scatter_plot['diff'].astype('timedelta64[h]')

        tickets_aux = pd.DataFrame(columns=['mes/ano', 'group', 'diff'])
        for i in range(0, len(self.leadtime_scatter_plot['diff'])):
            tickets_aux.loc[i] = [self.leadtime_scatter_plot['close_at'].iloc[i].date().strftime('%y-%m'), self.leadtime_scatter_plot['group'].iloc[i], self.leadtime_scatter_plot['diff'].iloc[i]]

        tickets_aux = tickets_aux.groupby(['mes/ano', 'group']).mean().reset_index()
        tickets_aux['diff'] = tickets_aux['diff']/24
        tickets_aux['diff'] = tickets_aux['diff'].astype(int)

        self.leadtime_scatter_plot['diff'] = self.leadtime_scatter_plot['diff']/24
        self.leadtime_scatter_plot['diff'] = self.leadtime_scatter_plot['diff'].astype(int)

        self.leadtime_scatter_plot["mes/ano"] = self.leadtime_scatter_plot['close_at'].dt.strftime('%y-%m')
        self.leadtime_scatter_plot = self.leadtime_scatter_plot.sort_values(by='mes/ano').reset_index(drop=True)
        self.leadtime_scatter_plot["mes/ano"] = self.leadtime_scatter_plot["mes/ano"].apply(lambda x: MONTH_NUMBER_TO_NAME[int(x.split('-')[1])] + '/' + x.split('-')[0])
        
        setores_list = ["Sistemas","Suporte ao Usuário","Serviços Computacionais","Micro Informática","Conectividade","CODAI","UABJ","UAST","UACSA","UAEADTec"]
        
        for mes in tickets_aux['mes/ano']:
            for setor in setores_list:
                if setor not in tickets_aux[(tickets_aux['mes/ano'] == mes)]['group'].to_list():
                    tickets_aux = tickets_aux.append({"mes/ano": mes, "group": setor, "diff": 0}, ignore_index=True)
            
        tickets_aux = tickets_aux.sort_values(by='mes/ano').reset_index(drop=True)

        self.leadtime_std_sectors = tickets_aux.loc[tickets_aux['group'].isin(["Sistemas","Suporte ao Usuário","Serviços Computacionais","Micro Informática","Conectividade"])]
        self.leadtime_campi = tickets_aux.loc[tickets_aux['group'].isin(["CODAI","UABJ","UAST","UACSA","UAEADTec"])]

        self.leadtime_std_sectors = self.leadtime_std_sectors.pivot_table('diff', 'mes/ano', 'group')
        self.leadtime_campi = self.leadtime_campi.pivot_table('diff', 'mes/ano', 'group')

        self.leadtime_std_sectors = self.leadtime_std_sectors.reset_index(level=[0])
        self.leadtime_campi = self.leadtime_campi.reset_index(level=[0])
        self.leadtime_std_sectors['mes/ano'] = self.leadtime_std_sectors['mes/ano'].apply(lambda x: MONTH_NUMBER_TO_NAME[int(x.split('-')[1])] + '/' + x.split('-')[0])
        self.leadtime_campi['mes/ano'] = self.leadtime_campi['mes/ano'].apply(lambda x: MONTH_NUMBER_TO_NAME[int(x.split('-')[1])] + '/' + x.split('-')[0])
        
    

class Conectividade(DataCleaning):
    def clean_data(self):
        super().clean_data()
        self.tickets = self.tickets[self.tickets['group'] == "Conectividade"]

    def get_by_state(self):

        dates_three_months_ago_from_today = pd.period_range(pd.Timestamp.now().to_period('m')-3,freq='M', 
                                                            periods=4).strftime('%Y-%m-%d').tolist()
        last_day_three_months_ago = datetime.strptime(dates_three_months_ago_from_today[0] + " 23:59:59",
                                                    '%Y-%m-%d %H:%M:%S').replace(day=1) - timedelta(days=1)

        self.open_tickets_previous = count_tickets(
            { "$and": [ 
                        {"group": "Conectividade"}, { "created_at": { "$lte": last_day_three_months_ago } } 
                ] 
            } )
        self.closed_tickets_previous = count_tickets(
            { "$and": [ 
                        {"group": "Conectividade"}, { "close_at": { "$lte": last_day_three_months_ago } } 
                ] 
            })
        self.closed_tickets_total = count_tickets(
            { "$and": [ 
                        {"group": "Conectividade"}, { "state": "closed" } 
                ] 
            })


        super().get_by_state(dates_three_months_ago_from_today, self.open_tickets_previous, self.closed_tickets_previous)

       
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




class ServicosComputacionais(DataCleaning):
    def clean_data(self):
        super().clean_data()
        self.tickets = self.tickets[self.tickets['group'] == "Serviços Computacionais"]

    def get_by_state(self):

        dates_three_months_ago_from_today = pd.period_range(pd.Timestamp.now().to_period('m')-3,freq='M', 
                                                            periods=4).strftime('%Y-%m-%d').tolist()
        last_day_three_months_ago = datetime.strptime(dates_three_months_ago_from_today[0] + " 23:59:59",
                                                    '%Y-%m-%d %H:%M:%S').replace(day=1) - timedelta(days=1)

        self.open_tickets_previous = count_tickets(
            { "$and": [ 
                        {"group": "Serviços Computacionais"}, { "created_at": { "$lte": last_day_three_months_ago } } 
                ] 
            } )
        self.closed_tickets_previous = count_tickets(
            { "$and": [ 
                        {"group": "Serviços Computacionais"}, { "close_at": { "$lte": last_day_three_months_ago } } 
                ] 
            })
        self.closed_tickets_total = count_tickets(
            { "$and": [ 
                        {"group": "Serviços Computacionais"}, { "state": "closed" } 
                ] 
            })


        super().get_by_state(dates_three_months_ago_from_today, self.open_tickets_previous, self.closed_tickets_previous)


class MicroInformatica(DataCleaning):
    def clean_data(self):
        super().clean_data()
        self.tickets = self.tickets[self.tickets['group'] == "Micro Informática"]
    
    def get_by_state(self):
        
        dates_three_months_ago_from_today = pd.period_range(pd.Timestamp.now().to_period('m')-3,freq='M', 
                                                            periods=4).strftime('%Y-%m-%d').tolist()
        last_day_three_months_ago = datetime.strptime(dates_three_months_ago_from_today[0] + " 23:59:59",
                                                    '%Y-%m-%d %H:%M:%S').replace(day=1) - timedelta(days=1)

        self.open_tickets_previous = count_tickets(
            { "$and": [ 
                        {"group": "Micro Informática"}, { "created_at": { "$lte": last_day_three_months_ago } } 
                ] 
            } )
        self.closed_tickets_previous = count_tickets(
            { "$and": [ 
                        {"group": "Micro Informática"}, { "close_at": { "$lte": last_day_three_months_ago } } 
                ] 
            })
        self.closed_tickets_total = count_tickets(
            { "$and": [ 
                        {"group": "Micro Informática"}, { "state": "closed" } 
                ] 
            })


        super().get_by_state(dates_three_months_ago_from_today, self.open_tickets_previous, self.closed_tickets_previous)


class Suporte(DataCleaning):
    def clean_data(self):
        super().clean_data()
        self.tickets = self.tickets[self.tickets['group'] == "Suporte ao Usuário"]

    def get_by_state(self):
        
        dates_three_months_ago_from_today = pd.period_range(pd.Timestamp.now().to_period('m')-3,freq='M', 
                                                            periods=4).strftime('%Y-%m-%d').tolist()
        last_day_three_months_ago = datetime.strptime(dates_three_months_ago_from_today[0] + " 23:59:59",
                                                    '%Y-%m-%d %H:%M:%S').replace(day=1) - timedelta(days=1)

        self.open_tickets_previous = count_tickets(
            { "$and": [ 
                        {"group": "Triagem"}, { "created_at": { "$lte": last_day_three_months_ago } } 
                ] 
            } )
        self.closed_tickets_previous = count_tickets(
            { "$and": [ 
                        {"group": "Triagem"}, { "close_at": { "$lte": last_day_three_months_ago } } 
                ] 
            })
        self.closed_tickets_total = count_tickets(
            { "$and": [ 
                        {"group": "Triagem"}, { "state": "closed" } 
                ] 
            })


        super().get_by_state(dates_three_months_ago_from_today, self.open_tickets_previous, self.closed_tickets_previous)

    def get_by_week(self):
        """
        Calculate the amount of tickets by weekday.

        Calculate the number of tickets opened in each
        week dayi.e., Monday, Tuesday, Wednesday, Thursday,
        Friday, Saturday, and Sunday). It separetes the tickets
        opened by web and by telephone.

        Parameters
        ----------
        tickets : pd.DataFrame
            Pandas Dataframe with the clean data of the Zammad tickets.

        Returns
        -------
        tickets_portal_semana : pd.DataFrame
            Pandas Dataframe with the amount of tickets opended
            over the web in each weekday (i.e., Monday, Tuesday,
            Wednesday, Thursday, Friday, Saturday, and Sunday).
        tickets_telefone_semana : pd.DataFrame
            Pandas Dataframe with the amount of tickets opended
            over the telephone in each weekday (i.e., Monday, Tuesday,
            Wednesday, Thursday, Friday, Saturday, and Sunday).
        """
        weekly_tickets = self.tickets.copy(deep=True)
        weekly_tickets = weekly_tickets[['created_at', 'create_article_type']]
        weekly_tickets.columns = ['criado', 'tipo']
        
        weekly_tickets['dia'] = weekly_tickets['criado'].dt.day_name()
        weekly_tickets = weekly_tickets[weekly_tickets["criado"] >= (pd.to_datetime("now") - pd.Timedelta(days=30))]

        day_translation = {"Monday":"Segunda",
                        "Tuesday":"Terça",
                        "Wednesday":"Quarta",
                        "Thursday":"Quinta",
                        "Friday":"Sexta",
                        "Saturday":"Sábado",
                        "Sunday":"Domingo",
                        }

        type_translation = {"email":"Portal",
                        "web":"Portal",
                        "note":"Portal",
                        "phone":"Telefone",
                        }


        weekly_tickets['tipo'] = weekly_tickets['tipo'].map(type_translation)

        self.portal_tickets_week = weekly_tickets.loc[weekly_tickets['tipo'] == "Portal", 'dia'].value_counts().rename_axis('dia').reset_index(name='total')
        self.phone_tickets_week = weekly_tickets.loc[weekly_tickets['tipo'] == "Telefone", 'dia'].value_counts().rename_axis('dia').reset_index(name='total')
        
        self.portal_tickets_week['dia'] = self.portal_tickets_week['dia'].map(day_translation)
        self.phone_tickets_week['dia'] = self.phone_tickets_week['dia'].map(day_translation)


    def get_by_hour(self):
        """
        Calculate the amount tickets by hour.

        Calculate the amount of tickets opened by hour
        of the day, the data is divided into two groups:
        web and telephone.

        Parameters
        ----------
        tickets : pd.DataFrame
            Pandas Dataframe with the clean data of the Zammad tickets.

        Returns
        -------
        tickets_horas : pd.DataFrame
            Pandas Dataframe with the amount of tickets opended
            each hour of day. The tickets are divided into two groups
            (i.e., web and telephone).
        """
        self.tickets_by_hour = self.tickets.copy(deep=True)
        self.tickets_by_hour = self.tickets_by_hour[['created_at', 'create_article_type']]
        self.tickets_by_hour.columns = ['criado', 'tipo']
        self.tickets_by_hour = self.tickets_by_hour[self.tickets_by_hour["criado"] >= (pd.to_datetime("now") - pd.Timedelta(days=30))]

        type_translation = {"email":"Portal",
                        "web":"Portal",
                        "note":"Portal",
                        "phone":"Telefone",
                        }
        self.tickets_by_hour['tipo'] = self.tickets_by_hour['tipo'].map(type_translation)

        hours_day = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09',
                    '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                    '20', '21', '22', '23']

        portal_tickets_hour = self.tickets_by_hour['criado'][self.tickets_by_hour['tipo'] == "Portal"].dt.hour.value_counts().rename_axis('hora').reset_index(name='qnt')
        phone_tickets_hour = self.tickets_by_hour['criado'][self.tickets_by_hour['tipo'] == "Telefone"].dt.hour.value_counts().rename_axis('hora').reset_index(name='qnt')

        for hour in hours_day:
            if int(hour) not in portal_tickets_hour['hora'].to_list():
                portal_tickets_hour = portal_tickets_hour.append({'hora': int(hour), 'qnt': 0}, ignore_index=True)

            if int(hour) not in phone_tickets_hour['hora'].to_list():
                phone_tickets_hour = phone_tickets_hour.append({'hora': int(hour), 'qnt': 0}, ignore_index=True)

        portal_tickets_hour = portal_tickets_hour.sort_values(by='hora').reset_index(drop=True)
        phone_tickets_hour = phone_tickets_hour.sort_values(by='hora').reset_index(drop=True)

        self.tickets_by_hour = pd.merge(portal_tickets_hour,phone_tickets_hour, on='hora',how='inner', suffixes=('_portal', '_telefone'))

    def get_processed_data(self):
        super().get_processed_data()
        self.get_by_week()
        self.get_by_hour()

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
        
class ProcessedData(metaclass=Singleton):
    def __init__(self):
        self.diretoria = Diretoria()
        self.conectividade = Conectividade()
        self.sistemas = Sistemas()
        self.servicos_computacionais = ServicosComputacionais()
        self.micro_informatica = MicroInformatica()
        self.suporte = Suporte()
        self.get_processed_data_all()

    def get_processed_data_all(self):
        self.diretoria.get_processed_data()
        self.conectividade.get_processed_data()
        self.sistemas.get_processed_data()
        self.servicos_computacionais.get_processed_data()
        self.micro_informatica.get_processed_data()
        self.suporte.get_processed_data()

    def get_data_diretoria(self):
        return self.diretoria

    def get_data_conectividade(self):
        return self.conectividade
    
    def get_data_sistemas(self):
        return self.sistemas

    def get_data_servicos_computacionais(self):
        return self.servicos_computacionais

    def get_data_micro_informatica(self):
        return self.micro_informatica

    def get_data_suporte(self):
        return self.suporte
