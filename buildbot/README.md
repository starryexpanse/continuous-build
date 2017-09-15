Starry Expanse Buildbot Continuous Build
=======================================

These are the scripts for the Starry Expanse continuous build/integration
system using [Buildbot](https://buildbot.net/).

# Prerequisites

In addition to the common continuous build prerequisites you will need:

1. Python 3.x.
2. Python [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

# Running a Master

1. Create a secrets directory

When running the master for the first time it is required to populate
the secrets directory with some configuration data.

```bash
mkdir secrets
echo "http://localhost:8010/" > secrets/master-url
echo "desired-password" > secrets/Win64-1
echo "desired-password" > secrets/Win64-2
echo "desired-password" > secrets/macOS-1
echo "git-user" > secrets/gituser.txt
echo "git-passwd" > secrets/gitpasswd.txt
echo "svn-user" > secrets/svnuser.txt
echo "svn-passwd" > secrets/svnpasswd.txt
chmod -R go-rwx secrets
```

Consult the `master/master.cfg` file to learn what these values are, and
what they should be set to.

2. Start the master

```bash
python bbmgr.py master start
```

If the Python virtualenv is not yet running, the it will be configured,
and you will be prompted to run a command and then re-run
the bbmgr.py script.

For more master commands run the following:

```bash
python bbmgr.py master --help
```

# Creating/Running a Worker
There can be as many workers as are defined in the `master/master.cfg` file.
Each one has it's own username and password.

1. Create the worker

```bash
python bbmgr.py worker create <master-hostname> <worker-username> <worker-password>
```

2. Start the worker

```bash
python bbmgr.py worker start
```

# Buildbot Development/Debugging

Each cluster of master/worker(s) are independent from each other. When making
changes to `master/master.cfg` it is always best to make them on a development
master so as to not to negatively impact the production master. Following the
steps above will allow one to easily setup an isolated master/worker for this
development.

## Checking configuration

After any change to `master.cfg` it recommended to validate that file as so:

```bash
python bbmgr.py master checkconfig
```
