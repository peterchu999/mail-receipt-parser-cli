import re
import html
from email.header import decode_header
from email.utils import parsedate_to_datetime


class EmailParser:
    """Extracts and processes email content."""
    
    def __init__(self):
        pass
    
    def extract_content_from_part(self, part):
        """Extract content from email part with proper decoding."""
        try:
            content = part.get_payload(decode=True)
            if content:
                # Handle different encodings
                if isinstance(content, bytes):
                    # Try different encodings
                    for encoding in ['utf-8', 'iso-8859-1', 'windows-1252']:
                        try:
                            return content.decode(encoding)
                        except (UnicodeDecodeError, AttributeError):
                            continue
                    # If all fail, use error handling
                    return content.decode('utf-8', errors='ignore')
                return str(content)
            return ""
        except Exception as e:
            print(f"Error extracting content: {e}")
            return ""
    
    def clean_raw_message(self, body_content):
        """Clean raw message by removing HTML tags and normalizing whitespace."""
        if not body_content:
            print("Warning: body_content is empty in clean_raw_message")
            return ""
        
        # Convert bytes to string if needed
        if isinstance(body_content, bytes):
            body_content = body_content.decode('utf-8', errors='ignore')
        
        # Unescape HTML entities first
        cleaned_text = html.unescape(body_content)
        
        # Remove HTML tags using regex
        cleaned_text = re.sub(r'<[^>]+>', '', cleaned_text)
        
        # Remove excessive whitespace and normalize line breaks
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)
        
        # Strip leading/trailing whitespace
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text
    
    def extract_email_info(self, email_message):
        """Extract complete information from an email message for CSV export."""
        # Extract subject
        subject = decode_header(email_message['subject'])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode('utf-8', errors='ignore')
        
        # Extract sender (from)
        sender = email_message['from']
        
        # Extract and normalize date to ISO format
        raw_date = email_message['date']
        try:
            # Parse email date and convert to ISO format
            parsed_date = parsedate_to_datetime(raw_date)
            normalized_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
        except:
            # Fallback to raw date if parsing fails
            normalized_date = raw_date
        
        # Extract unique email ID (Message-ID)
        email_id = email_message['Message-ID'] or f"no-id-{hash(str(email_message))}"
        
        # Get email body content with robust extraction
        body_content = ""
        
        if email_message.is_multipart():
            text_parts = []
            html_parts = []
            
            for part in email_message.walk():
                content_type = part.get_content_type()
                
                if content_type == "text/plain":
                    content = self.extract_content_from_part(part)
                    if content.strip():  # Only add non-empty content
                        text_parts.append(content)
                        
                elif content_type == "text/html":
                    content = self.extract_content_from_part(part)
                    if content.strip():  # Only add non-empty content
                        html_parts.append(content)
                        
            # Prefer text/plain, fallback to text/html
            if text_parts:
                body_content = "\n".join(text_parts)
            elif html_parts:
                body_content = "\n".join(html_parts)
            else:
                print("No text/plain or text/html parts found")
                
        else:
            # Single part email
            body_content = self.extract_content_from_part(email_message)
        
        # Clean raw message content
        raw_message = self.clean_raw_message(body_content)
        
        return {
            'from': sender,
            'subject': subject,
            'date': normalized_date,
            'email_id': email_id,
            'raw': raw_message,
            'body_content': body_content  # Keep original for amount extraction
        } 