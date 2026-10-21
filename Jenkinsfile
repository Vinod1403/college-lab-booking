
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'college-lab-booking'
        IMAGE_TAG = 'ci'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Source code checked out successfully.'
            }
        }

        stage('Run Automated Tests') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$WORKSPACE:/app" \
                      -w /app \
                      python:3.11-slim \
                      sh -c "pip install --no-cache-dir -r requirements.txt && pytest -v"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                      -t ${IMAGE_NAME}:${IMAGE_TAG} .
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Tests passed and Docker image was built.'
        }

        failure {
            echo 'FAILED: Check the stage logs for the error.'
        }

        always {
            echo 'Jenkins pipeline execution completed.'
        }
    }
}
