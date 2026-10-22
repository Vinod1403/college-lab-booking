
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        
stage('Install Dependencies and Test') {
    steps {
        bat 'py -3.11 --version'
        bat 'py -3.11 -m pip install -r requirements.txt'
        bat 'py -3.11 -m pytest -v'
    }
}


        stage('Build Docker Image') {
            steps {
                bat 'docker build -t college-lab-booking:ci .'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Tests passed and Docker image built.'
        }
        failure {
            echo 'FAILED: Check the console output for details.'
        }
    }
}
