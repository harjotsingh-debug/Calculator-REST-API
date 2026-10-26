// Declarative CI/CD pipeline: Checkout -> Build -> Test -> Docker Build -> Push -> Deploy
//
// Jenkins itself is defined in jenkins/ (Docker + Configuration as Code), which sets up everything below.
// Manual equivalent (see README "Jenkins setup"):
//   * Credentials: "Username with password" with ID 'dockerhub-creds' (Docker Hub username + access token)
//   * Global env vars (Manage Jenkins -> System -> Global properties):
//       DOCKERHUB_USER = your Docker Hub username
//       NOTIFY_EMAIL   = address that receives build notifications
//   * Plugins: Pipeline, Git, GitHub, JUnit, Coverage, Email Extension, Credentials Binding
//   * The Jenkins agent needs Docker + Docker Compose v2 and must be able to run "docker" without sudo

pipeline {
    agent any

    triggers {
        // Fired by the GitHub webhook (http://<jenkins>/github-webhook/)
        githubPush()
        // Fallback when GitHub cannot reach Jenkins (e.g. Jenkins on a laptop): poll every 2 minutes
        pollSCM('H/2 * * * *')
    }

    options {
        timestamps()
        disableConcurrentBuilds()          // two deploys must never race each other
        buildDiscarder(logRotator(numToKeepStr: '15'))
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        IMAGE_NAME = "${env.DOCKERHUB_USER}/calculator-api"
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Build') {
            steps {
                sh 'chmod +x mvnw'
                sh './mvnw -B clean package -DskipTests'
            }
        }

        stage('Test') {
            steps {
                // A failing test, or line coverage below 80% (JaCoCo check), makes mvn exit non-zero and fails the build
                sh './mvnw -B test'
            }
            post {
                always {
                    junit allowEmptyResults: false, testResults: 'target/surefire-reports/*.xml'
                    recordCoverage tools: [[parser: 'JACOCO', pattern: 'target/site/jacoco/jacoco.xml']],
                                   sourceCodeRetention: 'EVERY_BUILD'
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t "$IMAGE_NAME:$IMAGE_TAG" -t "$IMAGE_NAME:latest" .'
                // Nginx reverse proxy image with the config baked in
                sh 'docker compose build proxy'
            }
        }

        stage('Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_TOKEN')]) {
                    sh '''
                        echo "$DH_TOKEN" | docker login -u "$DH_USER" --password-stdin
                        docker push "$IMAGE_NAME:$IMAGE_TAG"
                        docker push "$IMAGE_NAME:latest"
                    '''
                }
            }
            post {
                always {
                    sh 'docker logout || true'
                }
            }
        }

        stage('Deploy') {
            steps {
                // Idempotent: "up -d" only recreates containers whose image/config changed;
                // --wait blocks until every service reports healthy (fails the stage otherwise).
                sh '''
                    docker compose up -d --no-build --remove-orphans --wait --wait-timeout 180
                    docker compose ps
                '''
                // End-to-end check through the Nginx proxy, from inside the Compose network
                sh '''
                    docker compose exec -T proxy wget -qO- http://127.0.0.1/actuator/health
                    docker compose exec -T proxy wget -qO- "http://127.0.0.1/api/v1/add?a=2&b=3"
                '''
            }
        }
    }

    post {
        success {
            emailext(
                to: "${env.NOTIFY_EMAIL}",
                subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """Build ${env.BUILD_NUMBER} of ${env.JOB_NAME} succeeded.
Image: ${env.IMAGE_NAME}:${env.IMAGE_TAG}
Details: ${env.BUILD_URL}"""
            )
        }
        failure {
            emailext(
                to: "${env.NOTIFY_EMAIL}",
                subject: "FAILURE: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """Build ${env.BUILD_NUMBER} of ${env.JOB_NAME} failed.
Console log: ${env.BUILD_URL}console""",
                attachLog: true
            )
        }
        always {
            // Remove dangling layers left by repeated builds; never touches running containers
            sh 'docker image prune -f || true'
        }
    }
}
