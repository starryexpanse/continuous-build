#!/usr/bin/env python3

from __future__ import print_function

import argparse
import os
import platform
import shutil
import socket
import subprocess
import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class Command(object):
  @staticmethod
  def OutputColor():
    if platform.system() == 'Windows':
      return False
    else:
      return sys.stdout.isatty()

  @staticmethod
  def Print(cmd):
    if type(cmd) is list:
      str_cmd = ' '.join(cmd)
    else:
      print(type(cmd).__name__)
      assert type(cmd) is str
      str_cmd = cmd
    if Command.OutputColor():
      print("%s%s%s" % (bcolors.OKBLUE, str_cmd, bcolors.ENDC))
    else:
      print(str_cmd)

  @staticmethod
  def Run(cmd, check=True):
    Command.Print(cmd)
    if check:
      subprocess.check_call(cmd)
    else:
      subprocess.call(cmd)

class VirtualEnv(object):
  @staticmethod
  def Get():
    """Returns the path to the current Python virtualenv, or None."""
    try:
      return os.environ['VIRTUAL_ENV']
    except KeyError as e:
      return None

  @staticmethod
  def Create(venv_dir):
    Command.Run(['python3', '-m', 'venv', venv_dir])
    if platform.system() == 'Windows':
      cmd = [os.path.join(venv_dir, 'Scripts', 'activate')]
    else:
      cmd = ['source', os.path.join(venv_dir, 'bin', 'activate')]
    print('From your shell run this command:')
    print()
    Command.Print([' ', ' '] + cmd)
    print()
    print('And then rerun this script.')
    sys.exit(0)

class Options(object):
  def __init__(self):
    self.command = None
    self.venv_dir = 'buildbotvenv'
    self.worker_dir = 'worker'
    self.master_dir = 'master'
    self.master_hostname = None
    self.worker_username = None
    self.worker_password = None
    self.worker_admin = 'Build Master <buildmaster@starryexpanse.com>'

  def Parse(self):
    parser = argparse.ArgumentParser(prog='bbmgr',
      description="The Starry Expanse Buildbot management script.")

    # parser.add_argument('--foo', action='store_true', help='foo help')
    top_subparsers = parser.add_subparsers(dest='cmd')

    # create the parser for the "master" command
    parser_master = top_subparsers.add_parser(
        'master', help='Manage the local Buildbot master.')
    msub = parser_master.add_subparsers(dest='sub_cmd')
    msub.add_parser('checkconfig', help='Validate master.cfg.')
    msub.add_parser('start', help='Start the master.')
    msub.add_parser('stop', help='Stop the master.')
    msub.add_parser('reconfig', help='Reconfigure the master w/o stopping.')
    msub.add_parser('restart', help='Restart the master.')
    msub.add_parser('reset-db', help='Reset the database - USE WITH CAUTION!')
    msub.add_parser('prereqs', help='Install master prerequisites.')

    # create the parser for the "worker" command
    parser_worker = top_subparsers.add_parser(
        'worker', help='Manage the local buildbot worker.')
    wsub = parser_worker.add_subparsers(dest='sub_cmd')
    cp = wsub.add_parser('create', help='Create a local worker.')
    cp.add_argument('host', help='The hostname of the master.')
    cp.add_argument('username', help='The worker username.')
    cp.add_argument('password', help='The worker password.')
    wsub.add_parser('start', help='Start the local worker.')
    wsub.add_parser('stop', help='Stop the local worker.')
    wsub.add_parser('prereqs', help='Install worker prerequisites.')

    args = parser.parse_args()
    if not args.cmd:
      parser.print_help()
      sys.exit(1)
    if not args.sub_cmd:
      if args.cmd == 'master':
        parser_master.print_help()
      elif args.cmd == 'worker':
        parser_worker.print_help()
      sys.exit(1)
    self.command = '%s-%s' % (args.cmd, args.sub_cmd)
    if self.command == 'worker-create':
      self.master_hostname = args.host
      self.worker_username = args.username
      self.worker_password = args.password

