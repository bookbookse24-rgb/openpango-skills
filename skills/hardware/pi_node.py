"""Raspberry Pi dedicated hardware node blueprint."""
import os, platform, subprocess
from typing import Dict, Any, List

class PiNode:
    """Manage OpenPango on Raspberry Pi hardware."""

    def get_info(self) -> Dict[str, Any]:
        info = {
            "platform": platform.machine(),
            "system": platform.system(),
            "is_pi": os.path.exists("/proc/device-tree/model")
        }
        if info["is_pi"]:
            try:
                info["model"] = Path("/proc/device-tree/model").read_text()
            except:
                pass
        return info

    def get_temperature(self) -> Dict[str, Any]:
        try:
            result = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True)
            temp = float(result.stdout.replace("temp=", "").replace("'C\n", ""))
            return {"temp_c": temp, "temp_f": temp * 9/5 + 32, "status": "ok" if temp < 80 else "hot"}
        except:
            return {"error": "vcgencmd not available (not a Pi or no GPU tools)"}

    def get_resources(self) -> Dict[str, Any]:
        try:
            import psutil
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {"total": psutil.virtual_memory().total, "used": psutil.virtual_memory().used, "percent": psutil.virtual_memory().percent},
                "disk": {"total": psutil.disk_usage("/").total, "used": psutil.disk_usage("/").used, "percent": psutil.disk_usage("/").percent}
            }
        except ImportError:
            return {"error": "psutil not installed. Run: pip install psutil"}

    def install_openclaw(self) -> Dict[str, Any]:
        """Setup script for Pi."""
        steps = [
            "curl -fsSL https://openclaw.ai/install.sh | bash",
            "openclaw configure",
            "openclaw gateway start",
            "openclaw cron add --schedule 'every 1h' --task 'health check'"
        ]
        return {"setup_steps": steps, "docs": "https://docs.openclaw.ai/deploy/raspberry-pi"}
