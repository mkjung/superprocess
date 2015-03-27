import subprocess

from superprocess import base, py2, remote

__all__ = ['Popen', 'PIPE', 'STDOUT', 'call',
	'check_call', 'check_output', 'CalledProcessError']

PIPE = subprocess.PIPE
STDOUT = subprocess.PIPE
CalledProcessError = subprocess.CalledProcessError

class Popen(
		remote.RemoteShellMixin,
		py2.Py2Mixin,
		base.PopenMixin,
		subprocess.Popen):
	pass

call = Popen.call
check_call = Popen.check_call
check_output = Popen.check_output
