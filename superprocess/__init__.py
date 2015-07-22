from superprocess.base import superprocess
from superprocess.popen import popen
from superprocess.redirect import RedirectMixin
from superprocess.remote import RemoteShellMixin

__all__ = ['Popen', 'PIPE', 'STDOUT', 'STDERR', 'call',
	'check_call', 'check_output', 'CalledProcessError']

# create default superprocess instance
impl = superprocess()

# apply extensions from submodules
impl.STDERR = redirect.STDERR
impl.popen = popen(impl)
impl.Popen = type('Popen',
	(RedirectMixin, RemoteShellMixin, impl.Popen,), {})

# extract items into superprocess namespace
PIPE = impl.PIPE
STDOUT = impl.PIPE
STDERR = impl.STDERR
CalledProcessError = impl.CalledProcessError
call = impl.call
check_call = impl.check_call
check_output = impl.check_output
popen = impl.popen
Popen = impl.Popen
