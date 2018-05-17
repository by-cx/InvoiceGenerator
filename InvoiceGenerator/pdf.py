# -*- coding: utf-8 -*-
import errno
import locale
import os
import warnings

from InvoiceGenerator.api import Invoice, QrCodeBuilder
from InvoiceGenerator.conf import FONT_BOLD_PATH, FONT_PATH
from InvoiceGenerator.conf import LANGUAGE, get_gettext

from PIL import Image

from babel.dates import format_date
from babel.numbers import format_currency

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame, KeepInFrame, Paragraph


__all__ = ['SimpleInvoice', 'ProformaInvoice', 'CorrectingInvoice']


def get_lang():
    return os.environ.get("INVOICE_LANG", LANGUAGE)


def _(*args, **kwargs):
    lang = get_lang()
    try:
        gettext = get_gettext(lang)
    except ImportError:
        def gettext(x): x
    except OSError as e:
        if e.errno == errno.ENOENT:
            def gettext(x): x
        else:
            raise
    return gettext(*args, **kwargs)


class BaseInvoice(object):

    def __init__(self, invoice):
        assert isinstance(invoice, Invoice), "invoice is not instance of Invoice"

        self.invoice = invoice

    def gen(self, filename):
        """
        Generate the invoice into file

        :param filename: file in which the invoice will be written
        :type filename: string or File
        """
        pass


class NumberedCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if num_pages > 1:
                self.draw_page_number(num_pages)
            Canvas.showPage(self)
        Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("DejaVu", 7)
        self.drawRightString(
            200*mm,
            20*mm,
            _("Page %(page_number)d of %(page_count)d") % {"page_number": self._pageNumber, "page_count": page_count},
        )


def prepare_invoice_draw(self):
    self.TOP = 260
    self.LEFT = 20

    pdfmetrics.registerFont(TTFont('DejaVu', FONT_PATH))
    pdfmetrics.registerFont(TTFont('DejaVu-Bold', FONT_BOLD_PATH))

    self.pdf = NumberedCanvas(self.filename, pagesize=letter)
    self._addMetaInformation(self.pdf)

    self.pdf.setFont('DejaVu', 15)
    self.pdf.setStrokeColorRGB(0, 0, 0)

    if self.invoice.currency:
        warnings.warn("currency attribute is deprecated, use currency_locale instead", DeprecationWarning)


def currency(amount, unit, locale):
    currency_string = format_currency(amount, unit, locale=locale)
    if locale == 'cs_CZ.UTF-8':
        currency_string = currency_string.replace(u",00", u",-")
    return currency_string


