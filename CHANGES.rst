History
=======

1.0.0 - 2018-05-17
------------------
- Add support for Pohoda XML format
- Added much more complex documentation
- Parameter ``Address.zip`` was renamed to ``Address.zip_code``
- Add parameters ``division`` and ``country`` to the  ``Address``
- Added parameter ``Address.bank_code``
  If present, the bank code will be written after dash to
  the account number, otherwise whole
  ``Address.bank_account`` will be used
- Address are rendered to fit the area on the PDF invoice
- Code style fixes
- Fixes for rounding: usage of ``decimal.Decimal`` and
  added parameter ``Invoice.rounding_strategy``
- Fix for QR code
- Allow to set line width in ``SimpleInvoice``


0.5.4 - 2017-03-22
------------------
- Fix locale in build package


0.5.3 - 2017-01-09
------------------
- Use Babel for currency formating; fix and improve tests

0.5.2 - 2014-12-04
------------------
- Stop mentionning python2.6 support
- Make invoice.variable_symbol optional

0.5.1 - 2014-10-28
------------------
- Fix conf relative import
- Use python native function splitlines for notes

0.5.0 - 2014-09-21
------------------
- Add property number to object Invoice
- Replaced variable symbol for invoice number in invoice header
- Update Czech translations

0.4.9 - 2014-07-3
-----------------
- Bug fix previous commit

0.4.8 - 2014-07-3
-----------------
- Create proforma invoice

0.4.7 - 2014-07-1
-----------------
- Change date format for qr code generator
- Disable converting datetime to string on Invoice
- Disable rendering empty values

0.4.6 - 2014-05-14
------------------
- The displayed number of pages only when there is more than one
- Rename Date to  Date of exposure
- Use pillow instead of PIL

0.4.5 - 2014-04-21
------------------

- Support for multipage items printout
- Support for multiline item description
- Use locale to print currency strings and values
- Adding logo to provider header


No notes on earlier releases.
