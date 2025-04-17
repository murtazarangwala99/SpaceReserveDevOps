pipeline {
    agent { 
        label "interns2025" 
    }
    environment {
        branch_name = "develop"
    }
    stages {
        stage("Cloning the code") {
            steps {
                checkout scmGit(branches: [[name: 'develop']], extensions: [], userRemoteConfigs: [[credentialsId: 'spacereserve', url: 'https://1gitlab.1rivet.com/1Rivet/spacereserveservices-user-portal.git']])
            }
        }

        stage("Restoring dependencies") {
            steps {
                bat """
                    cd src
                    dotnet restore
                """
            }
        }

        stage("Starting Sonar Scanner analysis") {
            steps {
                withCredentials([string(credentialsId: 'sonar-token-intern', variable: 'SONAR_TOKEN')]) {
                bat """
                    cd src
                    dotnet sonarscanner begin /k:"Sonar_backend_user" /d:sonar.token="${SONAR_TOKEN}" /d:sonar.host.url="http://172.16.0.5:9000/"     
                """
            }
            }
        }

        stage("Build the app for analysis") {
            steps {
                bat """
                    cd src
                    dotnet build  --no-incremental
                """
            }
        }

        stage("Ending the analysis") {
            steps{
                withCredentials([string(credentialsId: 'sonar-token-intern', variable: 'SONAR_TOKEN')]) {
                bat """
                    cd src
                    dotnet sonarscanner end /d:sonar.token="${SONAR_TOKEN}"
                """
            }
            }
        }
        
    }
}
