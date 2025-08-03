#!/usr/bin/env python3
"""
E-Receipt Parser CLI
Simple hello world script to test basic setup
"""

import getpass
import imaplib
import email
import re
from email.header import decode_header
from datetime import datetime


def display_welcome_message():
    """Display welcome message and project status."""
    print("Hello World! E-Receipt Parser CLI is working!")
    print("Project structure is ready for development.")


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


def get_latest_emails(mail, max_emails=2):
    """Get the latest emails from the inbox."""
    # Select inbox
    mail.select('INBOX')
    
    # Search for all emails
    status, messages = mail.search(None, 'ALL')
    
    if status != 'OK':
        raise Exception("Failed to search emails")
    
    # Get the list of email IDs
    email_ids = messages[0].split()
    
    # Get the latest emails (or all if less than max_emails)
    latest_emails = email_ids[-max_emails:] if len(email_ids) > max_emails else email_ids
    
    print(f"\n📧 Found {len(latest_emails)} emails to fetch")
    return latest_emails


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


def extract_email_info(email_message):
    """Extract basic information from an email message."""
    # Extract subject
    subject = decode_header(email_message['subject'])[0][0]
    if isinstance(subject, bytes):
        subject = subject.decode('utf-8', errors='ignore')
    
    # Extract sender and date
    sender = email_message['from']
    date = email_message['date']
    
    # Get email body content
    body_content = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body_content = part.get_payload(decode=True)
                break
    else:
        body_content = email_message.get_payload(decode=True)
    
    # Extract total amount from body
    total_amount = extract_total_amount(body_content)
    print(total_amount)
    
    return {
        'subject': subject,
        'sender': sender,
        'date': date,
        'total_amount': total_amount
    }


def display_email_info(index, email_info):
    """Display formatted email information."""
    print(f"{index:2d}. From: {email_info['sender']}")
    print(f"    Subject: {email_info['subject']}")
    print(f"    Date: {email_info['date']}")
    
    # Display total amount if found
    if email_info.get('total_amount') is not None:
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


def main():
    """Main function orchestrating the email fetching process."""
    try:
        # Display welcome message
        display_welcome_message()
        
        # Get user credentials
        email_address, password = get_email_credentials()
        
        # Connect to email server
        mail = connect_to_imap_server(email_address, password)
        
        # Get latest emails
        latest_emails = get_latest_emails(mail)
        
        # Fetch and display emails
        fetch_and_display_emails(mail, latest_emails)
        
        # Close connection
        mail.logout()
        print("\n✅ Email fetching completed!")
        
    except Exception as e:
        print(f"❌ Error connecting to email server: {e}")
        print("Make sure you're using an app password if using Gmail.")


if __name__ == '__main__':
    main()
