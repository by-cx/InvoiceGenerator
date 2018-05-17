# -*- coding: utf-8 -*-

import decimal
from decimal import Decimal

from InvoiceGenerator.conf import _

import qrcode

__all__ = ['Address', 'Client', 'Provider', 'Creator', 'Item', 'Invoice']


class UnicodeProperty(object):
    _attrs = ()

    def __setattr__(self, key, value):
        if key in self._attrs:
            value = value
        self.__dict__[key] = value


class Address(UnicodeProperty):
    """
    Abstract address definition

    :param summary: address header line - name of addressee or company name
    :param division: division of the organisation (second line of the address)
    :param address: line of the address with street and house number
    :param city: city or part of the city
    :param zip_code: zip code (PSČ in Czech)
    :param phone:
    :param email:
    :param bank_name:
    :param bank_account: bank account number
    :param bank_code:
    :param note: note that will be written on the invoice
    :param vat_id: value added tax identification number (DIČ in czech)
    :param vat_note: VAT note
    :param ir: Taxpayer identification Number (IČO in czech)
    :param logo_filename: path to the image of logo of the company
    :param country: country
    """
    _attrs = ('summary', 'address', 'city', 'zip_code', 'phone', 'email',
              'bank_name', 'bank_account', 'bank_code', 'note', 'vat_id', 'ir',
              'logo_filename', 'vat_note', 'country', 'division')

    def __init__(
        self, summary, address='', city='', zip_code='', phone='', email='',
        bank_name='', bank_account='', bank_code='', note='', vat_id='', ir='',
        logo_filename='', vat_note='', country='', division='',
    ):
        self.summary = summary
        self.address = address
        self.division = division
        self.city = city
        self.country = country
        self.zip_code = zip_code
        self.phone = phone
        self.email = email
        self.bank_name = bank_name
        self.bank_account = bank_account
        self.bank_code = bank_code
        self.note = note
        self.vat_id = vat_id
        self.vat_note = vat_note
        self.ir = ir
        self.logo_filename = logo_filename

    def bank_account_str(self):
        """ Returns bank account identifier with bank code after slash """
        if self.bank_code:
            return "%s/%s" % (self.bank_account, self.bank_code)
        else:
            return self.bank_account

    def _get_address_lines(self):
        address_line = [self.summary]
        if self.division:
            address_line.append(self.division)
        address_line += [
            self.address,
            u' '.join(filter(None, (self.zip_code, self.city))),
            ]
        if self.country:
            address_line.append(self.country)
        if self.vat_id:
            address_line.append(_(u'Vat in: %s') % self.vat_id)

        if self.ir:
            address_line.append(_(u'IR: %s') % self.ir)

        return address_line

    def _get_contact_lines(self):
        return [
            self.phone,
            self.email,
            ]


class Client(Address):
    """
    Definition of client (recipient of the invoice) address.
    """
    pass


class Provider(Address):
    """
    Definition of prvider (subject, that issued the invoice) address.
    """
    pass


class Creator(UnicodeProperty):
    """
    Definition of creator of the invoice (ussually an accountant).

    :param name: name of the issuer
    :param stamp_filename: path to file with stamp (or subscription)
    """
    _attrs = ('name', 'stamp_filename')

    def __init__(self, name, stamp_filename=''):
        self.name = name
        self.stamp_filename = stamp_filename


class Item(object):
    """
    Item on the invoice.

    :param count: number of items or quantity associated with unit
    :param price: price for unit
    :param unit: unit in which it is measured (pieces, Kg, l)
    :param tax: the tax rate under which the item falls (in percent)
    """

    def __init__(self, count, price, description='', unit='', tax=Decimal(0)):
        self.count = count
        self.price = price
        self._description = description
        self.unit = unit
        self.tax = tax

    @property
    def total(self):
        """ Total price for the items without tax. """
        return self.price * self.count

    @property
    def total_tax(self):
        """ Total price for the items with tax. """
        return self.price * self.count * (Decimal(1) + self.tax / Decimal(100))

    def count_tax(self):
        """ Value of only tax that will be payed for the items. """
        return self.total_tax - self.total

    @property
    def description(self):
        """ Short description of the item. """
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def count(self):
        """ Count or amount of the items. """
        return self._count

    @count.setter
    def count(self, value):
        self._count = Decimal(value)

    @property
    def price(self):
        """ Price for unit. """
        return self._price

    @price.setter
    def price(self, value):
        self._price = Decimal(value)

    @property
    def unit(self):
        """ Unit. """
        return self._unit

    @unit.setter
    def unit(self, value):
        self._unit = value

    @property
    def tax(self):
        """ Tax rate. """
        return self._tax

    @tax.setter
    def tax(self, value):
        if value is None:
            self._tax = Decimal(0)
        else:
            self._tax = Decimal(value)


