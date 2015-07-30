from superprocess.utils import unbind, WeaklyBoundMethod

# Open a pipe to / from a command - similar to os.popen()
def popen(subprocess):
	def popen(cmd, mode='r', buffering=-1, check=False, **kwargs):
		if mode in ('r', 'rt', 'rb'):
			stdin, stdout = None, subprocess.PIPE
		elif mode in ('w', 'wt', 'wb'):
			stdin, stdout = subprocess.PIPE, None
		else:
			raise ValueError('invalid mode %s' % mode)

		p = subprocess.Popen(cmd, bufsize=buffering, stdin=stdin, stdout=stdout,
			universal_newlines=(mode[-1] != 'b'), **kwargs)

		# detach stream so that it can be managed independently
		f = p.stdin or p.stdout
		p.stdin, p.stdout = None, None

		# override close method to return the exit status
		_close = unbind(f.close)
		def close(self):
			_close(self)
			stdout, stderr = p.communicate()
			result = subprocess.CompletedProcess(p.args, p.returncode, stdout, stderr)
			if check:
				result.check_returncode()
			return result.returncode

		# weakly bind the new close method to avoid a circular reference
		f.close = WeaklyBoundMethod(close, f)

		return f
	return popen
