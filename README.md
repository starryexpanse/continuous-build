Starry Expanse Continuous Build
===============================

These are the scripts for the Starry Expanse continuous build/integration
system. The system is currently run on Jenkins-CI. The build script is
a Groovy pipeline using the declarative syntax.

# Prerequisites

1. Git.
2. Subversion.
3. Unreal Engine.
4. [Jenkins](https://jenkins.io).
   * The [Slack Plugin](https://wiki.jenkins.io/display/JENKINS/Slack+Plugin).
   * The [Lockable Resources plugin](https://wiki.jenkins.io/display/JENKINS/Lockable+Resources+Plugin).
5. Visual Studio.

# Configuration

## SSH Keys

Put the public key on the Subversion server.

## Jenkins

1. Create a new job (item) named "Starry Expanse".
2. Select **Pipeline** as the type.
3. Paste the contents of build.groovy into the pipeline script section.

**Note**: The goal is to have build.groovy run via "Pipeline script from SCM", but
when run via this mode Git/Svn polling doesn't work.
