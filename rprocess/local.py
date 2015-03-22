import subprocess

def call(*args, **kwargs):
	with LocalConnection() as connection:
		return connection.call(*args, **kwargs)

def check_call(*args, **kwargs):
	with LocalConnection() as connection:
		return connection.check_call(*args, **kwargs)

def check_output(*args, **kwargs):
	with LocalConnection() as connection:
		return connection.check_output(*args, **kwargs)

def Popen(*args, **kwargs):
	with LocalConnection() as connection:
		return connection.Popen(*args, **kwargs)

class LocalConnection(object):
	def __enter__(self):
		return self

	def __exit__(self, *exc):
		self.close()
		return False

	def close(self):
		pass

	def call(self, *args, **kwargs):
		return subprocess.call(*args, **kwargs)

	def check_call(self, *args, **kwargs):
		return subprocess.check_call(*args, **kwargs)

	def check_output(self, *args, **kwargs):
		return subprocess.check_output(*args, **kwargs)

	def Popen(self, *args, **kwargs):
		return subprocess.Popen(*args, **kwargs)
