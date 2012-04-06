# -*- coding: utf - 8 -*-
from PIL import Image
try:
    import gettext
    _ = gettext.gettext
except ImportError:
    _ = lambda x: x

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics



from api import Invoice


class BaseInvoice(object):

    FONT_PATH = '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf'
    FONT_BOLD_PATH = '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf'

    def __init__(self, invoice):
        assert isinstance(invoice, Invoice)

        self.invoice = invoice


    def gen(self, filename):
        self.TOP = 260
        self.LEFT = 20
        self.filename = filename

        pdfmetrics.registerFont(TTFont('DejaVu', self.FONT_PATH))
        pdfmetrics.registerFont(TTFont('DejaVu-Bold', self.FONT_BOLD_PATH))

        self.pdf = Canvas(self.filename, pagesize = letter)
        self.addMetaInformation(self.pdf)

        self.pdf.setFont('DejaVu', 15)
        self.pdf.setStrokeColorRGB(0, 0, 0)

        # Texty
        self.drawMain()
        self.drawProvider(self.TOP - 10,self.LEFT + 3)
        self.drawClient(self.TOP - 30,self.LEFT + 91)
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
        pdf.setCreator(self.invoice.creator)
        pdf.setTitle(self.invoice.title)

    def drawMain(self):
        # Up line
        self.pdf.drawString(self.LEFT*mm, self.TOP*mm, _('Invoice'))
        self.pdf.drawString((self.LEFT + 100) * mm,
                            self.TOP*mm,
                            _('Variable symbol: %s') %
                            self.invoice.variable_symbol)

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
        path.moveTo((self.LEFT + 88) * mm, (self.TOP - 23) * mm)
        path.lineTo((self.LEFT + 176) * mm, (self.TOP - 23) * mm)
        self.pdf.drawPath(path, True, True)

    def drawClient(self,TOP,LEFT):
        self.pdf.setFont('DejaVu', 12)
        self.pdf.drawString(LEFT * mm, TOP * mm, _('Customer'))
        self.pdf.setFont('DejaVu', 8)

        text = self.pdf.beginText((LEFT + 2) * mm, (TOP - 6) * mm)
        text.textLines('\n'.join(self.invoice.client.get_address_lines()))
        self.pdf.drawText(text)

        text = self.pdf.beginText((LEFT + 2) * mm, (TOP - 28) * mm)
        text.textLines('\n'.join(self.invoice.client.get_contact_lines()))
        self.pdf.drawText(text)

    def drawProvider(self,TOP,LEFT):
        self.pdf.setFont('DejaVu', 12)
        self.pdf.drawString(LEFT * mm, TOP * mm, _('Provider'))
        self.pdf.setFont('DejaVu', 8)

        text = self.pdf.beginText((LEFT + 2) * mm, (TOP - 6) * mm)
        text.textLines('\n'.join(self.invoice.provider.get_address_lines()))
        self.pdf.drawText(text)

        text = self.pdf.beginText((LEFT + 40) * mm, (TOP - 6) * mm)
        text.textLines('\n'.join(self.invoice.provider.get_contact_lines()))

        self.pdf.drawText(text)
        if self.invoice.provider.note:
            self.pdf.drawString((LEFT + 2) * mm, (TOP - 26) * mm,
                                self.invoice.provider.note)

    def drawPayment(self,TOP,LEFT):
        self.pdf.setFont('DejaVu-Bold', 9)
        self.pdf.drawString(LEFT * mm, TOP * mm, _('Payment information'))

        text = self.pdf.beginText((LEFT + 2) * mm, (TOP - 6) * mm)
        lines = [
            self.invoice.provider.bank_name,
            '%s: %s' % (_('Bank account'), self.invoice.provider.bank_account),
            '%s: %s' % (_('Variable symbol'), self.invoice.variable_symbol)
        ]
        text.textLines('\n'.join(lines))
        self.pdf.drawText(text)

    def drawItems(self,TOP,LEFT):
        # Items
        path = self.pdf.beginPath()
        path.moveTo(LEFT * mm, (TOP - 4) * mm)
        path.lineTo((LEFT + 176) * mm, (TOP - 4) * mm)
        self.pdf.drawPath(path, True, True)

        self.pdf.setFont('DejaVu-Bold', 7)
        self.pdf.drawString((LEFT + 1) * mm, (TOP - 2) * mm, _('List of items'))

        self.pdf.drawString((LEFT + 1) * mm, (TOP - 9) * mm, _('Description'))
        if self.invoice.vat_number:
            i=9
            self.pdf.drawString((LEFT + 68) * mm, (TOP - i) * mm, _('Units'))
            self.pdf.drawString((LEFT + 88) * mm, (TOP - i) * mm,
                                _('Price per one'))
            self.pdf.drawString((LEFT + 115) * mm, (TOP - i) * mm,
                                _('Total price'))
            self.pdf.drawString((LEFT + 137) * mm, (TOP - i) * mm,
                                _('Tax'))
            self.pdf.drawString((LEFT + 146) * mm, (TOP - i) * mm,
                                _('Total price with tax'))
            i+=5
        else:
            i=9
            self.pdf.drawString((LEFT + 104) * mm, (TOP - i) * mm,
                                _('Units'))
            self.pdf.drawString((LEFT + 123) * mm, (TOP - i) * mm,
                                _('Price per one'))
            self.pdf.drawString((LEFT + 150) * mm, (TOP - i) * mm,
                                _('Total price'))
            i+=5

        self.pdf.setFont('DejaVu', 7)

        # List
        for item in self.invoice.items:
            self.pdf.drawString((LEFT + 1) * mm, (TOP - i) * mm, item.description)
            if self.invoice.vat_number:
                if len(item.description) > 52: i+=5
                if float(int(item.count)) == item.count:
                    self.pdf.drawString((LEFT + 68) * mm, (TOP - i) * mm, '%d %s' % (item.count, item.unit))
                else:
                    self.pdf.drawString((LEFT + 68) * mm, (TOP - i) * mm, '%.1f %s' % (item.count, item.unit))
                self.pdf.drawString((LEFT + 88) * mm, (TOP - i) * mm, '%.0f,- %s' % (item.price, self.invoice.currency))
                self.pdf.drawString((LEFT + 115) * mm, (TOP - i) * mm, '%.0f,- %s' % (item.total, self.invoice.currency))
                self.pdf.drawString((LEFT + 137) * mm, (TOP - i) * mm, '%.0f %%' % item.tax)
                self.pdf.drawString((LEFT + 146) * mm, (TOP - i) * mm, '%.0f,- %s' % (item.total_tax, self.invoice.currency))
                i+=5
            else:
                if len(item.description) > 75: i+=5
                if float(int(item.count)) == item.count:
                    self.pdf.drawString((LEFT + 104) * mm, (TOP - i) * mm, '%d %s' % (item.count, item.unit))
                else:
                    self.pdf.drawString((LEFT + 104) * mm, (TOP - i) * mm, '%.1f %s' % (item.count, item.unit))
                self.pdf.drawString((LEFT + 123) * mm, (TOP - i) * mm, '%.0f,- %s' % (item.price, self.invoice.currency))
                self.pdf.drawString((LEFT + 150) * mm, (TOP - i) * mm, '%.0f,- %s' % (item.total, self.invoice.currency))
                i+=5

        path = self.pdf.beginPath()
        path.moveTo(LEFT * mm, (TOP - i) * mm)
        path.lineTo((LEFT + 176) * mm, (TOP - i) * mm)
        self.pdf.drawPath(path, True, True)

        self.pdf.setFont('DejaVu-Bold', 11)
        self.pdf.drawString((LEFT + 100) * mm, (TOP - i - 7) * mm, _('Total')+': %.2f %s' % (self.invoice.price, self.invoice.currency))
        if self.invoice.vat_number:
            self.pdf.drawString((LEFT + 100) * mm, (TOP - i - 14) * mm, _('Total with tax')+': %.2f %s' % (self.invoice.price_tax, self.invoice.currency))

        if self.invoice.vat_number:
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

        self.pdf.drawString((LEFT + 112) * mm, (TOP - i - 75) * mm, '%s: %s' % (_('Creator'), self.invoice.creator))


    def drawDates(self,TOP,LEFT):
        self.pdf.setFont('DejaVu', 10)
        self.pdf.drawString(LEFT * mm, (TOP + 1) * mm, '%s: %s' % (_('Date'), self.invoice.date))
        self.pdf.drawString(LEFT * mm, (TOP - 4) * mm, '%s: %s' % (_('Payback'), self.invoice.payback))
        self.pdf.drawString(LEFT * mm, (TOP - 9) * mm, '%s: %s' % (_('Paytype'), self.invoice.paytype))