from superprocess.utils import WeaklyBoundMethod

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
		f = p.stdin or p.stdout

		# override close method to return the exit status
		def close(self):
			type(self).close(self)
			returncode = p.wait()
			if returncode:
				return returncode

		# weakly bind the new close method to avoid a circular reference
		f.close = WeaklyBoundMethod(close, f)

		return f
	return popen
