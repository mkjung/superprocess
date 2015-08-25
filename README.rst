superprocess
============
Superprocess facilitates extending the built-in subprocess module.
You can extend superprocess to add custom behaviour or use the bundled
extensions, most notably support for running remote processes.

Installation
------------
Requires Python 2.6, 2.7 or 3.4+.

To install superprocess, simply::

	$ pip install superprocess

Usage
-----
Run a remote command::

	>>> superprocess.check_output('echo $SSH_CONNECTION', netloc='127.0.0.1', shell=True)
	b'127.0.0.1 56924 127.0.0.1 22\n'

Open a pipe to a command::

	>>> with superprocess.popen('ls') as f:
	...   for line in f:
	...     print(line.strip())
	...
	README.rst
	setup.py
	superprocess
	superprocess.egg-info

Note: close() will raise a CalledProcessError if the return code is non-zero::

	>>> f = superprocess.popen('echo Hello World!; exit 1', shell=True)
	>>> f.read()
	'Hello World!\n'
	>>> f.close()
	Traceback (most recent call last):
		...
	subprocess.CalledProcessError: Command 'echo Hello World!; exit 1' returned non-zero exit status 1

Customise an instance of superprocess to use the shell by default::

	>>> from superprocess import Superprocess
	>>> superprocess = Superprocess()
	>>> superprocess.run = functools.partial(superprocess.run, shell=True)
	>>> superprocess.call('exit 1')
	1

License
-------
Licensed under the Apache License, Version 2.0.
