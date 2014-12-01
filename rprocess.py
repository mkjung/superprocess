import pipes
import subprocess


# subprocess overrides
def call(*popenargs, **kwargs):
	with connect(kwargs.pop('netloc', None)) as connection:
		return connection.call(*popenargs, **kwargs)

def check_call(*popenargs, **kwargs):
	with connect(kwargs.pop('netloc', None)) as connection:
		return connection.check_call(*popenargs, **kwargs)

def check_output(*popenargs, **kwargs):
	with connect(kwargs.pop('netloc', None)) as connection:
		return connection.check_output(*popenargs, **kwargs)

def Popen(*popenargs, **kwargs):
	with connect(kwargs.pop('netloc', None)) as connection:
		return connection.Popen(*popenargs, **kwargs)

# open a connection that can be used to execute processes
def connect(netloc):
	# use local connection if netloc is empty
	if not netloc:
		return LocalConnection()

	# split netloc
	user, _, host = netloc.rpartition('@')
	username, _, password = user.partition(':')
	hostname, _, port = host.partition(':')

	# don't use remote shell for localhost unless user or port is specified
	if not username and not port and hostname in {'localhost', '127.0.0.1'}:
		return LocalConnection()

	return RemoteShellConnection(hostname, port, username, password)

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

class RemoteShellConnection(object):
	def __init__(self, hostname, port=None, username=None, password=None, remote_shell=None):
		# use ssh as default remote shell
		if not remote_shell:
			remote_shell = ['ssh']
		elif isinstance(remote_shell, basestring):
			remote_shell = [remote_shell]
		else:
			remote_shell = list(remote_shell)

		# set remote user and host
		if username:
			remote_shell.append('-l')
			remote_shell.append(username)
		remote_shell.append(hostname)

		# store remote shell command list
		self.remote_shell = remote_shell

	def __enter__(self):
		return self

	def __exit__(self, *exc):
		self.close()
		return False

	def close(self):
		pass

	# call subprocess function after adjusting cmd to run in remote shell
	def _call(self, f, cmd, *args, **kwargs):
		# quote command for remote shell if provided as list
		if isinstance(cmd, basestring):
			cmd = [cmd]
		else:
			cmd = [pipes.quote(x) for x in cmd]
		cmd = self.remote_shell + cmd

		# shell option not suitable for command list
		kwargs['shell'] = False

		# call function with updated args
		return f(cmd, *args, **kwargs)

	def call(self, *args, **kwargs):
		return self._call(subprocess.call, *args, **kwargs)

	def check_call(self, *args, **kwargs):
		return self._call(subprocess.check_call, *args, **kwargs)

	def check_output(self, *args, **kwargs):
		return self._call(subprocess.check_output, *args, **kwargs)

	def Popen(self, *args, **kwargs):
		return self._call(subprocess.Popen, *args, **kwargs)
