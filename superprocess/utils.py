import io
import weakref

# Alternative to types.MethodType that weakly binds a method
class WeaklyBoundMethod(object):
	__slots__ = ('__func__', '__ref__', )

	def __init__(self, function, instance):
		self.__func__ = function
		self.__ref__ = weakref.ref(instance)

	@property
	def __self__(self):
		return self.__ref__()

	def __call__(self, *args, **kwargs):
		__func__ = self.__func__
		__self__ = self.__self__

		if __self__ is None:
			raise ReferenceError('weakly-referenced object no longer exists')

		return __func__(__self__, *args, **kwargs)

# Reopen file with new mode, buffer size etc using io module
def reopen(file, mode='r', buffering=-1,
		encoding=None, errors=None, newline=None):
	# create new file object over same file descriptor
	iofile = io.open(file.fileno(), mode, buffering,
		encoding, errors, newline, closefd=False)

	# override close method to close original file too
	def close(self):
		try:
			return type(self).close(self)
		finally:
			file.close()

	# weakly bind the new close method to avoid a circular reference
	iofile.close = WeaklyBoundMethod(close, iofile)

	return iofile
