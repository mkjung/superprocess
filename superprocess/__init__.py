import subprocess

from superprocess.base import PopenMixin
from superprocess.popen import OSPopenMixin
from superprocess.py2 import Py2Mixin
from superprocess.redirect import RedirectMixin
from superprocess.remote import RemoteShellMixin

__all__ = ['Popen', 'PIPE', 'STDOUT', 'STDERR', 'call',
	'check_call', 'check_output', 'CalledProcessError']

PIPE = subprocess.PIPE
STDOUT = subprocess.PIPE
STDERR = redirect.STDERR
CalledProcessError = subprocess.CalledProcessError

class Popen(
		OSPopenMixin,
		RedirectMixin,
		RemoteShellMixin,
		PopenMixin,
		Py2Mixin,
		subprocess.Popen):
	pass

call = Popen.call
check_call = Popen.check_call
check_output = Popen.check_output
popen = Popen.popen
