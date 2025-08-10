import csv
import os


class CSVExporter:
    """Handles data persistence to CSV."""
    
    def __init__(self, filename='receipts.csv'):
        self.filename = filename
    
    def save_records(self, records):
        """Save email records to CSV file with proper headers."""
        if not records:
            print("⚠️  No email records to save")
            return False
        
        # Define CSV headers in the correct order
        fieldnames = ['from', 'subject', 'date', 'total_amount', 'email_id', 'raw']
        
        try:
            # Check if file exists to determine if we need headers
            file_exists = os.path.exists(self.filename)
            
            with open(self.filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header only if file is new
                if not file_exists:
                    writer.writeheader()
                    print(f"📄 Created new CSV file: {self.filename}")
                
                # Write email records
                for record in records:
                    # Ensure all required fields are present
                    csv_record = {field: record.get(field, '') for field in fieldnames}
                    writer.writerow(csv_record)
                
                print(f"💾 Successfully saved {len(records)} email records to {self.filename}")
                return True
                
        except Exception as e:
            print(f"❌ Error saving to CSV: {e}")
            return False
    
    def append_records(self, records):
        """Alias for save_records for consistency."""
        return self.save_records(records) 