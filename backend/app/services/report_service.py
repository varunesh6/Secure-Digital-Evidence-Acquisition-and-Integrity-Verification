from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_report_pdf(case, evidence_records, verification_records, output_path):
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("Digital Evidence Report", styles["Title"]))
    story.append(Spacer(1, 18))
    story.append(Paragraph(f"Case ID: {case.get('case_number', 'N/A')}", styles["Heading2"]))
    story.append(Paragraph(f"Title: {case.get('title', 'N/A')}", styles["BodyText"]))
    story.append(Paragraph(f"Incident Category: {case.get('incident_category', 'N/A')}", styles["BodyText"]))
    story.append(Paragraph(f"Priority: {case.get('priority', 'N/A')}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    data = [["Evidence ID", "Filename", "SHA-256", "Status"]]
    for item in evidence_records:
        data.append([str(item.get("id", "")), item.get("original_filename", ""), item.get("original_sha256", ""), item.get("status", "")])

    table = Table(data, colWidths=[80, 160, 180, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C7BE5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(table)

    story.append(Spacer(1, 18))
    story.append(Paragraph("Integrity verification notes:", styles["Heading2"]))
    for ver in verification_records:
        story.append(Paragraph(f"- {ver.get('result', 'UNKNOWN')} on {ver.get('verification_timestamp', '')}", styles["BodyText"]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    Path(output_path).write_bytes(pdf_bytes)
    return output_path
