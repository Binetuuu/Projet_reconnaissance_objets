pipeline {
    agent any

    environment {
        API_URL = "http://api:8002"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Binetuuu/Projet_reconnaissance_objets.git'
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    bat 'docker-compose -f docker-compose.yml build'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    bat 'docker-compose -f docker-compose.yml up -d'
                }
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline exécuté avec succès. L’API est dispo sur ${API_URL}"
        }
        failure {
            echo "❌ Le pipeline a échoué. Vérifie les logs Jenkins."
        }
    }
}
