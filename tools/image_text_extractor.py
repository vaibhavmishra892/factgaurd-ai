"""
Image Text Extractor Tool
Extracts text from images using OCR (Tesseract)
"""
import pytesseract
from PIL import Image
import os
from typing import Dict, Optional
import re
from schemas.response_messages import ocr_issue, tesseract_missing


class ImageTextExtractorTool:
    """Tool for extracting text from images using OCR"""
    
    def __init__(self):
        # Configure tesseract path if needed (Windows)
        # Uncomment and adjust if tesseract is not in PATH
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def is_valid_image(self, file_path: str) -> bool:
        """
        Validate if file exists and is an image
        
        Args:
            file_path: Path to image file
            
        Returns:
            True if valid image file
        """
        if not os.path.exists(file_path):
            return False
        
        # Check file extension
        valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in valid_extensions:
            return False
        
        # Try to open as image
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except:
            return False
    
    def extract_text(self, image_path: str) -> Dict[str, str]:
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        # Validate image
        if not self.is_valid_image(image_path):
            return {"error": f"Invalid or non-existent image file: {image_path}"}
        
        try:
            # Open image
            image = Image.open(image_path)
            
            # Preprocess image for better OCR
            image = self._preprocess_image(image)
            
            # Extract text using pytesseract
            extracted_text = pytesseract.image_to_string(image, lang='eng')
            
            # Clean extracted text
            extracted_text = self._clean_text(extracted_text)
            
            # Validate we got meaningful content
            if len(extracted_text.strip()) < 10:
                return {
                    "error": "No readable text found in image - image may be too low quality or contain no text"
                }
            
            return {
                "image_path": image_path,
                "extracted_text": extracted_text,
                "text_length": len(extracted_text),
                "source": "OCR - Tesseract"
            }
            
        except pytesseract.TesseractNotFoundError:
            return {"error": tesseract_missing()}
        except FileNotFoundError:
            return {"error": f"⚠️ **Image file not found.**\n\nPlease check the path: {image_path}"}
        except Exception as e:
            return {"error": ocr_issue()}
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed image
        """
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too small (improve OCR accuracy)
        width, height = image.size
        if width < 300 or height < 300:
            scale = max(300 / width, 300 / height)
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    def _clean_text(self, text: str) -> str:
        """
        Clean OCR-extracted text
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        # Remove common OCR artifacts
        text = text.replace('|', 'I')  # Common misread
        text = text.replace('0', 'O') if text.count('0') < text.count('O') / 10 else text
        
        return text.strip()
