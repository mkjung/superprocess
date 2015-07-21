import subprocess
import types
from functools import wraps

def superprocess(subprocess=subprocess):
	module = types.ModuleType('superprocess', subprocess.__doc__)

	module.__all__ = ['Popen', 'PIPE', 'STDOUT', 'call',
		'check_call', 'check_output', 'CalledProcessError']

	module.PIPE = subprocess.PIPE
	module.STDOUT = subprocess.STDOUT
	module.CalledProcessError = subprocess.CalledProcessError

	module.call = wraps(subprocess.call)(call(module))
	module.check_call = wraps(subprocess.check_call)(check_call(module))
	module.check_output = check_output(module)
	try:
		module.check_output = wraps(subprocess.check_output)(module.check_output)
	except AttributeError:
		pass  # check_output not defined in Python 2.6

	bases = (subprocess.Popen,)
	if not issubclass(subprocess.Popen, PopenMixin):
		bases = (PopenMixin,) + bases
	module.Popen = type('Popen', bases, {})

	return module

def call(subprocess):
	def call(*args, **kwargs):
		# don't allow pipe, as it is likely to deadlock
		for s in ('stdin', 'stdout', 'stderr'):
			if kwargs.get(s) == subprocess.PIPE:
				raise ValueError('PIPE not allowed when waiting for process')
		return subprocess.Popen(*args, **kwargs).wait()
	return call

def check_call(subprocess):
	def check_call(*args, **kwargs):
		return subprocess.call(*args, fail_on_error=True, **kwargs)
	return check_call

def check_output(subprocess):
	def check_output(*args, **kwargs):
		# don't allow stdout arg, it needs to be set to PIPE here
		if 'stdout' in kwargs:
			raise ValueError('stdout argument not allowed, it will be overridden')
		out, err = subprocess.Popen(
			*args, stdout=subprocess.PIPE, fail_on_error=True, **kwargs
		).communicate()
		return out
	return check_output

class PopenMixin(object):
	def __init__(self, cmd, *args, **kwargs):
		fail_on_error = kwargs.pop('fail_on_error', False)

		super(PopenMixin, self).__init__(cmd, *args, **kwargs)
		self.cmd = cmd
		self._fail_on_error = fail_on_error

	def check(self):
		if self.returncode:
			raise subprocess.CalledProcessError(self.returncode, self.cmd)

	def poll(self):
		super(PopenMixin, self).poll()
		if self._fail_on_error:
			self.check()
		return self.returncode

	def wait(self):
		super(PopenMixin, self).wait()
		if self._fail_on_error:
			self.check()
		return self.returncode
