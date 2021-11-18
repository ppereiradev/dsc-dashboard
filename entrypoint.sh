#!/bin/sh
set -e

ls -la /home/user/vol/
ls -la /home/user/vol/web

# para apagar o banco descomente essa linha
#python manage.py flush --no-input

# esperando pelo banco de dados
python manage.py wait_for_db

# preparando os models para criar o banco de dados
python manage.py makemigrations


# criando o banco de dados para cada model
python manage.py migrate accounts --noinput
python manage.py migrate admin --noinput
python manage.py migrate auth --noinput
python manage.py migrate contenttypes --noinput
python manage.py migrate sessions --noinput

# django_plotly_dash gera um problema na migração com o mongodb, então temos que usar a flag --fake
python manage.py migrate django_plotly_dash --fake --noinput

# descomente essa linha para criar SU
#python manage.py createsuperuser --noinput

#unset DJANGO_SUPERUSER_PASSWORD && unset DJANGO_SUPERUSER_USERNAME && unset DJANGO_SUPERUSER_EMAIL

python manage.py collectstatic --noinput

gunicorn dsc_dashboard.wsgi:application --bind 0.0.0.0:8000