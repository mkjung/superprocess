import subprocess

from superprocess import base, remote

__all__ = ['Popen', 'PIPE', 'STDOUT', 'call',
	'check_call', 'check_output', 'CalledProcessError']

PIPE = subprocess.PIPE
STDOUT = subprocess.PIPE
CalledProcessError = subprocess.CalledProcessError

class Popen(remote.RemoteShellMixin, base.PopenMixin, subprocess.Popen):
	pass

call = Popen.call
check_call = Popen.check_call
check_output = Popen.check_output