class SimpleInvoice(BaseInvoice):
    """
    Generator of simple invoice in PDF format

    :param invoice: the invoice
    :type invoice: Invoice
    """
    line_width = 62

    def gen(self, filename, generate_qr_code=False):
        """
        Generate the invoice into file

        :param filename: file in which the PDF simple invoice will be written
        :type filename: string or File
        :param generate_qr_code: should be QR code included in the PDF?
        :type generate_qr_code: boolean
        """
        self.filename = filename
        if generate_qr_code:
            qr_builder = QrCodeBuilder(self.invoice)
        else:
            qr_builder = None

        self.qr_builder = qr_builder

        prepare_invoice_draw(self)

        # Texty
        self._drawMain()
        self._drawTitle()
        self._drawProvider(self.TOP - 10, self.LEFT + 3)
        self._drawClient(self.TOP - 39, self.LEFT + 91)
        self._drawPayment(self.TOP - 47, self.LEFT + 3)
        self._drawQR(self.TOP - 39.4, self.LEFT + 61, 75.0)
        self._drawDates(self.TOP - 10, self.LEFT + 91)
        self._drawItems(self.TOP - 80, self.LEFT)

        # self.pdf.setFillColorRGB(0, 0, 0)

        self.pdf.showPage()
        self.pdf.save()
        if self.qr_builder:
            self.qr_builder.destroy()

    #############################################################
    # Draw methods
    #############################################################

    def _addMetaInformation(self, pdf):
        pdf.setCreator(self.invoice.provider.summary)
        pdf.setTitle(self.invoice.title)
        pdf.setAuthor(self.invoice.creator.name)

    def _drawTitle(self):
        # Up line
        self.pdf.drawString(self.LEFT*mm, self.TOP*mm, self.invoice.title)
        if not self.invoice.use_tax:
            self.pdf.drawString(
                (self.LEFT + 90) * mm,
                self.TOP*mm,
                _(u'Invoice num.: %s') % self.invoice.number,
            )
        else:
            self.pdf.drawString(
                (self.LEFT + 90) * mm,
                self.TOP*mm,
                _(u'Taxable invoice num.: %s') % self.invoice.number,
            )

    def _drawMain(self):
        # Borders
        self.pdf.rect(
            self.LEFT * mm,
            (self.TOP - 68) * mm,
            (self.LEFT + 156) * mm,
            65 * mm,
            stroke=True,
            fill=False,
        )

        path = self.pdf.beginPath()
        path.moveTo((self.LEFT + 88) * mm, (self.TOP - 3) * mm)
        path.lineTo((self.LEFT + 88) * mm, (self.TOP - 68) * mm)
        self.pdf.drawPath(path, True, True)

        path = self.pdf.beginPath()
        path.moveTo(self.LEFT * mm, (self.TOP - 39) * mm)
        path.lineTo((self.LEFT + 88) * mm, (self.TOP - 39) * mm)
        self.pdf.drawPath(path, True, True)

        path = self.pdf.beginPath()
        path.moveTo((self.LEFT + 88) * mm, (self.TOP - 27) * mm)
        path.lineTo((self.LEFT + 176) * mm, (self.TOP - 27) * mm)
        self.pdf.drawPath(path, True, True)

    def _drawAddress(self, top, left, width, height, header_string, address):
        self.pdf.setFont('DejaVu', 8)
        text = self.pdf.beginText((left + 40) * mm, (top - 6) * mm)
        text.textLines(address._get_contact_lines())
        self.pdf.drawText(text)

        frame = Frame((left - 3) * mm, (top - 29) * mm, width*mm, height*mm)
        header = ParagraphStyle('header', fontName='DejaVu', fontSize=12, leading=15)
        default = ParagraphStyle('default', fontName='DejaVu', fontSize=8, leading=8.5)
        small = ParagraphStyle('small', parent=default, fontSize=6, leading=6)
        story = [
            Paragraph(header_string, header),
            Paragraph("<br/>".join(address._get_address_lines()), default),
            Paragraph("<br/>".join(address.note.splitlines()), small),
        ]
        story_inframe = KeepInFrame(width*mm, height*mm, story)
        frame.addFromList([story_inframe], self.pdf)

        if address.logo_filename:
            im = Image.open(address.logo_filename)
            height = 30.0
            width = float(im.size[0]) / (float(im.size[1])/height)
            self.pdf.drawImage(self.invoice.provider.logo_filename, (left + 84) * mm - width, (top - 4) * mm, width, height)

    def _drawClient(self, TOP, LEFT):
        self._drawAddress(TOP, LEFT, 88, 41, _(u'Customer'), self.invoice.client)

    def _drawProvider(self, TOP, LEFT):
        self._drawAddress(TOP, LEFT, 88, 36, _(u'Provider'), self.invoice.provider)

    def _drawPayment(self, TOP, LEFT):
        self.pdf.setFont('DejaVu-Bold', 8)
        self.pdf.drawString(LEFT * mm, (TOP + 2) * mm, _(u'Payment information'))

        text = self.pdf.beginText((LEFT) * mm, (TOP - 2) * mm)
        lines = [
            self.invoice.provider.bank_name,
            '%s: %s' % (_(u'Account n.'), self.invoice.provider.bank_account_str()),
        ]
        if self.invoice.variable_symbol:
            lines.append(
                '%s: %s' % (_(u'Variable symbol'), self.invoice.variable_symbol),
            )
        if self.invoice.specific_symbol:
            lines.append(
                '%s: %s' % (_(u'Specific symbol'), self.invoice.specific_symbol),
            )
        if self.invoice.iban:
            lines.append(
                '%s: %s' % (_(u'IBAN'), self.invoice.iban),
            )
        if self.invoice.swift:
            lines.append(
                '%s: %s' % (_(u'SWIFT'), self.invoice.swift),
            )
        text.textLines(lines)
        self.pdf.drawText(text)

    def _drawItemsHeader(self,  TOP,  LEFT):
        path = self.pdf.beginPath()
        path.moveTo(LEFT * mm, (TOP - 4) * mm)
        path.lineTo((LEFT + 176) * mm, (TOP - 4) * mm)
        self.pdf.drawPath(path, True, True)

        self.pdf.setFont('DejaVu-Bold', 7)
        self.pdf.drawString((LEFT + 1) * mm, (TOP - 2) * mm, _(u'List of items'))

        self.pdf.drawString((LEFT + 1) * mm, (TOP - 9) * mm, _(u'Description'))
        items_are_with_tax = self.invoice.use_tax
        if items_are_with_tax:
            i = 9
            self.pdf.drawString((LEFT + 73) * mm, (TOP - i) * mm, _(u'Units'))
            self.pdf.drawString(
                (LEFT + 88) * mm,
                (TOP - i) * mm,
                _(u'Price per one'),
            )
            self.pdf.drawString(
                (LEFT + 115) * mm,
                (TOP - i) * mm,
                _(u'Total price'),
            )
            self.pdf.drawString(
                (LEFT + 137) * mm,
                (TOP - i) * mm,
                _(u'Tax'),
            )
            self.pdf.drawString(
                (LEFT + 146) * mm,
                (TOP - i) * mm,
                _(u'Total price with tax'),
            )
            i += 5
        else:
            i = 9
            self.pdf.drawString(
                (LEFT + 104) * mm,
                (TOP - i) * mm,
                _(u'Units'),
            )
            self.pdf.drawString(
                (LEFT + 123) * mm,
                (TOP - i) * mm,
                _(u'Price per one'),
            )
            self.pdf.drawString(
                (LEFT + 150) * mm,
                (TOP - i) * mm,
                _(u'Total price'),
            )
            i += 5
        return i

    def _drawItems(self, TOP, LEFT):  # noqa
        # Items
        i = self._drawItemsHeader(TOP, LEFT)
        self.pdf.setFont('DejaVu', 7)

        items_are_with_tax = self.invoice.use_tax

        # List
        will_wrap = False
        for item in self.invoice.items:
            if TOP - i < 30 * mm:
                will_wrap = True

            style = ParagraphStyle('normal', fontName='DejaVu', fontSize=7)
            p = Paragraph(item.description, style)
            pwidth, pheight = p.wrapOn(self.pdf, 70*mm if items_are_with_tax else 90*mm, 30*mm)
            i_add = max(float(pheight)/mm, 4.23)

            if will_wrap and TOP - i - i_add < 8 * mm:
                will_wrap = False
                self.pdf.rect(LEFT * mm, (TOP - i) * mm, (LEFT + 156) * mm, (i + 2) * mm, stroke=True, fill=False)  # 140,142
                self.pdf.showPage()

                i = self._drawItemsHeader(self.TOP, LEFT)
                TOP = self.TOP
                self.pdf.setFont('DejaVu', 7)

            # leading line
            path = self.pdf.beginPath()
            path.moveTo(LEFT * mm, (TOP - i + 3.5) * mm)
            path.lineTo((LEFT + 176) * mm, (TOP - i + 3.5) * mm)
            self.pdf.setLineWidth(0.1)
            self.pdf.drawPath(path, True, True)
            self.pdf.setLineWidth(1)

            i += i_add
            p.drawOn(self.pdf, (LEFT + 1) * mm, (TOP - i + 3) * mm)
            i -= 4.23
            if items_are_with_tax:
                if float(int(item.count)) == item.count:
                    self.pdf.drawRightString((LEFT + 85) * mm, (TOP - i) * mm, u'%s %s' % (locale.format("%i", item.count, grouping=True), item.unit))
                else:
                    self.pdf.drawRightString((LEFT + 85) * mm, (TOP - i) * mm, u'%s %s' % (locale.format("%.2f", item.count, grouping=True), item.unit))
                self.pdf.drawRightString((LEFT + 110) * mm, (TOP - i) * mm, currency(item.price, self.invoice.currency, self.invoice.currency_locale))
                self.pdf.drawRightString((LEFT + 134) * mm, (TOP - i) * mm, currency(item.total, self.invoice.currency, self.invoice.currency_locale))
                self.pdf.drawRightString((LEFT + 144) * mm, (TOP - i) * mm, '%.0f %%' % item.tax)
                self.pdf.drawRightString((LEFT + 173) * mm, (TOP - i) * mm, currency(item.total_tax, self.invoice.currency, self.invoice.currency_locale))
                i += 5
            else:
                if float(int(item.count)) == item.count:
                    self.pdf.drawRightString((LEFT + 118) * mm, (TOP - i) * mm, u'%s %s' % (locale.format("%i", item.count, grouping=True), item.unit))
                else:
                    self.pdf.drawRightString((LEFT + 118) * mm, (TOP - i) * mm, u'%s %s' % (locale.format("%.2f", item.count, grouping=True), item.unit))
                self.pdf.drawRightString((LEFT + 148) * mm, (TOP - i) * mm, currency(item.price, self.invoice.currency, self.invoice.currency_locale))
                self.pdf.drawRightString((LEFT + 173) * mm, (TOP - i) * mm, currency(item.total, self.invoice.currency, self.invoice.currency_locale))
                i += 5

        if will_wrap:
            self.pdf.rect(LEFT * mm, (TOP - i) * mm, (LEFT + 156) * mm, (i + 2) * mm, stroke=True, fill=False)  # 140,142
            self.pdf.showPage()

            i = 0
            TOP = self.TOP
            self.pdf.setFont('DejaVu', 7)

        if self.invoice.rounding_result:
            path = self.pdf.beginPath()
            path.moveTo(LEFT * mm, (TOP - i) * mm)
            path.lineTo((LEFT + 176) * mm, (TOP - i) * mm)
            i += 5
            self.pdf.drawPath(path, True, True)
            self.pdf.drawString((LEFT + 1) * mm, (TOP - i) * mm, _(u'Rounding'))
            self.pdf.drawString((LEFT + 68) * mm, (TOP - i) * mm, currency(self.invoice.difference_in_rounding, self.invoice.currency, self.invoice.currency_locale))
            i += 3

        path = self.pdf.beginPath()
        path.moveTo(LEFT * mm, (TOP - i) * mm)
        path.lineTo((LEFT + 176) * mm, (TOP - i) * mm)
        self.pdf.drawPath(path, True, True)

        if not items_are_with_tax:
            self.pdf.setFont('DejaVu-Bold', 11)
            self.pdf.drawString((LEFT + 100) * mm, (TOP - i - 7) * mm, '%s: %s' % (_(u'Total'), currency(self.invoice.price, self.invoice.currency, self.invoice.currency_locale)))
        else:
            self.pdf.setFont('DejaVu-Bold', 6)
            self.pdf.drawString((LEFT + 1) * mm, (TOP - i - 2) * mm, _(u'Breakdown VAT'))
            vat_list, tax_list, total_list, total_tax_list = [_(u'VAT rate')], [_(u'Tax')], [_(u'Without VAT')], [_(u'With VAT')]
            for vat, items in self.invoice.generate_breakdown_vat().items():
                vat_list.append("%s%%" % locale.format('%.2f', vat))
                tax_list.append(currency(items['tax'], self.invoice.currency, self.invoice.currency_locale))
                total_list.append(currency(items['total'], self.invoice.currency, self.invoice.currency_locale))
                total_tax_list.append(currency(items['total_tax'], self.invoice.currency, self.invoice.currency_locale))

            self.pdf.setFont('DejaVu', 6)
            text = self.pdf.beginText((LEFT + 1) * mm, (TOP - i - 5) * mm)
            text.textLines(vat_list)
            self.pdf.drawText(text)

            text = self.pdf.beginText((LEFT + 11) * mm, (TOP - i - 5) * mm)
            text.textLines(tax_list)
            self.pdf.drawText(text)

            text = self.pdf.beginText((LEFT + 27) * mm, (TOP - i - 5) * mm)
            text.textLines(total_list)
            self.pdf.drawText(text)

            text = self.pdf.beginText((LEFT + 45) * mm, (TOP - i - 5) * mm)
            text.textLines(total_tax_list)
            self.pdf.drawText(text)

            # VAT note
            if self.invoice.client.vat_note:
                text = self.pdf.beginText((LEFT + 1) * mm, (TOP - i - 11) * mm)
                text.textLines([self.invoice.client.vat_note])
                self.pdf.drawText(text)

            self.pdf.setFont('DejaVu-Bold', 11)
            self.pdf.drawString(
                (LEFT + 100) * mm,
                (TOP - i - 14) * mm,
                u'%s: %s' % (_(u'Total with tax'), currency(self.invoice.price_tax, self.invoice.currency, self.invoice.currency_locale)),
            )

        if items_are_with_tax:
            self.pdf.rect(LEFT * mm, (TOP - i - 17) * mm, (LEFT + 156) * mm, (i + 19) * mm, stroke=True, fill=False)  # 140,142
        else:
            self.pdf.rect(LEFT * mm, (TOP - i - 11) * mm, (LEFT + 156) * mm, (i + 13) * mm, stroke=True, fill=False)  # 140,142

        self._drawCreator(TOP - i - 20, self.LEFT + 98)

    def _drawCreator(self, TOP, LEFT):
        height = 20*mm
        if self.invoice.creator.stamp_filename:
            im = Image.open(self.invoice.creator.stamp_filename)
            height = float(im.size[1]) / (float(im.size[0])/200.0)
            self.pdf.drawImage(self.invoice.creator.stamp_filename, (LEFT) * mm, (TOP - 2) * mm - height, 200, height)

        path = self.pdf.beginPath()
        path.moveTo((LEFT + 8) * mm, (TOP) * mm - height)
        path.lineTo((LEFT + self.line_width) * mm, (TOP) * mm - height)
        self.pdf.drawPath(path, True, True)

        self.pdf.drawString((LEFT + 10) * mm, (TOP - 5) * mm - height, '%s: %s' % (_(u'Creator'), self.invoice.creator.name))

    def _drawQR(self, TOP, LEFT, size=130.0):
        if self.qr_builder:
            qr_filename = self.qr_builder.filename
            im = Image.open(qr_filename)
            height = float(im.size[1]) / (float(im.size[0]) / size)
            self.pdf.drawImage(
                qr_filename,
                LEFT * mm,
                TOP * mm - height,
                size,
                height,
            )

    def _drawDates(self, TOP, LEFT):
        self.pdf.setFont('DejaVu', 10)
        top = TOP + 1
        items = []
        lang = get_lang()
        if self.invoice.date and self.invoice.use_tax:
            items.append((LEFT * mm, '%s: %s' % (_(u'Date of exposure taxable invoice'), format_date(self.invoice.date, locale=lang))))
        elif self.invoice.date and not self.invoice.use_tax:
            items.append((LEFT * mm, '%s: %s' % (_(u'Date of exposure'), format_date(self.invoice.date, locale=lang))))
        if self.invoice.payback:
            items.append((LEFT * mm, '%s: %s' % (_(u'Due date'), format_date(self.invoice.payback, locale=lang))))
        if self.invoice.taxable_date:
            items.append((LEFT * mm, '%s: %s' % (_(u'Taxable date'), format_date(self.invoice.taxable_date, locale=lang))))

        if self.invoice.paytype:
            items.append((LEFT * mm, '%s: %s' % (_(u'Paytype'), self.invoice.paytype)))

        for item in items:
            self.pdf.drawString(item[0], top * mm, item[1])
            top += -5


