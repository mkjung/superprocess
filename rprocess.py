import pipes
import subprocess


# prepare command for remote execution
def remote_cmd(cmd, netloc=None, remote_shell=None):
	# don't attempt remote shell if command or netloc empty
	if not cmd or not netloc:
		return cmd

	# split netloc
	username, _, hostname = netloc.rpartition('@')

	# don't use remote shell for localhost unless user is specified
	if not username and hostname in {'localhost', '127.0.0.1'}:
		return cmd

	# use ssh as default remote shell
	if not remote_shell:
		rsh_cmd = ['ssh']
	elif isinstance(remote_shell, basestring):
		rsh_cmd = [remote_shell]
	else:
		rsh_cmd = list(remote_shell)

	# set remote user and host
	if username:
		rsh_cmd.append('-l')
		rsh_cmd.append(username)
	rsh_cmd.append(hostname)

	# quote command for remote shell if provided as list
	if isinstance(cmd, basestring):
		rsh_cmd.append(cmd)
	else:
		rsh_cmd.extend(pipes.quote(x) for x in cmd)

	return rsh_cmd

# subprocess overrides
def Popen(*popenargs, **kwargs):
	netloc = kwargs.pop('netloc', None)
	remote_shell = kwargs.pop('remote_shell', None)
	cmd = remote_cmd(popenargs[0], netloc, remote_shell)
	return subprocess.Popen(cmd, *popenargs[1:], **kwargs)

def call(*popenargs, **kwargs):
	netloc = kwargs.pop('netloc', None)
	remote_shell = kwargs.pop('remote_shell', None)
	cmd = remote_cmd(popenargs[0], netloc, remote_shell)
	return subprocess.call(cmd, *popenargs[1:], **kwargs)

def check_call(*popenargs, **kwargs):
	netloc = kwargs.pop('netloc', None)
	remote_shell = kwargs.pop('remote_shell', None)
	cmd = remote_cmd(popenargs[0], netloc, remote_shell)
	return subprocess.check_call(cmd, *popenargs[1:], **kwargs)

def check_output(*popenargs, **kwargs):
	netloc = kwargs.pop('netloc', None)
	remote_shell = kwargs.pop('remote_shell', None)
	cmd = remote_cmd(popenargs[0], netloc, remote_shell)
	return subprocess.check_output(cmd, *popenargs[1:], **kwargs)
