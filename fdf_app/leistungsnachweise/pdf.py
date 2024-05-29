from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime, timedelta

def modifyPdf(input_pdf_path, output_pdf_path, biling_id, vorname, nachname, straße, hausnummer, stadt, postleitzahl):
    print(f"Current billing Id {biling_id}")
    print(f"Current vorname {vorname}")
    print(f"Current nachname {nachname}")

    # Laden der vorhandenen PDF-Datei
    input_pdf = PdfReader(open(input_pdf_path, "rb"))

    # Erstellen des neuen PDF-Dokuments
    output_pdf = PdfWriter()

    # Kopieren des Inhalts der vorhandenen PDF-Seiten und Hinzufügen des Texts
    for page in input_pdf.pages:
        # Hinzufügen des Texts zur Seite
        page.merge_page(page)
        page.merge_page(create_text_page(biling_id, vorname, nachname, straße, hausnummer, stadt, postleitzahl))

        # Hinzufügen der Seite zum neuen PDF-Dokument
        output_pdf.add_page(page)

    # Speichern des modifizierten PDFs
    with open(output_pdf_path, "wb") as output_file:
        output_pdf.write(output_file)


def create_text_page(biling_id, vorname, nachname, straße, hausnummer, stadt, postleitzahl):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from io import BytesIO

    # Erstellen eines neuen Canvas
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    now = datetime.now()
    formated_date = now.strftime("%d.%m.%Y")
    formated_pay_date = now + timedelta(days=14)
    formated_pay_date = formated_pay_date.strftime("%d.%m.%Y")

    # Hinzufügen des Texts zur Seite
    c.setFont("Helvetica", 10)
    c.drawString(450, 538, formated_date)
    c.drawString(450, 520, formated_pay_date)
    c.drawString(175, 538, biling_id)
    c.drawString(73, 700, vorname )
    c.drawString(140, 700, nachname )
    c.drawString(73, 688, straße )
    c.drawString(160, 688, str(hausnummer) )
    c.drawString(73, 676, str(postleitzahl) )
    c.drawString(73, 664, stadt )
    c.setFont("Helvetica", 20)
    c.drawString(71, 720, "Empfänger:" )
    c.save()

    # Rückgabe des Canvas als PDF-Seite
    return PdfReader(packet).pages[0]