class CorrectingInvoice(SimpleInvoice):
    def gen(self, filename):
        """
        Generate the invoice into file

        :param filename: file in which the PDF correcting invoice will be written
        :type filename: string or File
        """
        self.filename = filename
        prepare_invoice_draw(self)

        # Texty
        self._drawMain()
        self._drawTitle()
        self._drawProvider(self.TOP - 10, self.LEFT + 3)
        self._drawClient(self.TOP - 39, self.LEFT + 91)
        self._drawPayment(self.TOP - 47, self.LEFT + 3)
        self.drawCorretion(self.TOP - 73, self.LEFT)
        self._drawDates(self.TOP - 10, self.LEFT + 91)
        self._drawItems(self.TOP - 82, self.LEFT)

        # self.pdf.setFillColorRGB(0, 0, 0)

        self.pdf.showPage()
        self.pdf.save()

    def _drawTitle(self):
        # Up line
        self.pdf.drawString(self.LEFT*mm, self.TOP*mm, self.invoice.title)
        self.pdf.drawString(
            (self.LEFT + 90) * mm,
            self.TOP*mm,
            _(u'Correcting document: %s') % self.invoice.number,
        )

    def drawCorretion(self, TOP, LEFT):
        self.pdf.setFont('DejaVu', 8)
        self.pdf.drawString(LEFT * mm, TOP * mm, _(u'Correction document for invoice: %s') % self.invoice.number)
        self.pdf.drawString(LEFT * mm, (TOP - 4) * mm, _(u'Reason to correction: %s') % self.invoice.reason)


class ProformaInvoice(SimpleInvoice):

    def _drawCreator(self, TOP, LEFT):
        return

    def _drawTitle(self):
        # Up line
        self.pdf.drawString(self.LEFT*mm, self.TOP*mm, self.invoice.title)
        self.pdf.drawString(
            (self.LEFT + 90) * mm,
            self.TOP*mm,
            _(u'Document num.: %s') % self.invoice.number,
        )

    def _drawDates(self, TOP, LEFT):
        self.pdf.setFont('DejaVu', 10)
        top = TOP + 1
        items = []
        if self.invoice.date:
            items.append((LEFT * mm, '%s: %s' % (_(u'Date of exposure'), self.invoice.date)))
        if self.invoice.payback:
            items.append((LEFT * mm, '%s: %s' % (_(u'Payback'), self.invoice.payback)))

        if self.invoice.paytype:
            items.append((LEFT * mm, '%s: %s' % (_(u'Paytype'),
                                                 self.invoice.paytype)))

        for item in items:
            self.pdf.drawString(item[0], top * mm, item[1])
            top += -5
