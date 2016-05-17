import io
import types
import weakref

# Create a weakly-bound proxy for a bound method
def weakmethodproxy(method):
	try:
		instance = method.__self__

		if isinstance(method, types.BuiltinMethodType):
			function = getattr(type(instance), method.__name__)
		else:
			function = method.__func__
	except AttributeError:
		raise TypeError('argument should be a bound method, not %s', type(method))

	return WeaklyBoundMethod(function, instance)

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

	# store reference to underlying close method, taking care not
	# to create a circular reference f -> close -> _close -> f
	_close = iofile.close
	if getattr(_close, '__self__', None) is iofile:
		_close = weakmethodproxy(_close)

	# override close method to close the original file too
	def close():
		try:
			_close()
		finally:
			file.close()
	iofile.close = close

	return iofile
