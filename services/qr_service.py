import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
from PIL import Image

def generate_qr_image(token, student_name, nis):
    """Generate QR Code image as base64 PNG"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    # QR contains token only (no password)
    qr.add_data(f"ALKAUTSAR:{token}:{nis}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="#064E3B", back_color="#FFFFFF")
    
    # Add logo overlay if needed
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

def generate_qr_file(token, nis, filepath):
    """Save QR Code to file"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(f"ALKAUTSAR:{token}:{nis}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="#064E3B", back_color="#FFFFFF")
    img.save(filepath)
    return filepath