import io
import subprocess as _subprocess
import types
from functools import wraps

from superprocess.utils import reopen

def superprocess(subprocess=None):
	if subprocess is None:
		subprocess = _subprocess

	module = types.ModuleType('superprocess', subprocess.__doc__)

	module.__all__ = ['Popen', 'PIPE', 'STDOUT', 'call',
		'check_call', 'check_output', 'CalledProcessError']

	module.PIPE = subprocess.PIPE
	module.STDOUT = subprocess.STDOUT
	module.CalledProcessError = subprocess.CalledProcessError

	module.call = wraps(subprocess.call)(call(module))
	module.check_call = wraps(subprocess.check_call)(check_call(module))
	module.check_output = check_output(module)
	try:
		module.check_output = wraps(subprocess.check_output)(module.check_output)
	except AttributeError:
		pass  # check_output not defined in Python 2.6

	bases = (subprocess.Popen,)
	if not issubclass(subprocess.Popen, Py2Mixin):
		bases = (Py2Mixin,) + bases
	if not issubclass(subprocess.Popen, CheckMixin):
		bases = (CheckMixin,) + bases
	module.Popen = type('Popen', bases, {})

	return module

def call(subprocess):
	def call(*args, **kwargs):
		# don't allow pipe, as it is likely to deadlock
		for s in ('stdin', 'stdout', 'stderr'):
			if kwargs.get(s) == subprocess.PIPE:
				raise ValueError('PIPE not allowed when waiting for process')
		return subprocess.Popen(*args, **kwargs).wait()
	return call

def check_call(subprocess):
	def check_call(*args, **kwargs):
		return subprocess.call(*args, check=True, **kwargs)
	return check_call

def check_output(subprocess):
	def check_output(*args, **kwargs):
		# don't allow stdout arg, it needs to be set to PIPE here
		if 'stdout' in kwargs:
			raise ValueError('stdout argument not allowed, it will be overridden')
		out, err = subprocess.Popen(
			*args, stdout=subprocess.PIPE, check=True, **kwargs
		).communicate()
		return out
	return check_output

# Popen mixin to improve consistency between Python 2 and 3
class Py2Mixin(object):
	def __init__(self, *args, **kwargs):
		bufsize = kwargs.pop('bufsize', -1)
		universal_newlines = kwargs.pop('universal_newlines', False)

		# initialise process
		super(Py2Mixin, self).__init__(*args, bufsize=bufsize,
			universal_newlines=universal_newlines, **kwargs)

		# reopen standard streams with io module
		if self.stdin and not isinstance(self.stdin, io.IOBase):
			self.stdin = reopen(self.stdin, 'wb', bufsize)
			if universal_newlines:
				self.stdin = io.TextIOWrapper(self.stdin,
					write_through=True, line_buffering=(bufsize == 1))
		if self.stdout and not isinstance(self.stdout, io.IOBase):
			self.stdout = reopen(self.stdout, 'rb', bufsize)
			if universal_newlines:
				self.stdout = io.TextIOWrapper(self.stdout)
		if self.stderr and not isinstance(self.stderr, io.IOBase):
			self.stderr = reopen(self.stderr, 'rb', bufsize)
			if universal_newlines:
				self.stderr = io.TextIOWrapper(self.stderr)

# Popen mixin that adds support for checking the return code on poll / wait
class CheckMixin(object):
	def __init__(self, cmd, *args, **kwargs):
		check = kwargs.pop('check', False)

		super(CheckMixin, self).__init__(cmd, *args, **kwargs)
		self.cmd = cmd
		self._check = check

	def check_returncode(self):
		if self.returncode:
			raise _subprocess.CalledProcessError(self.returncode, self.cmd)

	def poll(self):
		super(CheckMixin, self).poll()
		if self._check:
			self.check_returncode()
		return self.returncode

	def wait(self):
		super(CheckMixin, self).wait()
		if self._check:
			self.check_returncode()
		return self.returncode
