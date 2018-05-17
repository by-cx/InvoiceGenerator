# -*- coding: utf-8 -*-
import logging
import xml.etree.cElementTree as ET

from builtins import str

from .pdf import BaseInvoice

logger = logging.getLogger(__name__)

__all__ = ['SimpleInvoice']


class SimpleInvoice(BaseInvoice):
    """
    Generator of simple invoice in XML format for Pohoda accounting system

    :param invoice: the invoice
    :type invoice: Invoice
    :param tax_rates: definition of tax rates used in Pohoda, left None for default values
    :type tax_rates: dict
    """

    tax_rates = {
        'high': 21,
        'low': 15,
        'none': 0,
    }
    _dat_ns = "http://www.stormware.cz/schema/version_2/data.xsd"
    _inv_ns = "http://www.stormware.cz/schema/version_2/invoice.xsd"
    _typ_ns = "http://www.stormware.cz/schema/version_2/type.xsd"

    def __init__(self, invoice, tax_rates=None):
        super(SimpleInvoice, self).__init__(invoice)

        if tax_rates:
            self.tax_rates = tax_rates
        self.inv_tax_rates = {v: k for k, v in self.tax_rates.items()}

    def _add_item(self, xml_invoice, item):
        invoice_item = ET.SubElement(xml_invoice, "{%s}invoiceItem" % self._inv_ns)

        ET.SubElement(invoice_item, '{%s}quantity' % self._inv_ns).text = str(item.count)
        ET.SubElement(invoice_item, '{%s}unit' % self._inv_ns).text = str(item.unit)
        home_currency = ET.SubElement(invoice_item, '{%s}homeCurrency' % self._inv_ns)

        ET.SubElement(home_currency, '{%s}unitPrice' % self._typ_ns).text = str(item.price)

        ET.SubElement(invoice_item, '{%s}text' % self._inv_ns).text = str(item.description)[:90]
        if item.tax in self.inv_tax_rates:
            ET.SubElement(invoice_item, '{%s}rateVAT' % self._inv_ns).text = self.inv_tax_rates[item.tax]
        else:
            logger.warning("Tax rate %s is not among the tax rates accepted by Pohoda system" % item.tax)

        return invoice_item

    def _format_address(self, address, to_element):
        address_element = ET.SubElement(to_element, '{%s}address' % self._typ_ns)
        ET.SubElement(address_element, '{%s}company' % self._typ_ns).text = str(address.summary)
        ET.SubElement(address_element, '{%s}street' % self._typ_ns).text = str(address.address)
        ET.SubElement(address_element, '{%s}city' % self._typ_ns).text = str(address.city)
        ET.SubElement(address_element, '{%s}zip' % self._typ_ns).text = str(address.zip_code)
        ET.SubElement(address_element, '{%s}phone' % self._typ_ns).text = str(address.phone)
        ET.SubElement(address_element, '{%s}ico' % self._typ_ns).text = str(address.ir)
        ET.SubElement(address_element, '{%s}dic' % self._typ_ns).text = str(address.vat_id)
        ET.SubElement(address_element, '{%s}email' % self._typ_ns).text = str(address.email)

    def _format_date(self, date):
        if date:
            return date.isoformat()

    def _invoice_header(self, invoice_header):
        ET.SubElement(invoice_header, "{%s}invoiceType" % self._inv_ns).text = "issuedInvoice"
        number = ET.SubElement(invoice_header, "{%s}number" % self._inv_ns)
        ET.SubElement(number, "{%s}numberRequested" % self._typ_ns).text = self.invoice.number

        if self.invoice.date:
            ET.SubElement(invoice_header, "{%s}date" % self._inv_ns).text = str(self._format_date(self.invoice.date))
        if self.invoice.taxable_date:
            ET.SubElement(invoice_header, "{%s}dateTax" % self._inv_ns).text = str(self._format_date(self.invoice.taxable_date))
        if self.invoice.payback:
            ET.SubElement(invoice_header, "{%s}dateDue" % self._inv_ns).text = str(self._format_date(self.invoice.payback))
        ET.SubElement(invoice_header, "{%s}text" % self._inv_ns).text = str(self.invoice.title)
        ET.SubElement(invoice_header, "{%s}symVar" % self._inv_ns).text = str(self.invoice.variable_symbol)
        ET.SubElement(invoice_header, "{%s}symSpec" % self._inv_ns).text = str(self.invoice.specific_symbol)
        payment_account = ET.SubElement(invoice_header, "{%s}paymentAccount" % self._inv_ns)
        ET.SubElement(payment_account, "{%s}accountNo" % self._typ_ns).text = str(self.invoice.provider.bank_account)
        ET.SubElement(payment_account, "{%s}bankCode" % self._typ_ns).text = str(self.invoice.provider.bank_code)

        partner_identity = ET.SubElement(invoice_header, "{%s}partnerIdentity" % self._inv_ns)
        self._format_address(self.invoice.client, partner_identity)

        my_identity = ET.SubElement(invoice_header, "{%s}myIdentity" % self._inv_ns)
        self._format_address(self.invoice.provider, my_identity)

    def _invoice_summary(self, invoice_summary):
        ET.SubElement(invoice_summary, "{%s}roundingDocument" % self._inv_ns).text = "math2one"
        home_currency = ET.SubElement(invoice_summary, "{%s}homeCurrency" % self._inv_ns)
        breakdown = self.invoice.generate_breakdown_vat()
        for rate_ident, rate in self.tax_rates.items():
            if rate in breakdown:
                rate_camel = rate_ident.capitalize()
                ET.SubElement(home_currency, '{%s}price%s' % (self._typ_ns, rate_camel)).text = str(breakdown[rate]['total_tax'])
                if rate_ident != 'none':
                    ET.SubElement(home_currency, '{%s}price%sVAT' % (self._typ_ns, rate_camel)).text = str(breakdown[rate]['tax'])

    def gen(self, filename):
        """
        Generate the invoice into file

        :param filename: file in which the XML invoice will be written
        :type filename: string or File
        """
        ET.register_namespace('dat', self._dat_ns)
        ET.register_namespace('inv', self._inv_ns)
        ET.register_namespace('typ', self._typ_ns)

        data_pack = ET.Element(
            "{%s}dataPack" % self._dat_ns,
            version="2.0",
            id=self.invoice.number,
            ico=self.invoice.provider.ir,
            application="InvoiceGenerator",
            note="Generated from InvoiceGenerator",
        )
        data_pack_item = ET.SubElement(data_pack, "{%s}dataPackItem" % self._dat_ns, version="2.0", id=self.invoice.number)
        xml_invoice = ET.SubElement(data_pack_item, "{%s}invoice" % self._inv_ns, version="2.0")

        invoice_header = ET.SubElement(xml_invoice, "inv:invoiceHeader")
        self._invoice_header(invoice_header)

        invoice_detail = ET.SubElement(xml_invoice, "{%s}invoiceDetail" % self._inv_ns)
        for item in self.invoice.items:
            self._add_item(invoice_detail, item)

        invoice_summary = ET.SubElement(xml_invoice, "{%s}invoiceSummary" % self._inv_ns)
        self._invoice_summary(invoice_summary)

        tree = ET.ElementTree(data_pack)
        tree.write(filename, encoding="UTF-8", xml_declaration=True)
