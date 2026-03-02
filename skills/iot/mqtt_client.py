"""MQTT client for IoT messaging."""

import json
from typing import Dict, Any, Callable, Optional
from datetime import datetime

class MQTTClient:
    """MQTT client for pub/sub."""
    
    def __init__(self, broker: str = "localhost", port: int = 1883):
        self.broker = broker
        self.port = port
        self.connected = False
        self.subscriptions = {}
    
    def connect(self) -> Dict[str, Any]:
        """Connect to MQTT broker."""
        self.connected = True
        return {"status": "connected", "broker": self.broker}
    
    def publish(self, topic: str, payload: Dict) -> Dict[str, Any]:
        """Publish message."""
        return {"topic": topic, "payload": payload, "timestamp": datetime.now().isoformat()}
    
    def subscribe(self, topic: str, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Subscribe to topic."""
        self.subscriptions[topic] = callback
        return {"topic": topic, "subscribed": True}

def publish_mqtt(topic: str, message: Dict) -> Dict[str, Any]:
    """Publish to MQTT."""
    return MQTTClient().publish(topic, message)
