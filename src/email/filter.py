import re
from datetime import datetime, timedelta


class EmailFilter:
    """Manages email filtering logic."""
    
    def __init__(self, config):
        self.config = config
        self.sender_domains = config['sender_domains']
        self.subject_patterns = config['subject_patterns']
        self.date_range_days = config['date_range_days']
    
    def filter_by_sender(self, mail):
        """Filter emails by sender domains using IMAP search."""
        # Calculate date range for filtering
        cutoff_date = datetime.now() - timedelta(days=self.date_range_days)
        date_str = cutoff_date.strftime("%d-%b-%Y")
        
        all_email_ids = set()
        
        print(f"\n🔍 Filtering emails by sender domains (since {date_str})...")
        
        for domain in self.sender_domains:
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
    
    def filter_by_subject(self, mail, email_ids):
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
                        for pattern in self.subject_patterns:
                            if re.search(pattern, subject, re.IGNORECASE):
                                filtered_emails.append(email_id)
                                print(f"  ✅ Match: {subject[:50]}...")
                                break
                                
            except Exception as e:
                print(f"  ⚠️  Error checking email {email_id}: {e}")
                continue
        
        return filtered_emails
    
    def get_filtered_emails(self, mail, max_emails=10):
        """Get filtered emails that are likely e-receipts."""
        # Select inbox
        mail.select('INBOX')
        
        # Step 1: Filter by sender domains
        sender_filtered_emails = self.filter_by_sender(mail)
        
        if not sender_filtered_emails:
            print("\n❌ No emails found from known e-wallet/payment domains")
            return []
        
        # Step 2: Filter by subject patterns
        subject_filtered_emails = self.filter_by_subject(mail, sender_filtered_emails)
        
        if not subject_filtered_emails:
            print("\n❌ No emails found matching receipt subject patterns")
            return []
        
        # Step 3: Limit to max_emails (get most recent)
        final_emails = subject_filtered_emails[-max_emails:] if len(subject_filtered_emails) > max_emails else subject_filtered_emails
        
        print(f"\n📧 Final result: {len(final_emails)} filtered e-receipt emails")
        print(f"   (from {len(sender_filtered_emails)} sender matches, {len(subject_filtered_emails)} subject matches)")
        
        return final_emails 