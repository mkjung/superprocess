import pipes
try:
	from urllib.parse import SplitResult
except ImportError:
	from urlparse import SplitResult

try:
	string_types = basestring  # Python 2
except NameError:
	string_types = str  # Python 3

# open a connection that can be used to execute processes
def connect(netloc, remote_shell=None):
	url = SplitResult(None, netloc, None, None, None)
	return RemoteShellConnection(
		url.hostname, url.port, url.username, url.password, remote_shell)

class RemoteShellConnection(object):
	def __init__(self, hostname, port=None,
			username=None, password=None, remote_shell=None):
		# use ssh as default remote shell
		if not remote_shell:
			remote_shell = ['ssh']
		elif isinstance(remote_shell, string_types):
			remote_shell = [remote_shell]
		else:
			remote_shell = list(remote_shell)

		# set remote user and host
		if username:
			remote_shell.append('-l')
			remote_shell.append(username)
		remote_shell.append(hostname)

		self.shell = remote_shell

	def close(self):
		pass

class ShellMixin(object):
	def __init__(self, cmd, *args, **kwargs):
		shell = kwargs.get('shell', False)

		if shell not in (True, False):
			if isinstance(shell, string_types):
				shell = [shell]
			else:
				shell = list(shell)

			# quote command for shell if provided as list
			if isinstance(cmd, string_types):
				cmd = [cmd]
			else:
				cmd = [pipes.quote(x) for x in cmd]
			cmd = shell + cmd

			kwargs['shell'] = False

		super(ShellMixin, self).__init__(cmd, *args, **kwargs)

class RemoteShellMixin(ShellMixin):
	def __init__(self, *args, **kwargs):
		netloc = kwargs.pop('netloc', None)
		remote_shell = kwargs.pop('remote_shell', None)

		if not netloc:
			self.connection = None
		else:
			self.connection = connect(netloc, remote_shell)
			kwargs['shell'] = self.connection.shell

		super(RemoteShellMixin, self).__init__(*args, **kwargs)

	def wait(self, *args, **kwargs):
		try:
			return super(RemoteShellMixin, self).wait(*args, **kwargs)
		finally:
			if self.connection:
				self.connection.close()

def Popen(subprocess, PopenBase):
	return type('Popen', (RemoteShellMixin, PopenBase,), {})
