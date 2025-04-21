import os
import yaml

# Default configuration
config = {
    # General settings
    "general": {
        "scan_interval": 30,  # minutes
        "log_level": "INFO",
        "database_path": "huizenzoeker.db"
    },
    
    # Filter settings
    "filter": {
        "min_price": 100000,
        "max_price": 225000,
        "min_area": 0,
        "cities": [],
        "property_types": []
    },
    
    # Telegram settings
    "telegram": {
        "token": "8169156824:AAG0Nz-OrByEWWjaCaDw6FaLVMCh3_lgnaA",
        "chat_id": "",
        "notify_new": True,
        "notify_updated": True,
        "notify_removed": True,
        "send_summary": True
    },
    
    # Website settings
    "websites": {
        "klipenvw": True,
        "bijdevaate": True,
        "ooms": True,
        "vbrmakelaars": True,
        "ruimzicht": True,
        "visiemakelaardij": True,
        "voornemakelaars": True,
        "marquis": True,
        "rozenburgmakelaardij": True,
        "deltamakelaardij": True,
        "dehuizenbemiddelaar": True,
        "kolpavanderhoek": True,
        "rijnmondmakelaars": True,
        "woonvoorn": True,
        "boogerman": True
    },
    
    # GUI settings
    "gui": {
        "enabled": True,
        "host": "0.0.0.0",
        "port": 5000,
        "debug": False
    }
}

# Save configuration to file
with open('config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print("Configuration file created: config.yaml")
