import subprocess

from superprocess.utils import WeaklyBoundMethod

# Popen mixin that adds a classmethod similar to os.popen()
class OSPopenMixin(object):
	@classmethod
	def popen(Popen, cmd, mode='r', buffering=-1, **kwargs):
		if mode in ('r', 'rt', 'rb'):
			stdin, stdout = None, subprocess.PIPE
		elif mode in ('w', 'wt', 'wb'):
			stdin, stdout = subprocess.PIPE, None
		else:
			raise ValueError('invalid mode %s' % mode)

		p = Popen(cmd, bufsize=buffering, stdin=stdin, stdout=stdout,
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
