#!/usr/bin/env python3
"""
E-Receipt Parser CLI
Simple hello world script to test basic setup
"""

import getpass
import imaplib
import email
import re
import csv
import html
import os
from email.header import decode_header
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime


# Email filtering configuration
EMAIL_FILTERS = {
    'sender_domains': [
        # E-wallets & Services
        
        'shopee.co.id', 'gojek.com', 'ovo.id', 'dana.id', 'grab.com',
        'tokopedia.com', 'bukalapak.com', 'blibli.com',
        
        # Banks
        'bca.co.id', 'mandiri.co.id', 'bni.co.id', 'bri.co.id', 'seabank.co.id',
        'cimb.co.id', 'danamon.co.id',
        
        # Payment Gateways
        'midtrans.com', 'xendit.co', 'doku.com',
        
        # Additional common notification domains
        'noreply@shopee.co.id', 'notification@gojek.com', 'noreply@grab.com',
    ],
    
    'subject_patterns': [
        # English patterns
        r'.*receipt.*', r'.*transaction.*', r'.*payment.*',
        r'.*invoice.*', r'.*billing.*', r'.*purchase.*',
        r'.*confirmation.*', r'.*statement.*',
        
        # Indonesian patterns  
        r'.*bukti.*', r'.*transaksi.*', r'.*pembayaran.*',
        r'.*struk.*', r'.*tagihan.*', r'.*pembelian.*',
        r'.*konfirmasi.*', r'.*laporan.*',
        
        # Specific wallet patterns
        r'.*shopee.*pay.*', r'.*gopay.*', r'.*ovo.*payment.*',
        r'.*dana.*transfer.*', r'.*linkaja.*'
    ],
    
    'date_range_days': 10  # Only process emails from last 30 days
}


def display_welcome_message():
    """Display welcome message and project status."""
    print("🧾 E-Receipt Parser CLI v2.0 - Smart Email Filtering!")
    print("📧 Scanning emails from Indonesian e-wallets and payment services...")
    print(f"🔍 Configured to filter {len(EMAIL_FILTERS['sender_domains'])} sender domains")
    print(f"📝 Using {len(EMAIL_FILTERS['subject_patterns'])} subject patterns")
    print(f"📅 Processing emails from last {EMAIL_FILTERS['date_range_days']} days")


def get_email_credentials():
    """Get email credentials from user input."""
    print("\nEnter your email credentials:")
    email_address = input("Email: ").strip()
    password = getpass.getpass("Password: ")
    
    # Print the credentials (for testing purposes)
    print(f"\nEmail: {email_address}")
    print(f"Password: {'*' * len(password)} (hidden for security)")
    print(f"Password length: {len(password)} characters")
    
    return email_address, password


def connect_to_imap_server(email_address, password):
    """Connect to IMAP server and return mail connection."""
    print("\nConnecting to email server...")
    
    # For Gmail
    imap_server = "imap.gmail.com"
    imap_port = 993
    
    # Connect to server
    mail = imaplib.IMAP4_SSL(imap_server, imap_port)
    mail.login(email_address, password)
    
    print("✅ Successfully connected to email server!")
    
    return mail


def filter_emails_by_sender(mail):
    """Filter emails by sender domains using IMAP search."""
    # Calculate date range for filtering
    cutoff_date = datetime.now() - timedelta(days=EMAIL_FILTERS['date_range_days'])
    date_str = cutoff_date.strftime("%d-%b-%Y")
    
    all_email_ids = set()
    
    print(f"\n🔍 Filtering emails by sender domains (since {date_str})...")
    
    for domain in EMAIL_FILTERS['sender_domains']:
        try:
            
            # Search for emails from this domain within date range
            search_criteria = f'(FROM "{domain}" SINCE "{date_str}")'
            status, messages = mail.search(None, search_criteria)
            
            if status == 'OK' and messages[0]:
                domain_emails = messages[0].split()
                all_email_ids.update(domain_emails)
                if domain_emails:
                    print(f"  ✅ Found {len(domain_emails)} emails from {domain}")
            
        except Exception as e:
            print(f"  ⚠️  Error searching {domain}: {e}")
            continue
    
    return list(all_email_ids)


def filter_emails_by_subject(mail, email_ids):
    """Filter emails by subject patterns."""
    if not email_ids:
        return []
    
    filtered_emails = []
    print(f"\n🔍 Filtering {len(email_ids)} emails by subject patterns...")
    
    for email_id in email_ids:
        try:
            # Fetch only the header for subject checking
            status, msg_data = mail.fetch(email_id, '(BODY[HEADER.FIELDS (SUBJECT)])')
            
            if status == 'OK':
                header_data = msg_data[0][1].decode('utf-8', errors='ignore')
                
                # Extract subject
                subject_match = re.search(r'Subject: (.+)', header_data, re.IGNORECASE)
                if subject_match:
                    subject = subject_match.group(1).strip()
                    
                    # Check against patterns
                    for pattern in EMAIL_FILTERS['subject_patterns']:
                        if re.search(pattern, subject, re.IGNORECASE):
                            filtered_emails.append(email_id)
                            print(f"  ✅ Match: {subject[:50]}...")
                            break
                            
        except Exception as e:
            print(f"  ⚠️  Error checking email {email_id}: {e}")
            continue
    
    return filtered_emails


