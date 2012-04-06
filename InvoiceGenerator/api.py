# -*- coding: utf-8 -*-

__all__ = ['Address', 'Client', 'Provider', 'Creator', 'Item', 'Invoice']

class Address:
    summary = ''
    address = ''
    city = ''
    zip = ''
    phone = ''
    email = ''
    bank_name = ''
    bank_account = ''
    note = ''

    def get_address_lines(self):
        return [
            self.summary,
            self.address,
            '%s %s' % (self.zip, self.city),
            ]

    def get_contact_lines(self):
        return [
            self.phone,
            self.email,
            ]

class Client(Address):
    pass

class Provider(Address):
    pass


class Creator(object):
    name = ''
    stamp_filename = ''

    def __unicode__(self):
        return u'%s'.strip() % self.name

class Item:
    description = ''
    count = 0
    price = 0.0
    unit = ''
    tax = 0.0

    @property
    def total(self):
        return self.price * self.count

    @property
    def total_tax(self):
        return self.price * self.count * (1.0 + self.tax / 100.0)


class Invoice(object):
    items = []
    title = ''
    variable_symbol = '00000000'
    creator = None
    paytype = ''

    currency = 'czk'
    vat_number = 0.0

    date = ''
    payback = ''

    def __init__(self, client, provider, creator):
        assert isinstance(client, Client)
        assert isinstance(provider, Provider)
        assert isinstance(creator, Creator)

        self.client = client
        self.provider = provider
        self.creator = creator

    @property
    def price(self):
        return sum([item.total for item in self.items])

    @property
    def price_tax(self):
        return sum([item.total_tax for item in self.items])
