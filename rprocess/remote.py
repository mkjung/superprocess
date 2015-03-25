import pipes

from rprocess.local import LocalConnection

def call(*args, **kwargs):
	with connect(kwargs.pop('netloc', None)) as connection:
		return connection.call(*args, **kwargs)

def check_call(*args, **kwargs):
	with connect(kwargs.pop('netloc', None)) as connection:
		return connection.check_call(*args, **kwargs)

def check_output(*args, **kwargs):
	with connect(kwargs.pop('netloc', None)) as connection:
		return connection.check_output(*args, **kwargs)

def Popen(*args, **kwargs):
	with connect(kwargs.pop('netloc', None)) as connection:
		return connection.Popen(*args, **kwargs)

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

class RemoteShellConnection(LocalConnection):
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

	# apply function f with cmd adjusted to run in remote shell
	def apply(self, f, cmd, *args, **kwargs):
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
		return self.apply(
			super(RemoteShellConnection, self).call, *args, **kwargs)

	def check_call(self, *args, **kwargs):
		return self.apply(
			super(RemoteShellConnection, self).check_call, *args, **kwargs)

	def check_output(self, *args, **kwargs):
		return self.apply(
			super(RemoteShellConnection, self).check_output, *args, **kwargs)

	def Popen(self, *args, **kwargs):
		return self.apply(
			super(RemoteShellConnection, self).Popen, *args, **kwargs)
