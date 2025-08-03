# E-Receipt Parser CLI

A command-line tool to automatically extract and track expenses from e-receipt emails sent by Indonesian e-wallets (ShopeePay, GoPay, OVO, etc.).

## 🎯 Problem Statement

Managing expenses from multiple e-wallets is tedious when done manually. Every transaction generates an e-receipt email that needs to be manually entered into finance tracking apps, leading to:

- Time-consuming manual data entry
- Potential errors and missed transactions
- Inconsistent expense tracking

## App Password

to use this cli parser you need app password instead of your email passwordm to create an app password, you could visit https://myaccount.google.com/apppasswords. Make sure 2FA already enabled

## ✨ Features

- **📧 Email Integration**: Connects to email inbox via IMAP to fetch e-receipts
- **🔍 Smart Filtering**: Automatically identifies unprocessed e-receipt emails
- **📊 Data Extraction**: Parses transaction details (amount, merchant, date, category)
- **💾 Local Storage**: Stores data in SQLite database for offline access
- **🔄 Deduplication**: Uses Message-ID to prevent double-processing

- **🎯 General Parser**: Pattern matching for various receipt formats
- **⚡ CLI Interface**: Simple command-line interface for automation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Email Inbox   │───▶│  E-Receipt      │───▶│  SQLite         │
│   (IMAP)        │    │  Parser CLI     │    │  Database       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

1. **Email Connector**: IMAP client for email access
2. **Receipt Filter**: Identifies e-receipt emails
3. **Parser Engine**: Wallet-specific parsing logic
4. **Database Manager**: SQLite operations
5. **CLI Interface**: User interaction layer

## 📋 Database Schema

### `receipts` Table

- `id` (INTEGER, PRIMARY KEY): Auto-incrementing ID
- `message_id` (TEXT, UNIQUE): Email Message-ID for deduplication
- `processed_at` (DATETIME): Timestamp when email was processed
- `email_subject` (TEXT): Original email subject
- `email_date` (DATETIME): Email received date
- `transaction_date` (DATETIME): Transaction timestamp (extracted from email)
- `amount` (DECIMAL): Transaction amount
- `currency` (TEXT): Currency code (default: IDR)
- `merchant` (TEXT): Merchant/store name
- `raw_data` (TEXT): Original parsed data (JSON)

## 🛠️ Supported Receipt Types

- **E-Wallet Receipts**: Various Indonesian e-wallets and payment apps
- **Bank Transaction Receipts**: Various Indonesian banks
- **Payment Gateway Receipts**: Midtrans, Xendit, etc.
- **General Transaction Emails**: Any email containing transaction details

The parser uses general pattern matching to extract transaction information from various receipt formats.

## 🚀 Installation

```bash
# Clone the repository
git clone <repository-url>
cd mail-receipt-parser-cli

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config.example.yaml config.yaml
# Edit config.yaml with your email server settings
```

## ⚙️ Configuration

Create a `config.yaml` file for basic settings:

```yaml
email:
  host: imap.gmail.com
  port: 993
  use_ssl: true

database:
  path: ./receipts.db

parsing:
  search_terms:
    - "e-receipt"
    - "transaction receipt"
    - "payment confirmation"
```

**Security Note**: Email credentials (username/password) are prompted interactively during CLI execution and are not stored in configuration files for security reasons.

## 📖 Usage

### Basic Commands

```bash
# Process new e-receipts
python main.py process

# List all receipts
python main.py list



# Show statistics
python main.py stats

# Check email connection
python main.py test-connection
```

### Advanced Usage

```bash
# Dry run (show what would be processed)
python main.py process --dry-run



# Show processing statistics
python main.py stats
```

## 🔧 Development

### Project Structure

```
mail-receipt-parser-cli/
├── src/
│   ├── __init__.py
│   ├── main.py              # CLI entry point
│   ├── email/
│   │   ├── __init__.py
│   │   ├── connector.py     # IMAP connection
│   │   └── filter.py        # Email filtering
│   ├── parser/
│   │   ├── __init__.py
│   │   └── receipt_parser.py # General receipt parser
│   ├── database/
│   │   ├── __init__.py
│   │   └── manager.py       # Database operations
│   └── utils/
│       ├── __init__.py
│       └── helpers.py       # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   └── test_database.py
├── config.yaml              # Configuration file
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Extending the Parser

The general receipt parser uses pattern matching to extract transaction information. To improve parsing for specific receipt formats:

1. Add new regex patterns in `src/parser/receipt_parser.py`
2. Update the parsing logic to handle new formats
3. Test with sample emails

Example:

```python
# Add new patterns for specific receipt types
PATTERNS = {
    'amount': [
        r'Rp\s*([\d,]+\.?\d*)',
        r'IDR\s*([\d,]+\.?\d*)',
        # Add more patterns as needed
    ],
    'merchant': [
        r'Merchant:\s*(.+)',
        r'Store:\s*(.+)',
        # Add more patterns as needed
    ]
}
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_parser.py

# Run with coverage
python -m pytest --cov=src tests/
```

## 📝 License

[Add your chosen license here]

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: General questions and discussions in GitHub Discussions

## 🔮 Roadmap

- [ ] Webhook support for real-time processing
- [ ] REST API for integration with other apps
- [ ] Machine learning for better parsing accuracy
- [ ] Mobile app companion
- [ ] Multi-language support
- [ ] Cloud sync options
- [ ] Advanced analytics and reporting

---

**Note**: This tool is designed for personal use and local-first architecture. Always ensure you comply with your email provider's terms of service and data privacy regulations.
