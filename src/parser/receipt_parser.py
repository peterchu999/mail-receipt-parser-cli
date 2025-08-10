import re


class ReceiptParser:
    """Parses transaction data from email content."""
    
    def __init__(self):
        pass
    
    def extract_total_amount(self, text):
        """
        Extract total amount from text using regex.
        Looks for patterns like 'total: Rp 123.456', 'Total: 123.456', 'TOTAL Rp 123.456', etc.
        Supports IDR (Indonesian Rupiah) currency format.
        """
        if not text:
            return None
        
        # Convert to string if it's bytes
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='ignore')
        
        # Multiple regex patterns to catch different total formats (IDR focused)
        patterns = [
            # IDR specific patterns
            r'total\s*:?\s*Rp\s*([\d.,]+)',  # total: Rp 123.456, total Rp 123.456
            r'Total\s*:?\s*Rp\s*([\d.,]+)',  # Total: Rp 123.456, Total Rp 123.456
            r'TOTAL\s*:?\s*Rp\s*([\d.,]+)',  # TOTAL: Rp 123.456, TOTAL Rp 123.456
            r'total\s+paid\s*:?\s*Rp\s*([\d.,]+)',  # Total Paid: Rp 123.456, total paid Rp 123.456
            r'Total\s+Paid\s*:?\s*Rp\s*([\d.,]+)',  # Total Paid: Rp 123.456, Total Paid Rp 123.456
            r'TOTAL\s+PAID\s*:?\s*Rp\s*([\d.,]+)',  # TOTAL PAID: Rp 123.456, TOTAL PAID Rp 123.456
            r'Rp\s*([\d.,]+)\s*\(?total\)?',  # Rp 123.456 total, Rp 123.456 (total)
            r'amount\s*:?\s*Rp\s*([\d.,]+)',  # amount: Rp 123.456
            r'Amount\s*:?\s*Rp\s*([\d.,]+)',  # Amount: Rp 123.456
            
            # IDR without currency symbol
            r'total\s*:?\s*([\d.,]+)',  # total: 123.456, total 123.456
            r'Total\s*:?\s*([\d.,]+)',  # Total: 123.456, Total 123.456
            r'TOTAL\s*:?\s*([\d.,]+)',  # TOTAL: 123.456, TOTAL 123.456
            
            # Alternative IDR formats
            r'Rp\s*([\d.,]+)',  # Rp 123.456 (anywhere in text)
            r'IDR\s*([\d.,]+)',  # IDR 123.456
            r'Rupiah\s*([\d.,]+)',  # Rupiah 123.456
            
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1)
                # Handle IDR format: remove dots (thousand separators) and replace comma with dot (decimal)
                # IDR format: 123.456,78 -> 123456.78
                if '.' in amount_str and ',' in amount_str:
                    # Has both dots and commas - assume IDR format
                    amount_str = amount_str.replace('.', '').replace(',', '.')
                elif '.' in amount_str and ',' not in amount_str:
                    # Only dots - could be IDR or decimal, check if it looks like IDR (3+ digits after dot)
                    parts = amount_str.split('.')
                    if len(parts) > 1 and len(parts[-1]) <= 2:
                        # Looks like decimal format (e.g., 123.45)
                        amount_str = amount_str.replace(',', '')
                    else:
                        # Looks like IDR format (e.g., 123.456)
                        amount_str = amount_str.replace('.', '').replace(',', '.')
                else:
                    # No dots or only commas - treat as regular decimal
                    amount_str = amount_str.replace(',', '')
                
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def parse_receipt_data(self, email_info):
        """Parse receipt data from email info and add total amount."""
        # Extract total amount from body content
        total_amount = self.extract_total_amount(email_info.get('body_content', ''))
        
        # Add total amount to email info
        email_info['total_amount'] = total_amount if total_amount is not None else 0.0
        
        # Remove body_content from final result (not needed in CSV)
        if 'body_content' in email_info:
            del email_info['body_content']
        
        return email_info 