# -*- coding: utf-8 -*-
from PIL import Image

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus.tables import Table, TableStyle

from conf import _, FONT_PATH, FONT_BOLD_PATH
from api import Invoice

class BaseInvoice(object):

    def __init__(self, invoice):
        assert isinstance(invoice, Invoice)

        self.invoice = invoice

    def gen(self, filename):
        pass


class SimpleInvoice(BaseInvoice):

    def gen(self, filename):
        self.TOP = 260
        self.LEFT = 20
        self.filename = filename

        pdfmetrics.registerFont(TTFont('DejaVu', FONT_PATH))
        pdfmetrics.registerFont(TTFont('DejaVu-Bold', FONT_BOLD_PATH))

        self.pdf = Canvas(self.filename, pagesize = letter)
        self.addMetaInformation(self.pdf)

        self.pdf.setFont('DejaVu', 15)
        self.pdf.setStrokeColorRGB(0, 0, 0)

        # Texty
        self.drawMain()
        self.drawTitle()
        self.drawProvider(self.TOP - 10,self.LEFT + 3)
        self.drawClient(self.TOP - 35,self.LEFT + 91)
        self.drawPayment(self.TOP - 47,self.LEFT + 3)
        self.drawItems(self.TOP - 80,self.LEFT)
        self.drawDates(self.TOP - 10,self.LEFT + 91)

        #self.pdf.setFillColorRGB(0, 0, 0)

        self.pdf.showPage()
        self.pdf.save()

    #############################################################
    ## Draw methods
    #############################################################

    def addMetaInformation(self, pdf):
        pdf.setCreator(self.invoice.provider.summary)
        pdf.setTitle(self.invoice.title)
        pdf.setAuthor(self.invoice.creator.name)

    def drawTitle(self):
        # Up line
        self.pdf.drawString(self.LEFT*mm, self.TOP*mm, self.invoice.title)
        self.pdf.drawString((self.LEFT + 90) * mm,
            self.TOP*mm,
            _(u'Variable symbol: %s') %
            self.invoice.variable_symbol)

    def drawMain(self):
        # Borders
        self.pdf.rect(self.LEFT * mm, (self.TOP - 68) * mm,
                      (self.LEFT + 156) * mm, 65 * mm, stroke=True, fill=False)

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

    def drawClient(self,TOP,LEFT):
        self.pdf.setFont('DejaVu', 12)
        self.pdf.drawString(LEFT * mm, TOP * mm, _(u'Customer'))
        self.pdf.setFont('DejaVu', 8)

        text = self.pdf.beginText((LEFT + 2) * mm, (TOP - 4) * mm)
        text.textLines('\n'.join(self.invoice.client.get_address_lines()))
        self.pdf.drawText(text)

        text = self.pdf.beginText((LEFT + 2) * mm, (TOP - 23) * mm)
        text.textLines('\n'.join(self.invoice.client.get_contact_lines()))
        self.pdf.drawText(text)

        if self.invoice.client.note:
            self.pdf.setFont('DejaVu', 6)
            text = self.pdf.beginText((LEFT + 2) * mm, (TOP - 28) * mm)
            text.textLines(self.invoice.client.note)
            self.pdf.drawText(text)


    def drawProvider(self,TOP,LEFT):
        self.pdf.setFont('DejaVu', 12)
        self.pdf.drawString(LEFT * mm, TOP * mm, _(u'Provider'))
        self.pdf.setFont('DejaVu', 8)

        text = self.pdf.beginText((LEFT + 2) * mm, (TOP - 6) * mm)
        text.textLines('\n'.join(self.invoice.provider.get_address_lines()))
        self.pdf.drawText(text)

        text = self.pdf.beginText((LEFT + 40) * mm, (TOP - 6) * mm)
        text.textLines('\n'.join(self.invoice.provider.get_contact_lines()))

        self.pdf.drawText(text)
        if self.invoice.provider.note:
            self.pdf.setFont('DejaVu', 6)
            text = self.pdf.beginText((LEFT + 2) * mm, (TOP - 23) * mm)
            text.textLines(self.invoice.provider.note)
            self.pdf.drawText(text)

    def drawPayment(self,TOP,LEFT):
        self.pdf.setFont('DejaVu-Bold', 9)
        self.pdf.drawString(LEFT * mm, TOP * mm, _(u'Payment information'))

        text = self.pdf.beginText((LEFT + 2) * mm, (TOP - 6) * mm)
        lines = [
            self.invoice.provider.bank_name,
            '%s: %s' % (_(u'Bank account'), self.invoice.provider.bank_account),
            '%s: %s' % (_(u'Variable symbol'), self.invoice.variable_symbol)
        ]
        if self.invoice.specific_symbol:
            lines.append(
                '%s: %s' % (_(u'Specific symbol'), self.invoice.specific_symbol))
        text.textLines('\n'.join(lines))
        self.pdf.drawText(text)

    def drawItems(self,TOP,LEFT):
        # Items
        path = self.pdf.beginPath()
        path.moveTo(LEFT * mm, (TOP - 4) * mm)
        path.lineTo((LEFT + 176) * mm, (TOP - 4) * mm)
        self.pdf.drawPath(path, True, True)

        self.pdf.setFont('DejaVu-Bold', 7)
        self.pdf.drawString((LEFT + 1) * mm, (TOP - 2) * mm, _(u'List of items'))

        self.pdf.drawString((LEFT + 1) * mm, (TOP - 9) * mm, _(u'Description'))
        items_are_with_tax = self.invoice.use_tax
        if items_are_with_tax:
            i=9
            self.pdf.drawString((LEFT + 68) * mm, (TOP - i) * mm, _(u'Units'))
            self.pdf.drawString((LEFT + 88) * mm, (TOP - i) * mm,
                                _(u'Price per one'))
            self.pdf.drawString((LEFT + 115) * mm, (TOP - i) * mm,
                                _(u'Total price'))
            self.pdf.drawString((LEFT + 137) * mm, (TOP - i) * mm,
                                _(u'Tax'))
            self.pdf.drawString((LEFT + 146) * mm, (TOP - i) * mm,
                                _(u'Total price with tax'))
            i+=5
        else:
            i=9
            self.pdf.drawString((LEFT + 104) * mm, (TOP - i) * mm,
                                _(u'Units'))
            self.pdf.drawString((LEFT + 123) * mm, (TOP - i) * mm,
                                _(u'Price per one'))
            self.pdf.drawString((LEFT + 150) * mm, (TOP - i) * mm,
                                _(u'Total price'))
            i+=5

        self.pdf.setFont('DejaVu', 7)

        # List
        for item in self.invoice.items:
            self.pdf.drawString((LEFT + 1) * mm, (TOP - i) * mm, item.description)
            if item.tax or items_are_with_tax:
                items_are_with_tax = True
                if len(item.description) > 52: i+=5
                if float(int(item.count)) == item.count:
                    self.pdf.drawString((LEFT + 68) * mm, (TOP - i) * mm, '%d %s' % (item.count, item.unit))
                else:
                    self.pdf.drawString((LEFT + 68) * mm, (TOP - i) * mm, '%.1f %s' % (item.count, item.unit))
                self.pdf.drawString((LEFT + 88) * mm, (TOP - i) * mm, '%.2f,- %s' % (item.price, self.invoice.currency))
                self.pdf.drawString((LEFT + 115) * mm, (TOP - i) * mm, '%.2f,- %s' % (item.total, self.invoice.currency))
                self.pdf.drawString((LEFT + 137) * mm, (TOP - i) * mm, '%.0f %%' % item.tax)
                self.pdf.drawString((LEFT + 146) * mm, (TOP - i) * mm, '%.2f,- %s' % (item.total_tax, self.invoice.currency))
                i+=5
            else:
                if len(item.description) > 75: i+=5
                if float(int(item.count)) == item.count:
                    self.pdf.drawString((LEFT + 104) * mm, (TOP - i) * mm, '%d %s' % (item.count, item.unit))
                else:
                    self.pdf.drawString((LEFT + 104) * mm, (TOP - i) * mm, '%.1f %s' % (item.count, item.unit))
                self.pdf.drawString((LEFT + 123) * mm, (TOP - i) * mm, '%.2f,- %s' % (item.price, self.invoice.currency))
                self.pdf.drawString((LEFT + 150) * mm, (TOP - i) * mm, '%.2f,- %s' % (item.total, self.invoice.currency))
                i+=5

        if self.invoice.rounding_result:
            path = self.pdf.beginPath()
            path.moveTo(LEFT * mm, (TOP - i) * mm)
            path.lineTo((LEFT + 176) * mm, (TOP - i) * mm)
            i += 5
            self.pdf.drawPath(path, True, True)
            self.pdf.drawString((LEFT + 1) * mm, (TOP - i) * mm, _(u'Rounding'))
            self.pdf.drawString((LEFT + 68) * mm, (TOP - i) * mm, '%.2f,- %s' % (self.invoice.difference_in_rounding, self.invoice.currency))
            i += 3

        path = self.pdf.beginPath()
        path.moveTo(LEFT * mm, (TOP - i) * mm)
        path.lineTo((LEFT + 176) * mm, (TOP - i) * mm)
        self.pdf.drawPath(path, True, True)

        if not items_are_with_tax:
            self.pdf.setFont('DejaVu-Bold', 11)
            self.pdf.drawString((LEFT + 100) * mm, (TOP - i - 7) * mm, _(u'Total')+': %.2f %s' % (self.invoice.price, self.invoice.currency))
        else:
            self.pdf.setFont('DejaVu-Bold', 6)
            self.pdf.drawString((LEFT + 1) * mm, (TOP - i - 2) * mm, _(u'Breakdown VAT'))
            vat_list, tax_list, total_list, total_tax_list = [_(u'VAT rate')], [_(u'Tax')], [_(u'Without VAT')], [_(u'With VAT')]
            for vat, items in self.invoice.generate_breakdown_vat().iteritems():
                vat_list.append('%.2f%%' % vat)
                tax_list.append('%.2f %s' % (items['tax'], self.invoice.currency))
                total_list.append('%.2f %s' % (items['total'], self.invoice.currency))
                total_tax_list.append('%.2f %s' % (items['total_tax'], self.invoice.currency))


            self.pdf.setFont('DejaVu', 6)
            text = self.pdf.beginText((LEFT + 1) * mm, (TOP - i - 5) * mm)
            text.textLines('\n'.join(vat_list))
            self.pdf.drawText(text)

            text = self.pdf.beginText((LEFT + 11) * mm, (TOP - i - 5) * mm)
            text.textLines('\n'.join(tax_list))
            self.pdf.drawText(text)

            text = self.pdf.beginText((LEFT + 27) * mm, (TOP - i - 5) * mm)
            text.textLines('\n'.join(total_list))
            self.pdf.drawText(text)

            text = self.pdf.beginText((LEFT + 45) * mm, (TOP - i - 5) * mm)
            text.textLines('\n'.join(total_tax_list))
            self.pdf.drawText(text)



            self.pdf.setFont('DejaVu-Bold', 11)
            self.pdf.drawString((LEFT + 100) * mm, (TOP - i - 14) * mm, _(u'Total with tax')+': %.2f %s' % (self.invoice.price_tax, self.invoice.currency))

        if items_are_with_tax:
            self.pdf.rect(LEFT * mm, (TOP - i - 17) * mm, (LEFT + 156) * mm, (i + 19) * mm, stroke=True, fill=False) #140,142
        else:
            self.pdf.rect(LEFT * mm, (TOP - i - 11) * mm, (LEFT + 156) * mm, (i + 13) * mm, stroke=True, fill=False) #140,142

        if self.invoice.creator.stamp_filename:
            im = Image.open(self.invoice.creator.stamp_filename)
            height = float(im.size[1]) / (float(im.size[0])/200.0)
            self.pdf.drawImage(self.invoice.creator.stamp_filename, (LEFT + 98) * mm, (TOP - i - 72) * mm, 200, height)

        path = self.pdf.beginPath()
        path.moveTo((LEFT + 110) * mm, (TOP - i - 70) * mm)
        path.lineTo((LEFT + 164) * mm, (TOP - i - 70) * mm)
        self.pdf.drawPath(path, True, True)

        self.pdf.drawString((LEFT + 112) * mm, (TOP - i - 75) * mm, '%s: %s' % (_(u'Creator'), self.invoice.creator.name))


    def drawDates(self,TOP,LEFT):
        self.pdf.setFont('DejaVu', 10)
        top = TOP + 1
        items = [
            (LEFT * mm, '%s: %s' % (_(u'Date'), self.invoice.date)),
            (LEFT * mm, '%s: %s' % (_(u'Payback'),
                                              self.invoice.payback))

        ]
        if self.invoice.taxable_date:
            items.append((LEFT * mm, '%s: %s' % (_(u'Taxable date'),
                        self.invoice.taxable_date)))

        items.append((LEFT * mm, '%s: %s' % (_(u'Paytype'),
                                                       self.invoice.paytype)))

        for item in items:
            self.pdf.drawString(item[0], top * mm, item[1])
            top += -5


