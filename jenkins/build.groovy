pipeline {
    agent any

    stages {
        stage('Get/Update Source') {
            steps {
                // https://jenkins.io/doc/pipeline/steps/slack/
                slackSend channel: "#build", message: "Build Started: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
                checkout poll: true, scm: [$class: 'SubversionSCM',
                    additionalCredentials: [],
                    excludedCommitMessages: '',
                    excludedRegions: '',
                    excludedRevprop: '',
                    excludedUsers: '',
                    filterChangelog: false,
                    ignoreDirPropChanges: false,
                    includedRegions: '',
                    locations: [[
                        credentialsId: '',
                        depthOption: 'infinity',
                        ignoreExternalsOption: true,
                        local: '.',
                        remote: 'svn://chris@10.0.9.57/starryexpanse']],
                    workspaceUpdater: [$class: 'UpdateUpdater']]
                checkout poll: true, scm: [$class: 'GitSCM',
                    branches: [[name: '*/master']],
                    doGenerateSubmoduleConfigurations: false,
                    extensions: [
                        [$class: 'CleanBeforeCheckout'],
                        [$class: 'RelativeTargetDirectory', relativeTargetDir: 'UE4/StarryExpanse/Source']
                    ],
                    submoduleCfg: [],
                    userRemoteConfigs: [[
                        url: 'https://github.com/starryexpanse/StarryExpanse.git']]
                    ]
                script {
                    if (fileExists('Build')) {
                        bat "rd /s /q Build"
                    }
                }
                echo 'Cleaning prior build.'
                bat 'python UE4\\StarryExpanse\\build.py clean'
            }
        }
        stage('Build') {
            steps {
                lock('UE4Build') {
                    bat 'python UE4\\StarryExpanse\\build.py full'
                }
            }
        }
        stage('Test') {
            steps {
                echo 'No tests to run.'
            }
        }
        stage('Archive') {
            steps {
                // 7z command-line args at: https://www.dotnetperls.com/7-zip-examples
                bat '"%ProgramW6432%/7-Zip/7z.exe" a -tzip -r "%WORKSPACE%/Build/Development/Win64/StarryExpanse_%BUILD_NUMBER%_Win64.zip" "%WORKSPACE%/Build/Development/Win64/WindowsNoEditor"'
                archiveArtifacts artifacts: "Build/Development/Win64/StarryExpanse_${env.BUILD_NUMBER}_Win64.zip", onlyIfSuccessful: true
            }
        }
    }
    post {
        always {
            echo 'One way or another, I have finished.'
        }
        success {
            echo 'I succeeded!'
            slackSend channel: "#build", color: "#00AA00", message: "Build succeeded: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        unstable {
            echo 'I am unstable :/'
        }
        failure {
            echo 'I failed :('
            slackSend channel: "#build", color: "#FF0000", message: "Build *FAILED*: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        changed {
            echo 'Things were different before...'
        }
    }
}

