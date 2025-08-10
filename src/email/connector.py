import imaplib
import getpass


class EmailConnector:
    """Handles IMAP connections and authentication."""
    
    def __init__(self, host="imap.gmail.com", port=993, use_ssl=True):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.connection = None
    
    def connect(self, email_address, password):
        """Connect to email server and authenticate."""
        print("\nConnecting to email server...")
        
        try:
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.host, self.port)
            else:
                self.connection = imaplib.IMAP4(self.host, self.port)
            
            self.connection.login(email_address, password)
            print("✅ Successfully connected to email server!")
            return True
            
        except Exception as e:
            print(f"❌ Error connecting to email server: {e}")
            print("Make sure you're using an app password if using Gmail.")
            return False
    
    def disconnect(self):
        """Disconnect from email server."""
        if self.connection:
            try:
                self.connection.logout()
                print("✅ Disconnected from email server")
            except Exception as e:
                print(f"⚠️  Error disconnecting: {e}")
    
    def get_connection(self):
        """Get the current IMAP connection."""
        return self.connection