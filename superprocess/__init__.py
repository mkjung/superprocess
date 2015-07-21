import subprocess

from superprocess.base import superprocess
from superprocess.popen import OSPopenMixin
from superprocess.py2 import Py2Mixin
from superprocess.redirect import RedirectMixin
from superprocess.remote import RemoteShellMixin

__all__ = ['Popen', 'PIPE', 'STDOUT', 'STDERR', 'call',
	'check_call', 'check_output', 'CalledProcessError']

impl = superprocess(subprocess)

PIPE = impl.PIPE
STDOUT = impl.PIPE
STDERR = redirect.STDERR
CalledProcessError = impl.CalledProcessError

class Popen(
		OSPopenMixin,
		RedirectMixin,
		RemoteShellMixin,
		Py2Mixin,
		impl.Popen):
	pass

call = Popen.call
check_call = Popen.check_call
check_output = Popen.check_output
popen = Popen.popen
