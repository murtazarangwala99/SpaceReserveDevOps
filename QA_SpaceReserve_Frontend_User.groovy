pipeline{
    agent {label 'interns2025'}
    
    environment {
        PROJECT_VERSION = '1.0.0'
    }
    stages {
        stage('Clone Project') {
            steps {
               checkout scmGit(branches: [[name: '*/qa']], extensions: [], userRemoteConfigs: [[credentialsId: 'spacereserve', url: 'https://1gitlab.1rivet.com/1Rivet/spacereservefrontend-user-portal.git']])
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    bat 'npm install'
                }
            }
        }
        
        // stage('Run Test Cases') {
        //     steps {
        //         script {
        //             bat 'npm run test -- --code-coverage'
        //         }
        //     }
        // }

        stage('Build Project') {
            steps {
                bat 'npm run build -- --configuration qa'
            }
        }

        stage('Delete Previous Zip') {
            steps {
                bat "del /F /Q *.zip"
            }
        }

        stage('Archive Artifact') {
            steps {
                bat "powershell Compress-Archive -Path dist\\desk-book\\* -DestinationPath QA_spacereserve_frontend_user.zip"
            }
        }

        stage('Upload Artifact to Nexus') {
            steps {
                nexusArtifactUploader(
                    nexusVersion: 'nexus3',
                    protocol: 'http',
                    nexusUrl: '172.16.1.236:8081',
                    groupId: 'Space-Reserve',
                    version: PROJECT_VERSION,
                    repository: 'Space-Reserve',
                    credentialsId: 'NEXUS',
                    artifacts: [[
                        artifactId: 'QA_spacereserve_frontend_user',
                        classifier: BUILD_TIMESTAMP,
                        file: "QA_spacereserve_frontend_user.zip",
                        type: 'zip'
                    ]]
                )
            }
        }

    }
}