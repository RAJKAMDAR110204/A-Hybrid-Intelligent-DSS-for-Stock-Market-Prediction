from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def generate_report(filename, data):

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("📊 SmartInvestor AI Report", styles['Title']))
    content.append(Spacer(1, 20))

    table_data = [[key, str(value)] for key, value in data.items()]

    table = Table(table_data)

    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke)
    ]))

    content.append(table)
    content.append(Spacer(1, 20))
    content.append(Paragraph("Generated using AI Stock Predictor", styles['Italic']))

    doc.build(content)