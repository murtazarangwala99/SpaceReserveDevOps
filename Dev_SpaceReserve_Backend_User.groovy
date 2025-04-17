pipeline{
    agent {label 'interns2025'}
    
    environment{
        PROJECT_VERSION="1.0.0"
        SITE_NAME="dev-SpaceReserveServices-User_Portal"
        PORT="8080"
    }
    
    stages{
        stage('clone'){
            steps{
                 checkout scmGit(branches: [[name: 'develop']], extensions: [], userRemoteConfigs: [[credentialsId: 'spacereserve', url: 'https://1gitlab.1rivet.com/1Rivet/spacereserveservices-user-portal.git']])
            }
        } 
        
        stage('Restore Nuget packages'){
            steps{
                 bat """
                    cd src
                    dotnet restore
                 """
            }
        }
        
        stage('Building the app'){
            steps{
                 bat """
                    cd src
                    dotnet build
                 """
            }
        }
        
        stage('Publish the app'){
            steps{
                 bat """
                    cd src
                    dotnet publish -o ./publish -c release
                """
            }
        }
        
        stage('Ziping the publish folder'){
            steps{
                bat """
                    cd src
                    powershell Remove-Item *.zip -Force -Recurse
                    cd C:/JenkinsWorkspace/workspace/Space-Reserve-2025/dev_spacereserveservices_user/src/publish/
                    powershell Compress-Archive -Path "C:/JenkinsWorkspace/workspace/Space-Reserve-2025/dev_spacereserveservices_user/src/publish/*" -DestinationPath "C:/JenkinsWorkspace/workspace/Space-Reserve-2025/dev_spacereserveservices_user/src/dev_spacereserveservices_user.zip"
                """
            }
        }
        
        stage('Upload Artifact to Nexus') {
            steps {
                script{
                    echo "The  project version is ${PROJECT_VERSION}"
                    echo "${BUILD_TIMESTAMP}"
                    // def TimeStamp = BUILD_TIMESTAMP.replaceAll('-', '').substring(0, BUILD_TIMESTAMP.replaceAll('-', '').length() - 2)
                    // echo TimeStamp
                }
                
                nexusArtifactUploader(
                    nexusVersion: 'nexus3',
                    protocol: 'http',
                    nexusUrl: '172.16.1.236:8081',
                    groupId: 'Space-Reserve',
                    version: "${PROJECT_VERSION}",
                    repository: 'Space-Reserve',
                    credentialsId: 'NEXUS',
                    artifacts: [[
                        artifactId: 'dev_spacereserveservices_user',
                        classifier: "${BUILD_TIMESTAMP}",
                        file: "src/dev_spacereserveservices_user.zip",
                        type: 'zip'
                    ]]
                )
            }
        }
        
        stage('Ansible Playbook'){
            agent{
                label 'ansible'
            }
            steps{
                sh """
                    ansible-playbook -i /etc/ansible/hosts /etc/ansible/Playbooks/deployBackend.yml --extra-vars "site_name=${env.SITE_NAME} port_for_site=${env.PORT}"
                """
            }
        }
        
    }
}