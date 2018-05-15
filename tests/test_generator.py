# -*- coding: utf-8 -*-
import unittest
from tempfile import NamedTemporaryFile

from InvoiceGenerator.api import Client, Creator, Invoice, Item, Provider
from InvoiceGenerator.generator import Generator
from InvoiceGenerator.pdf import SimpleInvoice


class TestGenerator(unittest.TestCase):

    def test_assertation(self):
        self.assertRaises(AssertionError, Generator, object)
        generator = Generator(self._build_invoice())

        self.assertRaises(AssertionError, generator.gen, '/black/hole', object)

    def test_gen(self):
        tmp_file = NamedTemporaryFile()
        Generator(self._build_invoice()).gen(tmp_file.name, SimpleInvoice)

    def _build_invoice(self):
        invoice = Invoice(Client('John'), Provider('Doe'), Creator('John Doe'))
        invoice.add_item(Item(42, 666))
        return invoice
