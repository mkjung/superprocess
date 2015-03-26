import subprocess

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
