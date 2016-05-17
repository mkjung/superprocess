from superprocess.utils import unbind, WeaklyBoundMethod

# Open a pipe to / from a command - similar to os.popen()
def popen(subprocess):
	def popen(cmd, mode='r', buffering=-1, **kwargs):
		if mode in ('r', 'rt', 'rb'):
			stdin, stdout = None, subprocess.PIPE
		elif mode in ('w', 'wt', 'wb'):
			stdin, stdout = subprocess.PIPE, None
		else:
			raise ValueError('invalid mode %s' % mode)

		p = subprocess.Popen(cmd, bufsize=buffering, stdin=stdin, stdout=stdout,
			universal_newlines=(mode[-1] != 'b'), **kwargs)

		# detach stream so that it can be managed independently,
		# and to break circular reference f -> close -> p -> f
		f = p.stdin or p.stdout
		p.stdin, p.stdout = None, None

		# store reference to underlying close method, taking care not
		# to create a circular reference f -> close -> _close -> f
		_close = f.close
		if getattr(_close, '__self__', None) is f:
			_close = WeaklyBoundMethod(unbind(_close), f)

		# override close method to check the return code
		def close():
			_close()
			stdout, stderr = p.communicate()
			result = subprocess.CompletedProcess(p.args, p.returncode, stdout, stderr)
			result.check_returncode()
		f.close = close

		return f
	return popen
