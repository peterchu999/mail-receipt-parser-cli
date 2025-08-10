#!/usr/bin/env python3
"""
E-Receipt Parser CLI - Refactored Version
Clean orchestration using class-based architecture
"""

import email

# Import our refactored modules
from src.config.email_filters import EMAIL_FILTERS
from src.email.connector import EmailConnector
from src.email.filter import EmailFilter
from src.email.parser import EmailParser
from src.parser.receipt_parser import ReceiptParser
from src.storage.csv_exporter import CSVExporter
from src.utils.helpers import display_welcome_message, display_email_info, input_credentials


def process_emails_batch(mail, email_ids, email_parser, receipt_parser):
    """Process emails in batch and return structured data for CSV export."""
    email_records = []
    
    print(f"\n📊 Processing {len(email_ids)} emails for data extraction...")
    
    for i, email_id in enumerate(email_ids, 1):
        try:
            # Fetch email data
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            if status == 'OK':
                email_message = email.message_from_bytes(msg_data[0][1])
                
                # Extract email info
                email_info = email_parser.extract_email_info(email_message)
                
                # Parse receipt data (add total amount)
                receipt_data = receipt_parser.parse_receipt_data(email_info)
                
                email_records.append(receipt_data)
                
                # Display progress (keep existing display functionality)
                display_email_info(i, receipt_data)
                
        except Exception as e:
            print(f"{i:2d}. Error processing email: {e}")
            print(f"    {'-'*50}")
    
    return email_records

MAX_PROCESS_EMAILS = 1000

def main():
    """Main function orchestrating the email fetching process."""
    try:
        # Display welcome message
        display_welcome_message()
        
        # Initialize all components
        email_connector = EmailConnector()
        email_filter = EmailFilter(EMAIL_FILTERS)
        email_parser = EmailParser()
        receipt_parser = ReceiptParser()
        csv_exporter = CSVExporter()
        
        # Get user credentials
        email_address, password = input_credentials()
        
        # Connect to email server
        if not email_connector.connect(email_address, password):
            return
        
        mail = email_connector.get_connection()
        
        try:
            # Get filtered e-receipt emails
            filtered_emails = email_filter.get_filtered_emails(mail, MAX_PROCESS_EMAILS)
            
            # Process emails and save to CSV
            if filtered_emails:
                # Batch process emails for data extraction
                email_records = process_emails_batch(mail, filtered_emails, email_parser, receipt_parser)
                
                # Save to CSV
                if email_records:
                    csv_exporter.save_records(email_records)
                else:
                    print("\n⚠️  No valid email records extracted for CSV export")
            else:
                print("\n📭 No e-receipt emails found with current filters.")
            
            # Close connection
        except Exception as e:
            print(f"❌ Error in main process: {e}")
        finally:
            email_connector.disconnect()
        print("\n✅ Email processing completed!")
        
    except Exception as e:
        print(f"❌ Error in main process: {e}")


if __name__ == '__main__':
    main() 