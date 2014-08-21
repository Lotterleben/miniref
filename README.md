miniref.py is a small utility to make sorting out references in lengthy e-mails just a bit less cumbersome.

# make it work
Write what you need to say into a text file. Mark each reference with ``[x]`` in the text and put whatever you want to refer to at the end of your e-mail, after the signature, in this format: ``[x] http://zombietetris.de``. ``x`` can be any alphanumerical character or special character except for ``[`` or ``]``.

You can find an example of what a compatible file should look like in ```example.txt```.

Then, run

	python miniref-py -f path/to/your/textfile.txt

Afterwards, your references in ``textfile.txt`` should be numbered neatly.