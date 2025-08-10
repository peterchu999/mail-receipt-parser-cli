# Email filtering configuration
# Try to load from YAML first, fallback to hardcoded values

from .config_manager import ConfigManager

# Initialize config manager
config_manager = ConfigManager()

# Try to load YAML config, fallback to hardcoded values
yaml_config = config_manager.get_email_filters()

if yaml_config is not None:
    EMAIL_FILTERS = yaml_config
    print("📋 Using YAML configuration")
else:
    # Fallback to hardcoded configuration
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
        
        'date_range_days': 10,  # Only process emails from last 10 days
        'max_emails': 1000
    }
    print("📋 Using fallback hardcoded configuration") 