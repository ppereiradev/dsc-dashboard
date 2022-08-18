import os
import pandas as pd
from datetime import datetime, timedelta

from ..mongo_utils import count_tickets

from .constant_utils import MONTH_NUMBER_TO_NAME
from .data_cleaning import DataCleaning

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
        self.leadtime_scatter_plot = self.leadtime_scatter_plot[['number', 'state', 'group', 'created_at', 'close_at']]
        
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

    def get_satisfaction(self):
        
        url = f"https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEET_ID')}/gviz/tq?tqx=out:csv&sheet={os.getenv('GOOGLE_SHEET_NAME')}"
        tickets_aux = pd.read_csv(url)
        score_column = tickets_aux.columns[1]
        ticket_number_column = tickets_aux.columns[-1]
        tickets_aux = tickets_aux.drop_duplicates(subset=ticket_number_column, keep="last")
        self.satisfaction_customers = pd.DataFrame(None, index =[0,1,2,3,4,5,6,7,8,9,10], columns =['qnt'])
        
        self.satisfaction_customers['qnt'] = self.satisfaction_customers.index.map(tickets_aux[score_column].value_counts()).fillna(0).astype(int)
        self.satisfaction_customers['percentage'] = self.satisfaction_customers.index.map(tickets_aux[score_column].value_counts(normalize=True) * 100).fillna(0).astype(float)