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
        docker.withRegistry('https://repo.secure.amsterdam.nl','docker-registry') {
	        def api = docker.build(
			"datapunt/iotsignals:${env.BUILD_NUMBER}", "api",
			"--build-arg https_proxy=http://10.240.2.1:8080/"
		)
                    api.push()
                    api.push("acceptance")
            }
        }
    }
}

String BRANCH = "${env.BRANCH_NAME}"

if (BRANCH == "master") {

    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
               docker.withRegistry('https://repo.secure.amsterdam.nl','docker-registry') {
                    def image = docker.image("datapunt/iotsignals:${env.BUILD_NUMBER}")
                    image.pull()
                    image.push("acceptance")
                }
            }
        }
    }

    node {
        stage("Deploy to ACC") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-iotsignals.yml'],
                ]
            }
        }
    }

    stage('Waiting for approval') {
        input "Deploy to Production?"
    }

    node {
        stage('Push production image') {
            tryStep "image tagging", {
                docker.withRegistry('https://repo.secure.amsterdam.nl','docker-registry') {
                    def api = docker.image("datapunt/iotsignals:${env.BUILD_NUMBER}")
                    api.push("production")
                    api.push("latest")
                }
            }
        }
    }

    node {
        stage("Deploy") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: 'production'],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-iotsignals.yml'],
                ]
            }
        }
    }
}
