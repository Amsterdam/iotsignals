#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block();
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#iotsignals', color: 'danger'
        throw t;
    }
    finally {
        if (tearDown) {
            tearDown();
        }
    }
}


node {
    stage("Checkout") {
        checkout scm
    }

    stage('Test') {
        tryStep "test", {
            sh "api/deploy/test/test.sh"
        }
    }

    stage("Build dockers") {
        tryStep "build", {
            docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                def api = docker.build("datapunt/iotsignals:${env.BUILD_NUMBER}", "api")
            }
        }
    }

    stage("Locust load test") {
        sh("./api/deploy/docker-locust-load-test.sh")
    }

    String BRANCH = "${env.BRANCH_NAME}"

    if (BRANCH == "master") {

        stage('Push acceptance image') {
            tryStep "image tagging", {
               docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                    def image = docker.image("datapunt/iotsignals:${env.BUILD_NUMBER}")
                    image.push("acceptance")
                }
            }
        }
        stage("Deploy to ACC") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy.yml'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOKPARAMS', value: "-e cmdb_id=app_iotsignals"],
                ]
            }
        }

        stage('Waiting for approval') {                                                                                                                                                 
            timeout(time: 6, unit: 'HOURS') {
                input "Deploy to Production?"
            }
        }

        stage('Push production image') {
            tryStep "image tagging", {
                docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                    def api = docker.image("datapunt/iotsignals:${env.BUILD_NUMBER}")
                    api.push("production")
                    api.push("latest")
                }
            }
        }

        stage("Deploy") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: 'production'],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy.yml'],
                        [$class: 'StringParameterValue', name: 'PLAYBOOKPARAMS', value: "-e cmdb_id=app_iotsignals"],
                ]
            }
        }
    }

}
