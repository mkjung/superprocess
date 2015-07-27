from superprocess import base, pipe, redirect, remote

# create default superprocess instance
impl = base.Superprocess()

# apply extensions from submodules
impl.__all__ = ['Popen', 'PIPE', 'STDOUT', 'STDERR', 'call', 'check_call',
	'getstatusoutput', 'getoutput', 'check_output', 'popen', 'run',
	'CalledProcessError', 'CompletedProcess']
impl.STDERR = redirect.STDERR
impl.popen = pipe.popen(impl)
impl.Popen = type('Popen',
	(redirect.RedirectMixin, remote.RemoteShellMixin, impl.Popen,), {})

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
