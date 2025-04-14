import json
from typing import Dict, List, Any
import os

def validate_bcm(bcm: float) -> bool:
    """Validate BCM value."""
    return 0 < bcm <= 20  # Typical BCM range for flexographic printing

def load_saved_settings() -> List[Dict[str, Any]]:
    """Load saved settings from file."""
    try:
        if os.path.exists('saved_settings.json'):
            with open('saved_settings.json', 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_settings(settings: List[Dict[str, Any]]) -> None:
    """Save settings to file."""
    try:
        with open('saved_settings.json', 'w') as f:
            json.dump(settings, f)
    except Exception as e:
        print(f"Error saving settings: {str(e)}")

def get_help_text(field: str) -> str:
    """Return help text for different fields."""
    help_texts = {
        'substrate': "Het type materiaal waarop gedrukt wordt. Dit beïnvloedt de UV-absorptie.",
        'ink_type': "Het type inkt dat gebruikt wordt. UV-inkt heeft andere uithardingseisen.",
        'bcm': "BCM (Billion Cubic Microns) is het celvolume van de aniloxwals.",
        'rasterwals': "Het type rasterwals bepaalt de inktoverdracht. Een hogere transfer betekent meer inkt en dus meer UV-vermogen nodig.",
        'volume': "Het specifieke volume van de rasterwals dat de hoeveelheid inkt bepaalt die kan worden overgedragen.",
        'general': "CleverCuring helpt bij het bepalen van de optimale UV-uitharding instellingen voor flexografisch drukwerk."
    }
    return help_texts.get(field, "")