class Invoice(UnicodeProperty):
    """
    Invoice definition

    :param client: client of the invoice
    :type client: Client
    :param creator: creator of the invoice
    :type creator: Creator
    :param provider: provider of the invoice
    :type provider: Provider
    """
    #: title on the invoice
    title = ""
    #: variable symbol associated with the payment
    variable_symbol = None
    #: specific_symbol
    specific_symbol = None
    #: textual description of type of payment
    paytype = None
    #: number or string used as the invoice identifier
    number = None
    #: iban
    iban = None
    #: swift
    swift = None
    #: date of exposure
    date = None
    #: due date
    payback = None
    #:  taxable date
    taxable_date = None
    #: currency_locale: locale according to which will be the written currency representations
    currency_locale = "cs_CZ.UTF-8"
    #: currency identifier (e.g. "$" or "Kč")
    currency = u"Kč"

    use_tax = False

    #: round result to integers?
    rounding_result = False

    #: Result rounding strategy (identifiers from `decimal` module).
    #: Default strategy for rounding in Python is bankers' rounding,
    #: which means that half of the X.5 numbers are rounded down and half up.
    #: Use this parameter to set different rounding strategy.
    rounding_strategy = decimal.ROUND_HALF_EVEN

    def __init__(self, client, provider, creator):
        assert isinstance(client, Client)
        assert isinstance(provider, Provider)
        assert isinstance(creator, Creator)

        self.client = client
        self.provider = provider
        self.creator = creator
        self._items = []

        for attr in self._attrs:
            self.__setattr__(attr, '')

    def _price_tax_unrounded(self):
        return sum(item.total_tax for item in self.items)

    @property
    def price(self):
        """ Total sum price without taxes. """
        return self._round_result(sum(item.total for item in self.items))

    @property
    def price_tax(self):
        """ Total sum price including taxes. """
        return self._round_result(self._price_tax_unrounded())

    def add_item(self, item):
        """
        Add item to the invoice.

        :param item: the new item
        :type item: Item class
        """
        assert isinstance(item, Item)
        self._items.append(item)

    @property
    def items(self):
        """ Items on the invoice. """
        return self._items

    def _round_price(self, price):
        return decimal.Decimal(price).quantize(0, rounding=self.rounding_strategy)

    @property
    def difference_in_rounding(self):
        """ Difference between rounded price and real price. """
        price = self._price_tax_unrounded()
        return Decimal(self._round_price(price)) - price

    def _get_grouped_items_by_tax(self):
        table = {}
        for item in self.items:
            if item.tax not in table:
                table[item.tax] = {'total': item.total, 'total_tax': item.total_tax, 'tax': item.count_tax()}
            else:
                table[item.tax]['total'] += item.total
                table[item.tax]['total_tax'] += item.total_tax
                table[item.tax]['tax'] += item.count_tax()

        return table

    def _round_result(self, price):
        if self.rounding_result:
            return self._round_price(price)
        return price

    def generate_breakdown_vat(self):
        return self._get_grouped_items_by_tax()

    def generate_breakdown_vat_table(self):
        rows = []
        for vat, items in self.generate_breakdown_vat().items():
            rows.append((vat, items['total'], items['total_tax'], items['tax']))

        return rows


class Correction(Invoice):
    """
    Correcting invoice
    """
    _attrs = ('number', 'reason', 'title', 'variable_symbol', 'specific_symbol', 'paytype',
              'date', 'payback', 'taxable_date')

    def __init__(self, client, provider, creator):
        super(Correction, self).__init__(client, provider, creator)


class QrCodeBuilder(object):

    def __init__(self, invoice):
        """
        :param invoice: Invoice
        """
        self.invoice = invoice
        self.qr = self._fill(invoice)
        self.tmp_file = None

    def _fill(self, invoice):
        from qrplatba import QRPlatbaGenerator

        qr_kwargs = {
            'account': invoice.provider.bank_account,
            'amount': invoice.use_tax and invoice.price_tax or invoice.price,
            'x_ss': invoice.specific_symbol,
        }

        if invoice.variable_symbol:
            qr_kwargs['x_vs'] = invoice.variable_symbol

        try:
            qr_kwargs['due_date'] = invoice.payback.strftime("%Y%m%d")
        except AttributeError:
            pass

        qr_kwargs = {k: v for k, v in qr_kwargs.items() if v}

        return QRPlatbaGenerator(**qr_kwargs)

    @property
    def filename(self):
        from tempfile import NamedTemporaryFile
        img = qrcode.make(self.qr.get_text())

        self.tmp_file = NamedTemporaryFile(
            mode='w+b',
            suffix='.png',
            delete=False,
        )
        img.save(self.tmp_file)
        self.tmp_file.close()
        return self.tmp_file.name

    def destroy(self):
        if hasattr(self.tmp_file, 'name'):
            import os
            os.unlink(self.tmp_file.name)
