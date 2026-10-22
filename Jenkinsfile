
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

        stage('Check Docker Access') {
            steps {
                bat '"C:\\Users\\Vinod\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" version'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '"C:\\Users\\Vinod\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" build -t college-lab-booking:ci .'
            }
        }

        stage('Deploy Application') {
            steps {
                bat '"C:\\Users\\Vinod\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" rm -f college-lab-demo 2>NUL || exit /b 0'
                bat '"C:\\Users\\Vinod\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" run -d --name college-lab-demo -p 5001:5000 college-lab-booking:ci'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Tests passed, Docker image built, and application deployed.'
        }
        failure {
            echo 'FAILED: Check the Console Output for details.'
        }
        always {
            echo 'Jenkins pipeline execution completed.'
        }
    }
}
