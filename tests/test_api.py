# -*- coding: utf-8 -*-
import decimal
import unittest
import uuid
from decimal import Decimal

from InvoiceGenerator.api import Address, Client, Creator, Invoice, \
    Item, Provider

from six import string_types


class AddressTest(unittest.TestCase):

    attrs = ('summary', 'address', 'city', 'zip_code', 'phone', 'email',
             'bank_name', 'bank_account', 'note', 'vat_id', 'ir')

    addresss_object = Address

    def test_required_args(self):
        self.assertRaises(TypeError, self.addresss_object)

    def test_check_data_types(self):
        address = self.addresss_object(
            **{key: str(uuid.uuid4()) for key in self.attrs}
        )
        for key in self.attrs:
            value = address.__getattribute__(key)
            self.assertIsInstance(value, string_types, msg="Attribute %s with type %s is not string type." % (key, type(value)))

    def test_get_address_lines(self):
        summary = 'Py s.r.o.'
        address = 'Prague street'
        zip_code = '1344234234'
        city = 'Prague'

        address_object = self.addresss_object(summary, address, city, zip_code)

        expected = [summary, address, u'%s %s' % (zip_code, city)]
        self.assertEquals(expected, address_object._get_address_lines())

    def test_get_contact_lines(self):
        phone = '56846846'
        email = 'mail@mail.com'

        address = self.addresss_object('Foo s.r.o.', phone=phone, email=email)

        expected = [phone, email]
        self.assertEquals(expected, address._get_contact_lines())


class ClientTest(AddressTest):
    addresss_object = Client


class ProviderTest(AddressTest):
    addresss_object = Provider


class CreatorTest(unittest.TestCase):

    def test_required_args(self):
        self.assertRaises(TypeError, Creator)

    def test_check_data_types(self):
        creator = Creator('John Doe', '/black/hole')

        self.assertIsInstance(creator.name, string_types)
        self.assertIsInstance(creator.stamp_filename, string_types)


class ItemTest(unittest.TestCase):

    def test_required_args(self):
        self.assertRaises(TypeError, Item)
        self.assertRaises(TypeError, Item, 42)

    def test_check_data_types_set_in_constructor(self):
        item = Item('42', '666', 'Item description', 'hour', '1.1')

        self.assertIsInstance(item.count, Decimal)
        self.assertEqual(item.count, 42)
        self.assertIsInstance(item.price, Decimal)
        self.assertEqual(item.price, 666)
        self.assertIsInstance(item.description, string_types)
        self.assertIsInstance(item.unit, string_types)
        self.assertIsInstance(item.tax, Decimal)
        self.assertEqual(item.tax, Decimal('1.1'))

    def test_getters_and_setters(self):
        item = Item(24, 666)

        item.count = '44'
        item.price = '667'
        item.description = 'Foo bar'
        item.unit = 'hour'
        item.tax = '99.9'

        self.assertIsInstance(item.count, Decimal)
        self.assertEqual(item.count, 44)
        self.assertIsInstance(item.price, Decimal)
        self.assertEqual(item.price, 667)
        self.assertIsInstance(item.description, string_types)
        self.assertIsInstance(item.unit, string_types)
        self.assertIsInstance(item.tax, Decimal)
        self.assertEqual(item.tax, Decimal('99.9'))

    def test_count_total(self):
        item = Item(42, 666, tax=21)
        self.assertEquals(27972, item.total)
        self.assertEquals(Decimal('33846.12'), item.total_tax)

    def test_count_total_strings(self):
        item = Item('42', '666', tax='21')
        self.assertEquals(27972, item.total)
        self.assertEquals(Decimal('33846.12'), item.total_tax)

    def test_count_total_decimal(self):
        item = Item(Decimal(42), Decimal(666), tax=Decimal(21))
        self.assertEquals(27972, item.total)
        self.assertEquals(Decimal('33846.12'), item.total_tax)

    def test_count_total_float(self):
        item = Item(42.0, 666.0, tax=21.0)
        self.assertEquals(27972, item.total)
        self.assertEquals(Decimal('33846.12'), item.total_tax)

    def test_count_tax(self):

        item = Item(2, 50, tax=50)
        self.assertEqual(50, item.count_tax())

        item = Item(2, 50)
        self.assertEqual(0, item.count_tax())

    def test_count_total_with_tax(self):
        count = 24
        price = 42
        tax = '99.9'
        item = Item(count, price, tax=tax)
        self.assertEquals(Decimal('2014.992'), item.total_tax)

    def test_count_total_with_none_tax(self):
        count = 24
        price = 42
        tax = None
        item = Item(count, price, tax=tax)
        self.assertIsInstance(item.tax, Decimal)
        self.assertEquals(1008, item.total_tax)

    def test_count_total_with_zero_tax(self):
        item = Item(24, 42, tax=0)
        self.assertIsInstance(item.tax, Decimal)
        self.assertEquals(1008, item.total_tax)


