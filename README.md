Starry Expanse Continuous Build
===============================

These are the scripts for the Starry Expanse continuous build/integration
system. There are currently two configurations. One using Jenkins-CI, and
the other using Buildbot.

# Common Prerequisites

1. Git
2. Subversion
3. Unreal Engine
4. Visual Studio

## Unreal Engine Install Directory
The Unreal Engine command-line build scripts have a bug causing them to fail
if the file paths contain spaces. Unfortunately, on macOS, the default engine
installation directory is `/Users/Shared/Epic Games/<envine version>/...`.
One way to fix this is to change the engine directory to
`/Users/Shared/EpicGames/<engine version>/...` **at installation time**.

# Jenkins

Jenkins is currently our active build system. More info can be found in the
[Jenkins README](jenkins/README.md).

# Buildbot

The team is currently experimenting with using [Buildbot](https://buildbot.net/).
More info can be found in the [Buildbot README](buildbot/README.md).
