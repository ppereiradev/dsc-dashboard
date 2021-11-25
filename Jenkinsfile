#!/usr/bin/env groovy
pipeline {
    agent any
    stages {
        stage('Deployment') {
            steps {
                sh '''
                    printenv
                    echo $WORKSPACE_TMP
                   '''
            }
        }
    }
}