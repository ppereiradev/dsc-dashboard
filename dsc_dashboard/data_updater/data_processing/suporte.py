import pandas as pd
from datetime import datetime, timedelta
import pytz

from tickets.models import Ticket

from .data_cleaning import DataCleaning

class Suporte(DataCleaning):
    def clean_data(self):
        super().clean_data()
        self.tickets = self.tickets[self.tickets['group'] == "Suporte ao Usuário"]

    def get_by_state(self):
        
        dates_three_months_ago_from_today = pd.period_range(pd.Timestamp.now().to_period('m')-3,freq='M', 
                                                            periods=4).strftime('%Y-%m-%d').tolist()
        last_day_three_months_ago = datetime.strptime(dates_three_months_ago_from_today[0] + " 23:59:59",
                                                    '%Y-%m-%d %H:%M:%S').replace(day=1) - timedelta(days=1)

        self.open_tickets_previous = (Ticket.objects.filter(group="Triagem") & 
                                      Ticket.objects.filter(created_at__lte=last_day_three_months_ago.replace(tzinfo=pytz.UTC))).count()
        self.closed_tickets_previous = (Ticket.objects.filter(group="Triagem") & 
                                      Ticket.objects.filter(close_at__lte=last_day_three_months_ago.replace(tzinfo=pytz.UTC))).count()
        self.closed_tickets_total = (Ticket.objects.filter(group="Triagem") & 
                                      Ticket.objects.filter(state="closed")).count()
        
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
        weekly_tickets = weekly_tickets[weekly_tickets["criado"] >= pd.to_datetime(pd.Timestamp('now') - pd.Timedelta(days=30), unit="ns", utc=True)]

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
        self.tickets_by_hour = self.tickets_by_hour[self.tickets_by_hour["criado"] >= pd.to_datetime(pd.Timestamp('now') - pd.Timedelta(days=30), unit="ns", utc=True)]

        self.tickets_by_hour["criado"] = pd.to_datetime(self.tickets_by_hour["criado"]) + pd.DateOffset(hours=-3)

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
                portal_tickets_hour = pd.concat([portal_tickets_hour, pd.DataFrame({'hora': [int(hour)], 'qnt': [0]})], ignore_index=True)

            if int(hour) not in phone_tickets_hour['hora'].to_list():
                phone_tickets_hour = pd.concat([phone_tickets_hour, pd.DataFrame({'hora': [int(hour)], 'qnt': [0]})], ignore_index=True)

        portal_tickets_hour = portal_tickets_hour.sort_values(by='hora').reset_index(drop=True)
        phone_tickets_hour = phone_tickets_hour.sort_values(by='hora').reset_index(drop=True)

        self.tickets_by_hour = pd.merge(portal_tickets_hour,phone_tickets_hour, on='hora',how='inner', suffixes=('_portal', '_telefone'))

    def get_processed_data(self):
        super().get_processed_data()
        self.get_by_week()
        self.get_by_hour()
