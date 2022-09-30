import time

from django.db import connection
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
from data_updater import data_zammad

class Command(BaseCommand):
    """
    Base commands to check the database.

    Check if the database is up before starting the
    Django application, and fill the database using
    the Zammad tickets' information.

    Method
    ----------
    handle(*args, **options)
        Perform the verification on database, and when
        the database is available, it adds the data collected
        from Zammad.
    """
    def handle(self, *args, **options):   
        """
        Check if database is available.

        This method checks and waits for the database, 
        it also fills the database with the data from
        Zammad.

        Parameters
        ----------
        *args 
            It is not used.
        **options 
            It is not used.
        """
        self.stdout.write('Waiting for database...')
        tries = 0
        while tries < 10:
            try:
                connection.ensure_connection()
                data_zammad.all_tickets()
                break
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
            tries += 1

        if tries < 10:
            self.stdout.write(self.style.SUCCESS('Database available!'))
        else:
            self.stdout.write('Database is not available, try again!')