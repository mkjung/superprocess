import io
import sys
import types
try:
	import subprocess32 as _subprocess
except ImportError:
	import subprocess as _subprocess

from superprocess.utils import reopen

def Superprocess(subprocess=None):
	if subprocess is None:
		subprocess = _subprocess
	assert subprocess.PIPE == PIPE
	assert subprocess.STDOUT == STDOUT

	superprocess = types.ModuleType('superprocess', subprocess.__doc__)

	superprocess.__all__ = ['Popen', 'PIPE', 'STDOUT', 'call', 'check_call',
		'getstatusoutput', 'getoutput', 'check_output', 'run',
		'CalledProcessError', 'CompletedProcess']

	superprocess.PIPE = subprocess.PIPE
	superprocess.STDOUT = subprocess.STDOUT
	superprocess.CalledProcessError = subprocess.CalledProcessError
	superprocess.CompletedProcess = CompletedProcess(superprocess)

	superprocess.run = run(superprocess)
	superprocess.call = call(superprocess)
	superprocess.check_call = check_call(superprocess)
	superprocess.check_output = check_output(superprocess)
	superprocess.getstatusoutput = getstatusoutput(superprocess)
	superprocess.getoutput = getoutput(superprocess)

	superprocess.Popen = Popen(superprocess, subprocess.Popen)

	return superprocess

PIPE = _subprocess.PIPE
STDOUT = _subprocess.STDOUT

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

def getstatusoutput(subprocess):
	def getstatusoutput(cmd):
		p = subprocess.run(cmd, shell=True, universal_newlines=True,
			stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		status, output = p.returncode, p.stdout
		if output.endswith('\n'):
			output = output[:-1]
		return status, output
	return getstatusoutput

def getoutput(subprocess):
	def getoutput(cmd):
		return subprocess.getstatusoutput(cmd)[1]
	return getoutput

# Python 2 compatibility mixin to partly emulate Python 3 Popen interface
class Py2PopenMixin(object):
	def __init__(self, cmd, *args, **kwargs):
		super(Py2PopenMixin, self).__init__(cmd, *args, **kwargs)
		self.args = cmd

	def __enter__(self):
		return self

	def __exit__(self, *exc):
		for f in (self.stdin, self.stdout, self.stderr):
			if f: f.close()
		self.wait()

# Python 2 compatibility mixin to provide streams as io-module files
class Py2IOMixin(object):
	def __init__(self, cmd, *args, **kwargs):
		bufsize = kwargs.pop('bufsize', -1)
		universal_newlines = kwargs.pop('universal_newlines', False)

		# initialise process
		super(Py2IOMixin, self).__init__(cmd, *args, bufsize=0,
			universal_newlines=False, **kwargs)

		# reopen standard streams with io module
		if self.stdin:
			self.stdin = reopen(self.stdin, 'wb', bufsize)
			if universal_newlines:
				self.stdin = io.TextIOWrapper(self.stdin,
					write_through=True, line_buffering=(bufsize == 1))
		if self.stdout:
			self.stdout = reopen(self.stdout, 'rb', bufsize)
			if universal_newlines:
				self.stdout = io.TextIOWrapper(self.stdout)
		if self.stderr:
			self.stderr = reopen(self.stderr, 'rb', bufsize)
			if universal_newlines:
				self.stderr = io.TextIOWrapper(self.stderr)

def Popen(subprocess, PopenBase):
	mixins = ()
	if sys.version_info[0] < 3:
		mixins = (Py2IOMixin,) + mixins
	if not hasattr(PopenBase, '__enter__'):
		mixins = (Py2PopenMixin,) + mixins
	if mixins:
		return type('Popen', mixins + (PopenBase,), {})

	return PopenBase
