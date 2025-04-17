pipeline {
    agent { 
        label "interns2025" 
    }
    environment {
        branch_name = "develop"
        SONAR_PROJECT_KEY = "Sonar_frontend_user"
        SONAR_HOST_URL = "http://172.16.0.5:9000"
    }

     stages {
        stage("Cloning the code") {
            steps {
                checkout scmGit(
                    branches: [[name: "${branch_name}"]],
                    extensions: [],
                    userRemoteConfigs: [[
                        credentialsId: 'spacereserve',
                        url: 'https://1gitlab.1rivet.com/1Rivet/spacereservefrontend-user-portal.git'
                    ]]
                )
            }
        }

        stage("Install dependencies") {
            steps {
                bat 'npm install'
            }
        }

        stage("Build Angular app") {
            steps {
                bat 'npm run build -- --configuration development'
            }
        }

        //stage("Run tests and generate coverage") {
          //  steps {
            //    echo 'Running unit tests with coverage...'
            //    bat 'npx ng test --watch=false --code-coverage'
        //    }
    //    }

        stage("Start SonarQube analysis") {
            steps {
                withCredentials([string(credentialsId: 'sonar-token-intern', variable: 'SONAR_TOKEN')]) {
                    bat """
                        sonar-scanner ^
                          -Dsonar.projectKey=${SONAR_PROJECT_KEY} ^
                          -Dsonar.sources=src ^
                          -Dsonar.host.url=${SONAR_HOST_URL} ^
                          -Dsonar.token=%SONAR_TOKEN% ^
                          -Dsonar.exclusions=**/*.spec.ts,**/node_modules/** ^
                          -Dsonar.tests=src ^
                          -Dsonar.test.inclusions=**/*.spec.ts ^
                          -Dsonar.javascript.lcov.reportPaths=coverage/lcov.info
                    """
                }
            }
        }
    }

    post {
        success {
            echo 'Angular pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Please check the logs.'
        }
    }
}