def get_filtered_emails(mail, max_emails=10):
    """Get filtered emails that are likely e-receipts."""
    # Select inbox
    mail.select('INBOX')
    
    # Step 1: Filter by sender domains
    sender_filtered_emails = filter_emails_by_sender(mail)
    
    if not sender_filtered_emails:
        print("\n❌ No emails found from known e-wallet/payment domains")
        return []
    
    # Step 2: Filter by subject patterns
    subject_filtered_emails = filter_emails_by_subject(mail, sender_filtered_emails)
    
    if not subject_filtered_emails:
        print("\n❌ No emails found matching receipt subject patterns")
        return []
    
    # Step 3: Limit to max_emails (get most recent)
    final_emails = subject_filtered_emails[-max_emails:] if len(subject_filtered_emails) > max_emails else subject_filtered_emails
    
    print(f"\n📧 Final result: {len(final_emails)} filtered e-receipt emails")
    print(f"   (from {len(sender_filtered_emails)} sender matches, {len(subject_filtered_emails)} subject matches)")
    
    return final_emails


def clean_raw_message(body_content):
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


def extract_content_from_email_part(part):
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


def extract_email_info(email_message):
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
                content = extract_content_from_email_part(part)
                if content.strip():  # Only add non-empty content
                    text_parts.append(content)
                    
            elif content_type == "text/html":
                content = extract_content_from_email_part(part)
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
        body_content = extract_content_from_email_part(email_message)
    
    # Clean raw message content
    raw_message = clean_raw_message(body_content)
    
    # Extract total amount from body
    total_amount = extract_total_amount(body_content)
    
    return {
        'from': sender,
        'subject': subject,
        'date': normalized_date,
        'total_amount': total_amount if total_amount is not None else 0.0,
        'email_id': email_id,
        'raw': raw_message
    }



def extract_total_amount(text):
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


def display_email_info(index, email_info):
    """Display formatted email information."""
    print(f"{index:2d}. From: {email_info['from']}")
    print(f"    Subject: {email_info['subject']}")
    print(f"    Date: {email_info['date']}")
    print(f"    Email ID: {email_info['email_id'][:50]}...")  # Truncate long IDs
    
    # Display total amount if found
    if email_info.get('total_amount') and email_info['total_amount'] > 0:
        print(f"    💰 Total Amount: Rp {email_info['total_amount']:,.0f}")
    else:
        print(f"    💰 Total Amount: Not found")
    
    print(f"    {'-'*50}")


def fetch_and_display_emails(mail, email_ids):
    """Fetch and display email information."""
    for i, email_id in enumerate(email_ids, 1):
        try:
            # Fetch email data
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            if status == 'OK':
                email_message = email.message_from_bytes(msg_data[0][1])
                email_info = extract_email_info(email_message)
                display_email_info(i, email_info)
                
                # print(email_message)  # Uncomment for debugging
                
        except Exception as e:
            print(f"{i:2d}. Error fetching email: {e}")
            print(f"    {'-'*50}")


def save_emails_to_csv(email_records, filename='receipts.csv'):
    """Save email records to CSV file with proper headers."""
    if not email_records:
        print("⚠️  No email records to save")
        return False
    
    # Define CSV headers in the correct order
    fieldnames = ['from', 'subject', 'date', 'total_amount', 'email_id', 'raw']
    
    try:
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header only if file is new
            if not file_exists:
                writer.writeheader()
                print(f"📄 Created new CSV file: {filename}")
            
            # Write email records
            for record in email_records:
                # Ensure all required fields are present
                csv_record = {field: record.get(field, '') for field in fieldnames}
                writer.writerow(csv_record)
            
            print(f"💾 Successfully saved {len(email_records)} email records to {filename}")
            return True
            
    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")
        return False


def process_emails_batch(mail, email_ids):
    """Process emails in batch and return structured data for CSV export."""
    email_records = []
    
    print(f"\n📊 Processing {len(email_ids)} emails for data extraction...")
    
    for i, email_id in enumerate(email_ids, 1):
        try:
            # Fetch email data
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            if status == 'OK':
                email_message = email.message_from_bytes(msg_data[0][1])
                email_info = extract_email_info(email_message)
                email_records.append(email_info)
                
                # Display progress (keep existing display functionality)
                display_email_info(i, email_info)
                
        except Exception as e:
            print(f"{i:2d}. Error processing email: {e}")
            print(f"    {'-'*50}")
    
    return email_records


def main():
    """Main function orchestrating the email fetching process."""
    try:
        # Display welcome message
        display_welcome_message()
        
        # Get user credentials
        email_address, password = get_email_credentials()
        # Connect to email server
        mail = connect_to_imap_server(email_address, password)
        
        # Get filtered e-receipt emails
        filtered_emails = get_filtered_emails(mail, 1000)
        
        # Process emails and save to CSV
        if filtered_emails:
            # Batch process emails for data extraction
            email_records = process_emails_batch(mail, filtered_emails)
            
            # Save to CSV
            if email_records:
                save_emails_to_csv(email_records)
            else:
                print("\n⚠️  No valid email records extracted for CSV export")
        else:
            print("\n📭 No e-receipt emails found with current filters.")
        
        # Close connection
        mail.logout()
        print("\n✅ Email fetching completed!")
        
    except Exception as e:
        print(f"❌ Error connecting to email server: {e}")
        print("Make sure you're using an app password if using Gmail.")


if __name__ == '__main__':
    main()
