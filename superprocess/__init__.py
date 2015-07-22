from superprocess.base import superprocess
from superprocess.popen import popen
from superprocess.redirect import RedirectMixin
from superprocess.remote import RemoteShellMixin

__all__ = ['Popen', 'PIPE', 'STDOUT', 'STDERR', 'call',
	'check_call', 'check_output', 'CalledProcessError']

impl = superprocess()

PIPE = impl.PIPE
STDOUT = impl.PIPE
STDERR = redirect.STDERR
CalledProcessError = impl.CalledProcessError

class Popen(
		RedirectMixin,
		RemoteShellMixin,
		impl.Popen):
	pass
impl.Popen = Popen
impl.popen = popen(impl)

call = impl.call
check_call = impl.check_call
check_output = impl.check_output
popen = impl.popen