class InvoiceTest(unittest.TestCase):

    def test_check_required_args(self):
        self.assertRaises(TypeError, Invoice)
        self.assertRaises(TypeError, Invoice, (), ())

        sample_data = (
            {'client': '', 'provider': '', 'creator': ''},
            {'client': Client('foo'), 'provider': '', 'creator': ''},
            {'client': Client('foo'), 'provider': Provider('bar'), 'creator': ''},

        )
        for args in sample_data:
            self.assertRaises(AssertionError, Invoice, **args)

    def test_check_attrs(self):
        attrs = ('title', 'variable_symbol', 'specific_symbol', 'paytype',
                 'currency', 'date', 'payback', 'taxable_date')

        invoice = Invoice(Client('Foo'), Provider('Bar'), Creator('Blah'))

        for attr in attrs:
            self.assertTrue(hasattr(invoice, attr))

    def test_add_item(self):
        invoice = Invoice(Client('Foo'), Provider('Bar'), Creator('Blah'))

        self.assertRaises(AssertionError, invoice.add_item, '')

        for item in [Item(1, 500), Item(2, 500), Item(3, 500)]:
            invoice.add_item(item)

        self.assertEquals(3, len(invoice.items))

    def test_price(self):
        invoice = Invoice(Client('Foo'), Provider('Bar'), Creator('Blah'))
        items = [Item(1, 500), Item(2, 500), Item(3, 500)]
        for item in items:
            invoice.add_item(item)

        self.assertEqual(3000, invoice.price)

    def test_price_tax(self):
        invoice = Invoice(Client('Foo'), Provider('Bar'), Creator('Blah'))
        items = [
            Item(1, 500, tax='99.9'),
            Item(2, 500, tax='99.9'),
            Item(3, 500, tax='99.9'),
        ]
        for item in items:
            invoice.add_item(item)

        self.assertEqual(5997, invoice.price_tax)

    def test_generate_breakdown_vat(self):
        invoice = Invoice(Client('Foo'), Provider('Bar'), Creator('Blah'))
        invoice.add_item(Item(1, 500, tax=50))
        invoice.add_item(Item(3, 500, tax=50))
        invoice.add_item(Item(500, 5, tax=0))
        invoice.add_item(Item(5, 500, tax=0))

        expected = {
            0.0: {'total': 5000.0, 'total_tax': 5000.0, 'tax': 0.0},
            50.0: {'total': 2000.0, 'total_tax': 3000.0, 'tax': 1000},
        }

        self.assertEquals(expected, invoice.generate_breakdown_vat())

    def test_generate_breakdown_vat_table(self):
        invoice = Invoice(Client('Foo'), Provider('Bar'), Creator('Blah'))
        invoice.add_item(Item(1, 500, tax=50))
        invoice.add_item(Item(3, 500, tax=50))
        invoice.add_item(Item(500, 5, tax=0))
        invoice.add_item(Item(5, 500, tax=0))

        expected = [(0.00, 5000.0, 5000.0, 0), (50.0, 2000.0, 3000.0, 1000.0)]

        self.assertEquals(expected, invoice.generate_breakdown_vat_table())

    def test_difference_rounding(self):
        invoice = Invoice(Client('Foo'), Provider('Bar'), Creator('Blah'))
        invoice.add_item(Item(1, 2.5, tax=50))

        self.assertEquals(0.25, invoice.difference_in_rounding)

    def test_price_tax_rounding(self):
        """
        Test, that the price that sums up to 1756.5 gets rounded according to rounding strategy.
        """
        invoice = Invoice(Client('Foo'), Provider('Bar'), Creator('Blah'))
        invoice.add_item(Item(5, 290, tax=21))
        invoice.rounding_result = True
        invoice.use_tax = True
        self.assertEqual(1754, invoice.price_tax)
        invoice.rounding_strategy = decimal.ROUND_HALF_UP
        self.assertEqual(1755, invoice.price_tax)
