import subprocess
import types

class PopenMixin(object):
	@classmethod
	def call(Popen, *args, **kwargs):
		return Popen(*args, **kwargs).wait()

	@classmethod
	def check_call(Popen, *args, **kwargs):
		return Popen.call(*args, fail_on_error=True, **kwargs)

	@classmethod
	def check_output(Popen, *args, **kwargs):
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

class SubprocessModule(types.ModuleType):
	__all__ = ['Popen', 'PIPE', 'STDOUT', 'call',
		'check_call', 'check_output', 'CalledProcessError']

	PIPE = subprocess.PIPE
	STDOUT = subprocess.PIPE
	CalledProcessError = subprocess.CalledProcessError

	def __init__(self, Popen, name='subprocess', doc=None):
		super(SubprocessModule, self).__init__(name, doc)

		if not issubclass(Popen, PopenMixin):
			Popen = type('Popen', (PopenMixin, Popen,), {})

		self.Popen = Popen
		self.call = Popen.call
		self.check_call = Popen.check_call
		self.check_output = Popen.check_output

class LocalConnection(object):
	def __init__(self, subprocess=subprocess):
		self.subprocess = subprocess

	def __enter__(self):
		return self

	def __exit__(self, *exc):
		self.close()
		return False

	def close(self):
		pass

	def apply(self, f, *args, **kwargs):
		return f(*args, **kwargs)

	def call(self, *args, **kwargs):
		return self.apply(self.subprocess.call, *args, **kwargs)

	def check_call(self, *args, **kwargs):
		return self.apply(self.subprocess.check_call, *args, **kwargs)

	def check_output(self, *args, **kwargs):
		return self.apply(self.subprocess.check_output, *args, **kwargs)

	def Popen(self, *args, **kwargs):
		return self.apply(self.subprocess.Popen, *args, **kwargs)
