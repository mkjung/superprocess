import pipes
import subprocess

from superprocess.base import SubprocessModule, SubprocessContext

try:
	string_types = basestring  # Python 2
except NameError:
	string_types = str  # Python 3

# open a connection that can be used to execute processes
def connect(netloc):
	# use default context if netloc is empty
	if not netloc:
		return SubprocessContext()

	# split netloc
	user, _, host = netloc.rpartition('@')
	username, _, password = user.partition(':')
	hostname, _, port = host.partition(':')

	# don't use remote shell for localhost unless user or port is specified
	if not username and not port and hostname in ('localhost', '127.0.0.1',):
		return SubprocessContext()

	return RemoteShellConnection(hostname, port, username, password)

class RemoteShellConnection(SubprocessContext):
	def __init__(self, hostname, port=None,
			username=None, password=None,
			remote_shell=None, subprocess=subprocess):
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

		# create custom Popen class to run commands in remote shell
		class Popen(subprocess.Popen):
			def __init__(self, cmd, *args, **kwargs):
				# quote command for remote shell if provided as list
				if isinstance(cmd, string_types):
					cmd = [cmd]
				else:
					cmd = [pipes.quote(x) for x in cmd]
				cmd = remote_shell + cmd

				# shell option not suitable for command list
				kwargs['shell'] = False

				super(Popen, self).__init__(cmd, *args, **kwargs)

		super(RemoteShellConnection, self).__init__(SubprocessModule(Popen))
