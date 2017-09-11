================
InvoiceGenerator
================
.. image:: https://travis-ci.org/creckx/InvoiceGenerator.svg
    :target: https://travis-ci.org/creckx/InvoiceGenerator

This is library to generate a simple invoices.
Currently supported formats are PDF and XML for Pohoda accounting system.
PDF invoice is based on ReportLab.

Installation
============

Run this command as root::

	pip install InvoiceGenerator

If you want upgrade to new version, add ``--upgrade`` flag::

	pip install InvoiceGenerator --upgrade

You can use setup.py from GitHub repository too::

	python setup.py install


Documentation
-------------

Complete documentation is available on
`Read The Docs <http://readthedocs.org/docs/InvoiceGenerator/>`_.


Example
=======

Basic API
---------

Define invoice data first::

	import os

	from tempfile import NamedTemporaryFile

	from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator

	# choose english as language
	os.environ["INVOICE_LANG"] = "en"

	client = Client('Client company')
	provider = Provider('My company', bank_account='2600420569', bank_code='2010')
	creator = Creator('John Doe')

	invoice = Invoice(client, provider, creator)
	invoice.currency_locale = 'en_US.UTF-8'
	invoice.add_item(Item(32, 600, description="Item 1"))
	invoice.add_item(Item(60, 50, description="Item 2", tax=21))
	invoice.add_item(Item(50, 60, description="Item 3", tax=0))
	invoice.add_item(Item(5, 600, description="Item 4", tax=15))

Note: Due to Python's representational error, write numbers as integer ``tax=10``,
Decimal ``tax=Decimal('10.1')`` or string ``tax='1.2'`` to avoid getting results with
lot of decimal places.

PDF
---

Generate PDF invoice file::

	from InvoiceGenerator.pdf import SimpleInvoice

	pdf = SimpleInvoice(invoice)
	pdf.gen("invoice.pdf", generate_qr_code=True)


Pohoda XML
----------

Generate XML invoice file::

	from InvoiceGenerator.pohoda import SimpleInvoice

	pdf = SimpleInvoice(invoice)
	pdf.gen("invoice.xml")

Note: Pohoda uses three tax rates: none: 0%, low: 15%, high: 21%.
If any item doesn't meet those percentage, the rateVat parameter will
not be set for those items resulting in 0% tax rate.

Only SimpleInvoice is currently supported for Pohoda XML format.


Hacking
=======

Fork the `repository on github <https://github.com/creckx/InvoiceGenerator>`_ and
write code. Make sure to add tests covering your code under `/tests/`. You can
run tests using::

    python setup.py test

Then propose your patch via a pull request.

Documentation is generated from `doc/source/` using `Sphinx
<http://sphinx-doc.org/>`_::

    python setup.py build_sphinx

Then head to `doc/build/html/index.html`.
