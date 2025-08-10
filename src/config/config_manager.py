import yaml
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages configuration loading from YAML files with fallback support."""
    
    def __init__(self, yaml_path: str = "config/email_filters.yaml"):
        self.yaml_path = yaml_path
        self.config = None
    
    def load_yaml_config(self) -> Optional[Dict[str, Any]]:
        """Load YAML configuration and convert to EMAIL_FILTERS format."""
        try:
            if not os.path.exists(self.yaml_path):
                print(f"⚠️  YAML config file not found: {self.yaml_path}")
                return None
            
            with open(self.yaml_path, 'r', encoding='utf-8') as file:
                yaml_data = yaml.safe_load(file)
            
            if not yaml_data:
                print("⚠️  YAML config file is empty")
                return None
            
            # Convert to EMAIL_FILTERS format
            config = {
                'sender_domains': yaml_data.get('sender_domains', []),
                'subject_patterns': yaml_data.get('subject_patterns', []),
                'date_range_days': yaml_data.get('settings', {}).get('date_range_days', 10),
                'max_emails': yaml_data.get('settings', {}).get('max_emails', 1000)
            }
            
            # Validate required fields
            if not config['sender_domains']:
                print("⚠️  No sender domains found in YAML config")
                return None
            
            if not config['subject_patterns']:
                print("⚠️  No subject patterns found in YAML config")
                return None
            
            print(f"✅ Successfully loaded YAML config from {self.yaml_path}")
            print(f"   - {len(config['sender_domains'])} sender domains")
            print(f"   - {len(config['subject_patterns'])} subject patterns")
            print(f"   - Date range: {config['date_range_days']} days")
            print(f"   - Max emails: {config['max_emails']}")
            
            return config
            
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML config: {e}")
            return None
        except Exception as e:
            print(f"❌ Error loading YAML config: {e}")
            return None
    
    def get_email_filters(self) -> Dict[str, Any]:
        """Get EMAIL_FILTERS configuration (YAML-loaded or fallback)."""
        if self.config is None:
            self.config = self.load_yaml_config()
        
        return self.config 