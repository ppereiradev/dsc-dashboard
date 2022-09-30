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
python manage.py migrate django_plotly_dash --noinput
python manage.py migrate tickets --noinput
python manage.py migrate

python manage.py default_users --superuser=yes --username=$DJANGO_SUPERUSER_USERNAME \
    --email=$DJANGO_SUPERUSER_EMAIL \
    --password=$DJANGO_SUPERUSER_PASSWORD

python manage.py default_users --username=$DJANGO_DIRETORIA_USERNAME \
    --email=$DJANGO_DIRETORIA_EMAIL \
    --password=$DJANGO_DIRETORIA_PASSWORD

python manage.py default_users --username=$DJANGO_CORPORATIVAS_USERNAME \
    --email=$DJANGO_CORPORATIVAS_EMAIL \
    --password=$DJANGO_CORPORATIVAS_PASSWORD

python manage.py default_users --username=$DJANGO_CONECTIVIDADE_USERNAME \
    --email=$DJANGO_CONECTIVIDADE_EMAIL \
    --password=$DJANGO_CONECTIVIDADE_PASSWORD

python manage.py default_users --username=$DJANGO_GOVERNANCA_USERNAME \
    --email=$DJANGO_GOVERNANCA_EMAIL \
    --password=$DJANGO_GOVERNANCA_PASSWORD

python manage.py collectstatic --noinput

gunicorn dsc_dashboard.wsgi:application --bind 0.0.0.0:8000
