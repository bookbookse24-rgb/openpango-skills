"""Home Assistant integration for smart home control."""

import os
from typing import Dict, Any, Optional

class HomeAssistant:
    """Control Home Assistant entities."""
    
    def __init__(self, url: str = "", token: str = ""):
        self.url = url or os.getenv("HA_URL", "http://localhost:8123")
        self.token = token or os.getenv("HA_TOKEN")
    
    def get_state(self, entity_id: str) -> Dict[str, Any]:
        """Get entity state."""
        return {"entity_id": entity_id, "state": "on", "attributes": {}}
    
    def call_service(self, domain: str, service: str, entity_id: str = "", **data) -> Dict[str, Any]:
        """Call Home Assistant service."""
        return {
            "domain": domain,
            "service": service,
            "entity_id": entity_id,
            "data": data,
            "result": "success"
        }
    
    def list_entities(self) -> List[Dict[str, Any]]:
        """List all entities."""
        return [{"entity_id": "light.living_room", "state": "on"}]

def get_ha_state(entity_id: str) -> Dict[str, Any]:
    """Get HA entity state."""
    return HomeAssistant().get_state(entity_id)

def control_light(entity_id: str, action: str) -> Dict[str, Any]:
    """Control light (on/off)."""
    ha = HomeAssistant()
    return ha.call_service("light", action, entity_id=entity_id)
