# -*- coding: utf-8 -*-
import unittest

from tempfile import NamedTemporaryFile

from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator
from InvoiceGenerator.pdf import SimpleInvoice, CorrectingInvoice


class TestBaseInvoice(unittest.TestCase):

    def test_required_args(self):
        self.assertRaises(AssertionError, SimpleInvoice, 'Invoice')
        invoice = Invoice(Client('Kkkk'), Provider('Pupik'), Creator('blah'))

        SimpleInvoice(invoice)

    def test_generate(self):
        provider = Provider('Pupik')
        provider.address = 'Kubelikova blah blah blah'
        provider.zip = '12655465'
        provider.city = 'Frantisek'
        provider.vat_id = 'CZ8590875682'
        provider.ir = '785684523'
        provider.email = 'mail@email.com'
        provider.bank_account = '2600420569/2010'
        provider.bank_name = 'RB'
        provider.note = u'zapsaná v obchodním rejstříku vedeném městským soudem v Praze,\noddíl C, vložka 176551'

        client = Client('Kkkk')
        client.summary = 'Bla blah blah'
        client.address = 'Kubelikova blah blah blah'
        client.zip = '12655465'
        client.city = 'Frantisek'
        client.vat_id = 'CZ8590875682'
        client.ir = '785684523'
        client.phone = '785684523'
        client.email = 'mail@email.com'
        client.note = u'zapsaná v obchodním rejstříku vedeném městským soudem v Praze,\noddíl C, vložka 176551'

        invoice = Invoice(client, provider, Creator('blah'))
        invoice.title = u"Testovací faktura"
        invoice.add_item(Item(32, 600.6, description=u"Krátký popis", tax=50))
        invoice.add_item(Item(32, 2.5, tax=20))
        invoice.add_item(Item(5, 25.42, description=u"Dlouhý popis blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah", tax=20))
        for i in range(1,26):
            invoice.add_item(Item(5, 25.42, description=u"Popis", tax=0))
        invoice.specific_symbol = 666
        invoice.taxable_date = '1.1.1979'
        invoice.variable_symbol = '000000001'
        invoice.currency = u'Kč'
        invoice.rounding_result = True


        tmp_file = NamedTemporaryFile(delete=False)
        pdf = SimpleInvoice(invoice)
        pdf.gen(tmp_file.name, True)

        invoice.number = 1
        invoice.reason = u"Položka navíc"
        tmp_file1 = NamedTemporaryFile(delete=False)
        pdf = CorrectingInvoice(invoice)
        pdf.gen(tmp_file1.name)


    def test_generate_with_vat(self):
        invoice = Invoice(Client('Kkkk'), Provider('Pupik'), Creator('blah'))
        invoice.add_item(Item(32, 600))
        invoice.add_item(Item(60, 50, tax=10))
        invoice.add_item(Item(50, 60, tax=5))
        invoice.add_item(Item(5, 600, tax=50))

        tmp_file = NamedTemporaryFile()

        pdf = SimpleInvoice(invoice)
        pdf.gen(tmp_file.name)
