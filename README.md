tutorial mongodb install docker:

https://dev.to/sonyarianto/how-to-spin-mongodb-server-with-docker-and-docker-compose-2lef

connect to mongodb
https://www.bmc.com/blogs/mongodb-docker-container/

tutorial: https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/

Change ownership of volume in docker volumes:

(ubuntu): chown -R $USER:$USER /var/lib/docker/volumes/volume-name

then build the image:
```bash
docker-compose build --build-arg UID=$(id -u) && docker-compose up -d
```
to read the documentation:
```bash
cd docs/
make html
```

## Miscellaneous

To delete all none images in the docker
```bash
docker rmi $(docker images | grep none | awk '{print $3}')
```

## Description of Files and Directories

```bash
.
├── Dockerfile # Create image of container dsc_dashboard_app
├── README.md 
├── docker-compose.yml # Rules to create the image of container
├── docs # documentation in HTML format
...
├── dsc_dashboard # the application in django
│   ├── accounts # application that is responsible for the accounts of users (login, logout, reset password, etc.)
│   │   ├── templates # the HTML pages responsible for rendering the login, logout, reset password page
│   ├── dashboards # application that is responsible for presenting the charts to the users
│   │   ├── dashboards application that is responsible for presenting the charts to the users
│   │   │   ├── apps # each dashboard (tab) is an application
│   │   │   │   ├── app_1.py # Diretoria dashboard
│   │   │   │   ├── app_2.py # Conectividade dashboard
│   │   │   │   ├── app_3.py # Sistemas dashboard
│   │   │   │   ├── app_4.py # Serviços Digitais dashboard
│   │   │   │   ├── app_5.py # Micro Informática dashboard
│   │   │   │   └── app_6.py # Suporte ao Usuário dashboard
│   │   │   └── dashboard.py # responsible for the landingpage of the dashboards
│   │   ├── management 
│   │   │   └── commands
│   │   │       ├── default_users.py # responsible for adding users
│   │   │       └── wait_for_db.py # waits for the database to be up
│   │   ├── static # keeps the static files such as css, js, etc.
│   │   ├── templates # keeps the HTML page of the dashboard
│   │   ├── urls.py # responsible for redirecting the urls for to the functions in the view
│   │   └── views.py # functions responsible for render the dashboard
│   ├── data_updater # processes and store all the data about the tickets
│   │   ├── data_processing # classes that process the data for each tab
│   │   │   ├── data_cleaning.py # parent class where all the methods are defined
│   │   │   ├── processed_data.py # singleton for the dashboard to improve the performance
│   │   ├── data_zammad.py # responsible for getting the data from zammad
│   │   ├── mongo_utils.py # functions to store and get the data from mongodb
│   │   └── updater.py # routines that update the database
├── dsc_dev # files to create image and container for development environment
├── entrypoint.sh # bash commands to initialize the dashboard
├── nginx # files to create the nginx image and container
└── requirements.txt # all packages needed to run the dashboard
```