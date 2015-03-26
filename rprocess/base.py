import subprocess

class PopenBase(subprocess.Popen):
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

		super(PopenBase, self).__init__(cmd, *args, **kwargs)
		self.cmd = cmd
		self._fail_on_error = fail_on_error

	def check(self):
		if self.returncode:
			raise subprocess.CalledProcessError(self.returncode, self.cmd)

	def poll(self):
		super(PopenBase, self).poll()
		if self._fail_on_error:
			self.check()
		return self.returncode

	def wait(self):
		super(PopenBase, self).wait()
		if self._fail_on_error:
			self.check()
		return self.returncode

class LocalConnection(object):
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
		return self.apply(subprocess.call, *args, **kwargs)

	def check_call(self, *args, **kwargs):
		return self.apply(subprocess.check_call, *args, **kwargs)

	def check_output(self, *args, **kwargs):
		return self.apply(subprocess.check_output, *args, **kwargs)

	def Popen(self, *args, **kwargs):
		return self.apply(subprocess.Popen, *args, **kwargs)
