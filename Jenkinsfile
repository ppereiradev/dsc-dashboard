#!/usr/bin/env groovy
pipeline {
    agent any
    stages {
        stage('Cleaning') {
            steps {
                sh '''
                    docker stop dsc_dashboard_app
                    docker rm dsc_dashboard_app
                    docker rmi dsc_dashboard_app:0.1.0
                   '''
            }
        }
        stage('Deployment') {
            steps {
                sh '''
                    docker-compose -f dsc_dev/docker-compose.yml build --build-arg UID=$(id -u)
                    docker-compose -f dsc_dev/docker-compose.yml up -d
                    docker logs dsc_dashboard_app
                   '''
            }
        }
    }
}