class BuildbotManager(object):
  @staticmethod
  def HasSecrets():
    return os.path.isdir('secrets')

  @staticmethod
  def InstallMasterPrereqs(options):
    prev_cwd = os.getcwd()
    try:
      os.chdir(options.venv_dir)
      Command.Run(['pip', 'install', '--upgrade', 'pip'])
      Command.Run(['pip', 'install', 'buildbot[bundle]'])
    finally:
      os.chdir(prev_cwd)

  @staticmethod
  def ResetMasterDatabase(options):
    Command.Run(['git', 'stash'])
    shutil.rmtree(options.master_dir)
    Command.Run(['buildbot', 'create-master', options.master_dir])
    Command.Run(['git', 'reset', '--hard', 'HEAD'])
    os.remove(os.path.join(options.master_dir, 'master.cfg.sample'))
    Command.Run(['git', 'stash', 'pop'], check=False)

  @staticmethod
  def StartMaster(options):
    if platform.system() == 'Darwin':
      bad_proxy = False
      try:
        if os.environ['no_proxy'] != '*':
          bad_proxy = True
      except KeyError:
        bad_proxy = True
      if bad_proxy:
        # Workaround a macOS Python bug
        # See https://github.com/buildbot/buildbot/issues/3605
        os.environ['no_proxy'] = '*'
    if not BuildbotManager.HasSecrets():
      print('Missing "secrets" directory', file=sys.stderr)
      sys.exit(1)
    if not os.path.exists(os.path.join(options.master_dir, 'state.sqlite')):
      # Probably a first run after initial checkout.
      BuildbotManager.ResetMasterDatabase(options)
    cmd = ['buildbot', 'start', options.master_dir]
    Command.Run(cmd)

  @staticmethod
  def CheckMasterConfig(options):
    Command.Run(['buildbot', 'checkconfig', options.master_dir])

  @staticmethod
  def StopMaster(options):
    Command.Run(['buildbot', 'stop', options.master_dir])

  @staticmethod
  def RestartMaster(options):
    Command.Run(['buildbot', 'restart', options.master_dir])

  @staticmethod
  def InstallWorkerPrereqs(options):
    prev_cwd = os.getcwd()
    try:
      os.chdir(options.venv_dir)
      Command.Run(['pip', 'install', '--upgrade', 'pip'])
      Command.Run(['pip', 'install', 'buildbot-worker'])
      if platform.system() == 'Windows':
        Command.Run(['pip', 'install', 'pypiwin32'])
    finally:
      os.chdir(prev_cwd)

  @staticmethod
  def WorkerExists(options):
    return os.path.isdir(options.worker_dir)

  @staticmethod
  def CreateWorker(options):
    cmd = ['buildbot-worker', 'create-worker', options.worker_dir,
           options.master_hostname, options.worker_username,
           options.worker_password]
    Command.Run(cmd)
    with open(os.path.join(options.worker_dir, 'info', 'admin'), 'w') as f:
      f.write(options.worker_admin)
    with open(os.path.join(options.worker_dir, 'info', 'host'), 'w') as f:
      f.write(socket.gethostname())

  @staticmethod
  def StartWorker(options):
    Command.Run(['buildbot-worker', 'start', options.worker_dir])

  @staticmethod
  def StopWorker(options):
    Command.Run(['buildbot-worker', 'stop', options.worker_dir])

if __name__ == '__main__':
  options = Options()
  options.Parse()

  full_venv_dir = os.path.join(os.getcwd(), options.venv_dir)
  if full_venv_dir != VirtualEnv.Get():
    VirtualEnv.Create(options.venv_dir)
  if options.command == 'master-prereqs':
    BuildbotManager.InstallMasterPrereqs(options)
  elif options.command == 'master-start':
    BuildbotManager.InstallMasterPrereqs(options)
    BuildbotManager.StartMaster(options)
  elif options.command == 'master-stop':
    BuildbotManager.StopMaster(options)
  elif options.command == 'master-checkconfig':
    BuildbotManager.CheckMasterConfig(options)
  elif options.command == 'master-restart':
    BuildbotManager.RestartMaster(options)
  elif options.command == 'master-reset-db':
    BuildbotManager.ResetMasterDatabase(options)
  elif options.command == 'worker-prereqs':
    BuildbotManager.InstallWorkerPrereqs(options)
  elif options.command == 'worker-create':
    BuildbotManager.InstallWorkerPrereqs(options)
    BuildbotManager.CreateWorker(options)
  elif options.command == 'worker-start':
    if not BuildbotManager.WorkerExists(options):
      BuildbotManager.InstallWorkerPrereqs(options)
      BuildbotManager.CreateWorker(options)
    BuildbotManager.StartWorker(options)
  elif options.command == 'worker-stop':
    BuildbotManager.StopWorker(options)
  else:
    assert False
