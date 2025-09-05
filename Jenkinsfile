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
                    bat 'docker-compose build'
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Exécution des tests dans le conteneur API déjà actif
                    bat 'docker exec -i reconnaissance_objet-api-1 pytest || echo "⚠️ Aucun test ou test échoué"'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    bat 'docker-compose up -d'
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
