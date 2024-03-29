#!groovy
def PROJECT_NAME = "iotsignals"
def SLACK_CHANNEL = '#opdrachten-deployments'
def PLAYBOOK = 'deploy.yml'
def SLACK_MESSAGE = [
    "title_link": BUILD_URL,
    "fields": [
        ["title": "Project","value": PROJECT_NAME],
        ["title": "Branch", "value": BRANCH_NAME, "short":true],
        ["title": "Build number", "value": BUILD_NUMBER, "short":true]
    ]
]



pipeline {
    agent any

    environment {
        SHORT_UUID = sh( script: "head /dev/urandom | tr -dc a-z0-9 | head -c10", returnStdout: true).trim()
        COMPOSE_PROJECT_NAME = "${PROJECT_NAME}-${env.SHORT_UUID}"
        VERSION = env.BRANCH_NAME.replace('/', '-').toLowerCase().replace(
            'master', 'latest'
        )
    }

    stages {
        stage('Test') {
            steps {
                sh "make test"
            }
        }

//         stage('Locust load test') {
//             steps {
//                 sh "./deploy/docker-locust-load-test.sh"
//             }
//         }

        stage('Build') {
            steps {
                sh 'make build'
            }
        }

        stage('Push and deploy') {
            when {
                anyOf {
                    branch 'master'
                    buildingTag()
                }
            }
            stages {
                stage('Push') {
                    steps {
                        slackSend(channel: SLACK_CHANNEL, attachments: [SLACK_MESSAGE <<
                            [
                                "color": "#D4DADF",
                                "title": "Starting deployment",
                            ]
                        ])
                        retry(3) {
                            sh 'make push_semver'
                        }
                    }
                }

                stage('Deploy to acceptance') {
                    when {
                        anyOf {
                            branch 'master'
                        }
                    }
                    steps {
                        sh 'VERSION=acceptance make push'
                        build job: 'Subtask_Openstack_Playbook', parameters: [
                            string(name: 'PLAYBOOK', value: PLAYBOOK),
                            string(name: 'INVENTORY', value: "acceptance"),
                            string(
                                name: 'PLAYBOOKPARAMS',
                                value: "-e cmdb_id=app_${PROJECT_NAME}"
                            )
                        ], wait: true

                        slackSend(channel: SLACK_CHANNEL, attachments: [SLACK_MESSAGE <<
                            [
                                "color": "#36a64f",
                                "title": "Deploy to acceptance succeeded :rocket:",
                            ]
                        ])
                    }
                }

                stage('Deploy to production') {
                    when { tag pattern: "\\d+\\.\\d+\\.\\d+\\.*", comparator: "REGEXP" }
                    steps {
                        sh 'VERSION=production make push'
                        build job: 'Subtask_Openstack_Playbook', parameters: [
                            string(name: 'PLAYBOOK', value: PLAYBOOK),
                            string(name: 'INVENTORY', value: "production"),
                            string(
                                name: 'PLAYBOOKPARAMS',
                                value: "-e cmdb_id=app_${PROJECT_NAME}"
                            )
                        ], wait: true

                        slackSend(channel: SLACK_CHANNEL, attachments: [SLACK_MESSAGE <<
                            [
                                "color": "#36a64f",
                                "title": "Deploy to production succeeded :rocket:",
                            ]
                        ])
                    }
                }
            }
        }

    }
    post {
        always {
            sh 'make clean'
        }
        failure {
            slackSend(channel: SLACK_CHANNEL, attachments: [SLACK_MESSAGE <<
                [
                    "color": "#D53030",
                    "title": "Build failed :fire:",
                ]
            ])
        }
    }
}