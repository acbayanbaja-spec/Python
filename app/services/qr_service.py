"""
QR Code Service for generating and managing claim codes
"""
import qrcode
import io
import base64
import secrets
import string
from PIL import Image

class QRService:
    """Service for QR code generation and management"""
    
    @staticmethod
    def generate_claim_code() -> str:
        """Generate a unique claim code"""
        # Generate 12-character alphanumeric code
        alphabet = string.ascii_uppercase + string.digits
        code = ''.join(secrets.choice(alphabet) for _ in range(12))
        return code
    
    @staticmethod
    def generate_qr_code(data: str) -> str:
        """
        Generate QR code image as base64 string
        Returns base64 encoded image data
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str
    
    @staticmethod
    def generate_qr_code_for_claim(claim_code: str) -> str:
        """Generate QR code for a claim code"""
        return QRService.generate_qr_code(claim_code)
