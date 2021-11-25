#!/usr/bin/env groovy
pipeline {
    agent any
    stages {
        stage('Cleaning') {
            steps {
                sh(returnStdout: true, script: '''#!/bin/bash
                    if [ $(docker stop dsc_dashboard_app) ];then
                            docker stop dsc_dashboard_app
                            docker rm dsc_dashboard_app
                            docker rmi dsc_dashboard_app:0.1.0
                    else
                            echo "There is no such container"
                    fi
                '''.stripIndent())
            }
        }
        stage('Deployment') {
            steps {
                sh '''
                    docker-compose -f build --build-arg UID=$(id -u)
                    docker-compose -f up -d
                    docker logs dsc_dashboard_app
                   '''
            }
        }
    }
}

