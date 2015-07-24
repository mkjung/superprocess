from superprocess.base import superprocess
from superprocess.popen import popen
from superprocess.redirect import STDERR, RedirectMixin
from superprocess.remote import RemoteShellMixin

# create default superprocess instance
impl = superprocess()

# apply extensions from submodules
impl.__all__ = ['Popen', 'PIPE', 'STDOUT', 'STDERR', 'call', 'check_call',
	'getstatusoutput', 'getoutput', 'check_output', 'popen', 'run',
	'CalledProcessError', 'CompletedProcess']
impl.STDERR = STDERR
impl.popen = popen(impl)
impl.Popen = type('Popen',
	(RedirectMixin, RemoteShellMixin, impl.Popen,), {})

# extract items into superprocess namespace
__all__ = impl.__all__
PIPE = impl.PIPE
STDOUT = impl.STDOUT
STDERR = impl.STDERR
CalledProcessError = impl.CalledProcessError
CompletedProcess = impl.CompletedProcess
run = impl.run
call = impl.call
check_call = impl.check_call
check_output = impl.check_output
getstatusoutput = impl.getstatusoutput
getoutput = impl.getoutput
popen = impl.popen
Popen = impl.Popen
