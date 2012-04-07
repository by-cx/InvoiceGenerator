# -*- coding: utf-8 -*-
import unittest

from tempfile import NamedTemporaryFile

from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator
from InvoiceGenerator.pdf import SimpleInvoice


class TestBaseInvoice(unittest.TestCase):

    def test_required_args(self):
        self.assertRaises(AssertionError, SimpleInvoice, 'Invoice')
        invoice = Invoice(Client('Kkkk'), Provider('Pupik'), Creator('blah'))

        SimpleInvoice(invoice)

    def test_generate(self):

        invoice = Invoice(Client('Kkkk'), Provider('Pupik'), Creator('blah'))
        invoice.add_item(Item(32, 600))

        tmp_file = NamedTemporaryFile()

        pdf = SimpleInvoice(invoice)
        pdf.gen(tmp_file.name)