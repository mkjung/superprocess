from superprocess import base, pipe, redirect, remote

def Superprocess(subprocess=None):
	# create base superprocess module
	superprocess = base.Superprocess(subprocess)

	# apply extensions from submodules
	superprocess.__all__ = ['Popen', 'PIPE', 'STDOUT', 'STDERR',
		'call', 'check_call', 'getstatusoutput', 'getoutput', 'check_output',
		'popen', 'run', 'CalledProcessError', 'CompletedProcess']
	superprocess.Popen = remote.Popen(superprocess, superprocess.Popen)
	superprocess.STDERR = redirect.STDERR
	superprocess.Popen = redirect.Popen(superprocess, superprocess.Popen)
	superprocess.popen = pipe.popen(superprocess)

	return superprocess

# create default superprocess instance and extract into module namespace
impl = Superprocess()
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
