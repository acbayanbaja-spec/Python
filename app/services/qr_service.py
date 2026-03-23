"""
QR Code Service for generating and managing claim codes
"""
import qrcode
import io
import base64
import secrets
import string
import json
from datetime import datetime
from PIL import Image  # kept for pillow import availability

class QRService:
    """Service for QR code generation and management"""
    
    @staticmethod
    def generate_claim_code() -> str:
        """Generate a unique claim code"""
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(12))
    
    @staticmethod
    def _build_claim_payload(claim_code: str, claim_id: int = None) -> str:
        """Create a compact JSON payload for QR contents"""
        payload = {
            "type": "SEAIT_CLAIM",
            "claim_code": claim_code,
            "claim_id": claim_id,
            "issued_at": datetime.utcnow().isoformat() + "Z"
        }
        return json.dumps(payload, separators=(",", ":"))

    @staticmethod
    def generate_qr_code(data: str, box_size: int = 11, border: int = 4) -> str:
        """
        Generate QR code image as base64 string with high error correction.
        Returns base64 encoded image data.
        """
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str
    
    @staticmethod
    def generate_qr_code_for_claim(claim_code: str, claim_id: int = None) -> str:
        """Generate QR code for a claim code with metadata payload"""
        payload = QRService._build_claim_payload(claim_code=claim_code, claim_id=claim_id)
        return QRService.generate_qr_code(payload, box_size=11, border=4)
