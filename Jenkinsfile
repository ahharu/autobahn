import org.jenkinsci.plugins.workflow.steps.FlowInterruptedException

final Map<String, String> COLOR = [
  SUCCESS: 'GREEN',
  UNSTABLE: 'YELLOW',
  FAILURE: 'RED',
  NOT_BUILT: 'GRAY',
  ABORTED: 'GRAY'
]

final String PROJECT = 'autobahn'
final int DEPLOY_RETRIES = 3

try {
  node('mobile-cd') {
    String mvnHome = tool name: 'maven', type: 'hudson.tasks.Maven$MavenInstallation'
    String javaHome = tool(name: 'java-8-oracle', type: 'hudson.model.JDK')
    String mvn = "${mvnHome}/bin/mvn"

    stage('Checkout') {
      if (isStrictCDInfringed())
        error "Only master or develop can be deployed in strict mode"

      deleteDir()

      checkout poll: true, scm: [
        $class: 'GitSCM',
        branches: [[name: "refs/heads/${BRANCH_NAME}"]],
        doGenerateSubmoduleConfigurations: false,
        extensions: [],
        submoduleCfg: [],
        userRemoteConfigs: scm.userRemoteConfigs
      ]
    }

    stage('Run Tests') {
      withEnv([
        "MVN=${mvn}",
        "JAVA_HOME=${javaHome}"
      ]) {
        sh "./generate_reports.sh"
      }
      junit keepLongStdio: true, testResults: '**/app/TEST-*.xml'
      if (currentBuild.result != null) {
        throw new Exception("Failed Tests!")
      } 
    }

    stage('Build') {
      withEnv([
        "MVN=${mvn}",
        "JAVA_HOME=${javaHome}"
      ]) {
        sh "./build.sh"
      }
    }

    stage('Deploy') {
      withEnv([
        "MVN=${mvn}",
        "JAVA_HOME=${javaHome}"
      ]) {
        withCredentials([[
            $class: 'StringBinding',
            credentialsId: 'serverless-decrypt',
            variable: 'SERVERLESS_DECRYPT_KEY'
        ]]) {
          final String DEPLOY_ENVIRONMENT = isMaster() ? 'prod' : 'dev'
          sh "./deploy_jenkins.sh ${DEPLOY_ENVIRONMENT}"
        }
      }
    }
  }
} catch (FlowInterruptedException f) {
  currentBuild.result = f.getResult()
} catch (Throwable unexpected) {
  currentBuild.result = "FAILURE"
  throw unexpected
} finally {
  String room = isMaster() ? 'ProductionDeploys' : 'Develop'
  String buildStatus = currentBuild.result ?: 'SUCCESS'

  hipchatSend(
    color: COLOR[buildStatus],
    message: "[${PROJECT.toUpperCase()}] Deploy ${buildStatus} -- ${env.JOB_NAME} #${env.BUILD_NUMBER} (<a href='${env.BUILD_URL}'>Open</a>)",
    notify: true,
    room: room
  )
}

private boolean isMaster() {
  return BRANCH_NAME.equals("master")
}

private boolean isStrictCDInfringed() {
  return !BRANCH_NAME.equals("master") && !BRANCH_NAME.equals("develop")
}