class CorrectingInvoice(SimpleInvoice):
    def gen(self, filename):
        self.TOP = 260
        self.LEFT = 20
        self.filename = filename

        pdfmetrics.registerFont(TTFont('DejaVu', FONT_PATH))
        pdfmetrics.registerFont(TTFont('DejaVu-Bold', FONT_BOLD_PATH))

        self.pdf = Canvas(self.filename, pagesize = letter)
        self.addMetaInformation(self.pdf)

        self.pdf.setFont('DejaVu', 15)
        self.pdf.setStrokeColorRGB(0, 0, 0)

        # Texty
        self.drawMain()
        self.drawTitle()
        self.drawProvider(self.TOP - 10,self.LEFT + 3)
        self.drawClient(self.TOP - 35,self.LEFT + 91)
        self.drawPayment(self.TOP - 47,self.LEFT + 3)
        self.drawCorretion(self.TOP - 73,self.LEFT)
        self.drawItems(self.TOP - 82,self.LEFT)
        self.drawDates(self.TOP - 10,self.LEFT + 91)

        #self.pdf.setFillColorRGB(0, 0, 0)

        self.pdf.showPage()
        self.pdf.save()

    def drawTitle(self):
        # Up line
        self.pdf.drawString(self.LEFT*mm, self.TOP*mm, self.invoice.title)
        self.pdf.drawString((self.LEFT + 90) * mm,
            self.TOP*mm,
            _(u'Correcting document: %s') %
            self.invoice.number)


    def drawCorretion(self,TOP,LEFT):
        self.pdf.setFont('DejaVu', 8)
        self.pdf.drawString(LEFT * mm, TOP * mm, _(u'Correction document for invoice: %s') % self.invoice.variable_symbol)
        self.pdf.drawString(LEFT * mm, (TOP - 4) * mm, _(u'Reason to correction: %s') % self.invoice.reason)
