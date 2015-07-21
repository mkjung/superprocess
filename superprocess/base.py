import subprocess
import types

class PopenMixin(object):
	@classmethod
	def call(Popen, *args, **kwargs):
		# don't allow pipe, as it is likely to deadlock
		for s in ('stdin', 'stdout', 'stderr'):
			if kwargs.get(s) == subprocess.PIPE:
				raise ValueError('PIPE not allowed when waiting for process')

		return Popen(*args, **kwargs).wait()

	@classmethod
	def check_call(Popen, *args, **kwargs):
		return Popen.call(*args, fail_on_error=True, **kwargs)

	@classmethod
	def check_output(Popen, *args, **kwargs):
		# don't allow stdout arg, it needs to be set to PIPE here
		if 'stdout' in kwargs:
			raise ValueError('stdout argument not allowed, it will be overridden')

		out, err = Popen(
			*args, stdout=subprocess.PIPE, fail_on_error=True, **kwargs
		).communicate()
		return out

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

def superprocess(subprocess=subprocess):
	module = types.ModuleType('superprocess', subprocess.__doc__)

	module.__all__ = ['Popen', 'PIPE', 'STDOUT', 'call',
		'check_call', 'check_output', 'CalledProcessError']

	module.PIPE = subprocess.PIPE
	module.STDOUT = subprocess.STDOUT
	module.CalledProcessError = subprocess.CalledProcessError

	Popen = subprocess.Popen
	if not issubclass(Popen, PopenMixin):
		Popen = type('Popen', (PopenMixin, Popen,), {})

	module.Popen = Popen
	module.call = Popen.call
	module.check_call = Popen.check_call
	module.check_output = Popen.check_output

	return module

class SubprocessContext(object):
	def __init__(self, subprocess=subprocess):
		self.subprocess = subprocess

	def __enter__(self):
		return self.subprocess

	def __exit__(self, *exc):
		self.close()
		return False

	def close(self):
		pass
