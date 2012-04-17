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
        invoice.specific_symbol = 666
        invoice.taxable_date = '1.1.1979'
        invoice.variable_symbol = '000000001'

        tmp_file = NamedTemporaryFile()

        pdf = SimpleInvoice(invoice)
        pdf.gen(tmp_file.name)


    def test_generate_with_vat(self):
        invoice = Invoice(Client('Kkkk'), Provider('Pupik'), Creator('blah'))
        invoice.add_item(Item(32, 600))
        invoice.add_item(Item(60, 50, tax=10))
        invoice.add_item(Item(50, 60, tax=5))
        invoice.add_item(Item(5, 600, tax=50))

        tmp_file = NamedTemporaryFile()

        pdf = SimpleInvoice(invoice)
        pdf.gen(tmp_file.name)