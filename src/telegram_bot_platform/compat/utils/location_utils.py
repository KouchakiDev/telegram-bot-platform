import requests
import logging
from typing import Dict, Optional
import sys
import pandas as pd
# Internal implementation note: legacy behavior is preserved during modernization.
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

# Internal implementation note: legacy behavior is preserved during modernization.
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_location_details(latitude: float, longitude: float) -> Optional[Dict[str, str]]:
    """Legacy-compatible behavior preserved for this callable."""
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&zoom=18&addressdetails=1"
    headers = {"User-Agent": "TelegramBot"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            # df = pd.DataFrame(address)
            print(address)
            return {
                "province": address.get("province") or address.get("state") or "Unknow",
                "city": address.get("city", address.get("town", address.get("village", "Unknow"))),
                "area": f"{address.get("neighbourhood", address.get("county", "Unknow"))},{address.get("road", address.get("county", "Unknow"))}"
            }
        else:
            logger.error(
                f"Failed to get location data. Status code: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching location details: {e}")
        return None


# Internal implementation note: legacy behavior is preserved during modernization.
if __name__ == "__main__":
    latitude, longitude = 35.6892, 51.3890  # Internal implementation note: legacy behavior is preserved during modernization.
    location = get_location_details(latitude, longitude)
    print(location)
