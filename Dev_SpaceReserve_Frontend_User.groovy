pipeline {
    agent {
        label 'interns2025'
    }
    environment {
        PROJECT_VERSION = '1.0.0'
    }
    stages {
        stage('Clone Project') {
            steps {
              checkout scmGit(branches: [[name: '*/develop']], extensions: [], userRemoteConfigs: [[credentialsId: 'spacereserve', url: 'https://1gitlab.1rivet.com/1Rivet/spacereservefrontend-user-portal.git']])
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    bat 'npm install'
                }
            }
        }

        stage('Build Project') {
            steps {
                bat 'npm run build -- --configuration development'
            }
        }
        
        stage('Delete Previous Zip') {
            steps {
                bat "del /F /Q *.zip"
            }
        }


        stage('Archive Artifact') {
            steps {
                bat "powershell Compress-Archive -Path dist\\desk-book\\* -DestinationPath dev_spacereserve_frontend_user.zip"
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
                        artifactId: 'dev_spacereserve_frontend_user',
                        classifier: BUILD_TIMESTAMP,
                        file: "dev_spacereserve_frontend_user.zip",
                        type: 'zip'
                    ]]
                )
            }
        }

        // stage('Deploy using Ansible on Ubuntu node') {
        //     agent {
        //         label 'linux'
        //     }
        //     steps {
        //         sh 'ansible-playbook -i /etc/ansible/hosts /etc/ansible/dev_spacereserve_frontend_user.yml'
        //     }
        // }
        

    }
}
