import fitz  # PyMuPDF
import io
from PIL import Image
import streamlit as st

class PDFProcessor:
    """Handle PDF processing operations including text and image extraction."""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_content(self, pdf_path):
        """
        Extract text and images from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            tuple: (extracted_text, list_of_images)
        """
        try:
            doc = fitz.open(pdf_path)
            text = ""
            images = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text
                page_text = page.get_text()
                text += page_text + "\n"
                
                # Extract images
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        # Convert to PIL Image for better handling
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        # Convert to RGB if necessary
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        # Convert back to bytes for storage
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG')
                        img_byte_arr = img_byte_arr.getvalue()
                        
                        images.append(img_byte_arr)
                        
                    except Exception as img_error:
                        st.warning(f"Could not extract image {img_index + 1} from page {page_num + 1}: {str(img_error)}")
                        continue
            
            doc.close()
            
            # Clean and validate text
            text = self._clean_text(text)
            
            return text, images
            
        except Exception as e:
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def _clean_text(self, text):
        """
        Clean and normalize extracted text.
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Only keep non-empty lines
                cleaned_lines.append(line)
        
        # Join lines with single newline
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove excessive spaces
        import re
        cleaned_text = re.sub(r' +', ' ', cleaned_text)
        
        return cleaned_text
    
    def get_document_stats(self, text, images):
        """
        Get basic statistics about the extracted content.
        
        Args:
            text (str): Extracted text
            images (list): List of extracted images
            
        Returns:
            dict: Document statistics
        """
        words = text.split()
        
        stats = {
            'character_count': len(text),
            'word_count': len(words),
            'line_count': len(text.split('\n')),
            'image_count': len(images),
            'estimated_reading_time': max(1, len(words) // 200)  # Assume 200 WPM
        }
        
        return stats
