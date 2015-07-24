import io
import subprocess as _subprocess
import types

from superprocess.utils import reopen

def superprocess(subprocess=None):
	if subprocess is None:
		subprocess = _subprocess

	module = types.ModuleType('superprocess', subprocess.__doc__)

	module.__all__ = ['Popen', 'PIPE', 'STDOUT', 'call', 'check_call',
		'check_output', 'run', 'CalledProcessError', 'CompletedProcess']

	module.PIPE = subprocess.PIPE
	module.STDOUT = subprocess.STDOUT
	module.CalledProcessError = subprocess.CalledProcessError
	module.CompletedProcess = CompletedProcess(module)

	module.run = run(module)
	module.call = call(module)
	module.check_call = check_call(module)
	module.check_output = check_output(module)

	module.Popen = type('Popen', (CheckMixin, Py2Mixin, subprocess.Popen), {})

	return module

def CompletedProcess(subprocess):
	class CompletedProcess(object):
		def __init__(self, args, returncode, stdout=None, stderr=None):
			self.args = args
			self.returncode = returncode
			self.stdout = stdout
			self.stderr = stderr

		def check_returncode(self):
			if self.returncode:
				raise subprocess.CalledProcessError(self.returncode, self.args)
	return CompletedProcess

def run(subprocess):
	def run(*args, **kwargs):
		input = kwargs.pop('input', None)
		check = kwargs.pop('check', False)

		if input is not None:
			if 'stdin' in kwargs:
				raise ValueError('stdin and input arguments may not both be used')
			kwargs['stdin'] = subprocess.PIPE

		p = subprocess.Popen(*args, **kwargs)
		stdout, stderr = p.communicate(input)
		result = subprocess.CompletedProcess(p.args, p.returncode, stdout, stderr)
		if check:
			result.check_returncode()
		return result
	return run

def call(subprocess):
	def call(*args, **kwargs):
		return subprocess.run(*args, **kwargs).returncode
	return call

def check_call(subprocess):
	def check_call(*args, **kwargs):
		return subprocess.run(*args, check=True, **kwargs).returncode
	return check_call

def check_output(subprocess):
	def check_output(*args, **kwargs):
		# don't allow stdout arg, it needs to be set to PIPE here
		if 'stdout' in kwargs:
			raise ValueError('stdout argument not allowed, it will be overridden')
		return subprocess.run(
			*args, stdout=subprocess.PIPE, check=True, **kwargs).stdout
	return check_output

# Popen mixin to improve consistency between Python 2 and 3
class Py2Mixin(object):
	def __init__(self, cmd, *args, **kwargs):
		bufsize = kwargs.pop('bufsize', -1)
		universal_newlines = kwargs.pop('universal_newlines', False)

		# initialise process
		super(Py2Mixin, self).__init__(cmd, *args, bufsize=bufsize,
			universal_newlines=universal_newlines, **kwargs)
		if not hasattr(self, 'args'):
			self.args = cmd

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
	def __init__(self, *args, **kwargs):
		self._check = kwargs.pop('check', False)
		super(CheckMixin, self).__init__(*args, **kwargs)

	def check_returncode(self):
		if self.returncode:
			raise _subprocess.CalledProcessError(self.returncode, self.args)

	def poll(self):
		super(CheckMixin, self).poll()
		if self._check:
			self.check_returncode()
		return self.returncode

	def wait(self, *args, **kwargs):
		super(CheckMixin, self).wait(*args, **kwargs)
		if self._check:
			self.check_returncode()
		return self.returncode
