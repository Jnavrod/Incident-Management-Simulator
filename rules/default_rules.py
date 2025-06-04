from typing import Dict, Set

INCIDENT_TYPE_ROLE_RULES: Dict[str, Set[str]] = {
    "infrastructure": {"alice"},
    "application": {"bob"},
    "security": {"carol"},
}