# utils/pdf_utils.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO
import textwrap

def generate_feedback_pdf(feedback_text: str, rating: int) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Margins and text settings
    left_margin = 1 * inch
    right_margin = 1 * inch
    top_margin = 1 * inch
    bottom_margin = 1 * inch
    max_width = width - left_margin - right_margin
    line_height = 14
    font_size = 11

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(left_margin, height - top_margin, "I-Sensei.ai Interview Feedback")

    # Rating
    c.setFont("Helvetica", 12)
    c.drawString(left_margin, height - top_margin - 25, f"Rating: {rating}/10")

    # Feedback content
    c.setFont("Helvetica", font_size)
    y = height - top_margin - 50  # Initial Y position

    wrapper = textwrap.TextWrapper(width=95)  # Controls wrapping length
    for line in feedback_text.strip().split('\n'):
        wrapped_lines = wrapper.wrap(text=line)
        for wrapped_line in wrapped_lines:
            if y < bottom_margin:
                c.showPage()
                y = height - top_margin
                c.setFont("Helvetica", font_size)
            c.drawString(left_margin, y, wrapped_line)
            y -= line_height

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
