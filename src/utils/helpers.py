import getpass

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


def display_welcome_message():
    """Display welcome message and project status."""
    print("🧾 E-Receipt Parser CLI v2.0 - Smart Email Filtering!")
    print("📧 Scanning emails from Indonesian e-wallets and payment services...")
    print("🔍 Configured to filter multiple sender domains")
    print("📝 Using multiple subject patterns")
    print("📅 Processing emails from last 10 days") 


def input_credentials():
    """Get email credentials from user input."""
    print("\nEnter your email credentials:")
    email_address = input("Email: ").strip()
    password = getpass.getpass("Password: ")
    
    # Print the credentials (for testing purposes)
    print(f"\nEmail: {email_address}")
    print(f"Password: {'*' * len(password)} (hidden for security)")
    print(f"Password length: {len(password)} characters")
    
    return email_address, password 