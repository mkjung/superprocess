import pipes
import subprocess

from superprocess.base import SubprocessModule, SubprocessContext

try:
	string_types = basestring  # Python 2
except NameError:
	string_types = str  # Python 3

# open a connection that can be used to execute processes
def connect(netloc):
	# don't need shell if netloc is empty
	if not netloc:
		return NullShellConnection()

	# split netloc
	user, _, host = netloc.rpartition('@')
	username, _, password = user.partition(':')
	hostname, _, port = host.partition(':')

	# don't use remote shell for localhost unless user or port is specified
	if not username and not port and hostname in ('localhost', '127.0.0.1',):
		return NullShellConnection()

	return RemoteShellConnection(hostname, port, username, password)

class NullShellConnection(object):
	shell = False
	def close(self):
		pass

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

class RemoteContext(SubprocessContext):
	def __init__(self, netloc, remote_shell=None, subprocess=subprocess):
		self.connection = connection = connect(netloc)
		class Popen(subprocess.Popen):
			def __init__(self, cmd, *args, **kwargs):
				# quote command for remote shell if provided as list
				if isinstance(cmd, string_types):
					cmd = [cmd]
				else:
					cmd = [pipes.quote(x) for x in cmd]
				cmd = connection.shell + cmd

				# shell option not suitable for command list
				kwargs['shell'] = False

				super(Popen, self).__init__(cmd, *args, **kwargs)

		super(RemoteContext, self).__init__(SubprocessModule(Popen))

	def close(self):
		self.connection.close()
