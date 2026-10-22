
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

        stage('Prepare Persistent Storage') {
            steps {
                bat '"C:\\Users\\Vinod\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" volume create college-lab-data'
            }
        }

        stage('Deploy Application') {
            steps {
                bat '"C:\\Users\\Vinod\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" rm -f college-lab-demo 2>NUL || exit /b 0'

                bat '"C:\\Users\\Vinod\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" run -d --name college-lab-demo -p 5001:5000 -v college-lab-data:/data -e DATABASE_PATH=/data/college_lab.db college-lab-booking:ci'
            }
        }

        stage('Verify Deployment') {
            steps {
                bat '"C:\\Users\\Vinod\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" exec college-lab-demo python -c "import database; print(\'Database path:\', database.DATABASE); assert str(database.DATABASE) == \'/data/college_lab.db\'"'

                bat '"C:\\Users\\Vinod\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" exec college-lab-demo python -c "import sqlite3; c=sqlite3.connect(\'/data/college_lab.db\'); print(\'Users:\', c.execute(\'SELECT name,email,role FROM users\').fetchall()); c.close()"'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Tests passed, image built, persistent volume mounted, and deployment verified.'
        }
        failure {
            echo 'FAILED: Check Console Output. If deployment failed, inspect the container and database volume.'
        }
        always {
            echo 'Jenkins pipeline execution completed.'
        }
    }
}
