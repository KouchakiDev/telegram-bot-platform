#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Legacy-compatible behavior preserved for this callable."""

import logging
from typing import List, Dict, Union, Optional

from telegram_bot_platform.compat.utils.database_manager import DatabaseManager
from telegram_bot_platform.compat.config.settings import DB_LOCATIONS
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger

log = CustomLogger("LocationHandler")


class LocationHandler:
    def __init__(self):
        """Legacy-compatible behavior preserved for this callable."""
        self.db_manager = DatabaseManager("sqlite", DB_LOCATIONS)

    def get_all_provinces(self) -> List[str]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            query = "SELECT name FROM provinces ORDER BY name"
            rows = self.db_manager.fetch_data(query)
            return [row[0] for row in rows] if rows else []
        except Exception as e:
            log.error(f"خطا در دریافت استان‌ها: {e}")
            return []

    def get_cities_by_province(self, province_name: str) -> List[str]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            query = """
                SELECT c.name
                FROM cities c
                JOIN provinces p ON c.province_id = p.id
                WHERE p.name = ?
                ORDER BY c.name
            """
            rows = self.db_manager.fetch_data(query, (province_name,))
            return [row[0] for row in rows] if rows else []
        except Exception as e:
            log.error(f"خطا در دریافت شهرهای استان «{province_name}»: {e}")
            return []

    def get_all_cities(self, as_dict: bool = True) -> Union[Dict[str, List[str]], List[str]]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            query = """
                SELECT p.name AS province, c.name AS city
                FROM provinces p
                JOIN cities c ON c.province_id = p.id
                ORDER BY p.name, c.name
            """
            rows = self.db_manager.fetch_data(query)
            if not rows:
                return {} if as_dict else []

            if as_dict:
                result: Dict[str, List[str]] = {}
                for province, city in rows:
                    result.setdefault(province, []).append(city)
                return result
            else:
                return [city for _, city in rows]
        except Exception as e:
            log.error(f"خطا در دریافت همه شهرها: {e}")
            return {} if as_dict else []

    def get_province_by_city(self, city_name: str) -> Optional[str]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            query = """
                SELECT p.name
                FROM provinces p
                JOIN cities c ON c.province_id = p.id
                WHERE c.name = ?
            """
            rows = self.db_manager.fetch_data(query, (city_name,))
            return rows[0][0] if rows else None
        except Exception as e:
            log.error(f"خطا در دریافت استان برای شهر «{city_name}»: {e}")
            return None

    def get_regions_by_city(self, city_name: str) -> List[str]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            query = """
                SELECT n.name
                FROM neighborhoods n
                JOIN cities c ON n.city_id = c.id
                WHERE c.name = ?
                ORDER BY n.name
            """
            rows = self.db_manager.fetch_data(query, (city_name,))
            return [row[0] for row in rows] if rows else []
        except Exception as e:
            log.error(f"خطا در دریافت مناطق برای شهر «{city_name}»: {e}")
            return []

    def get_city_slug_map(self) -> Dict[str, str]:
        """Legacy-compatible behavior preserved for this callable."""
        try:
            query = "SELECT name, slug FROM cities ORDER BY name"
            rows = self.db_manager.fetch_data(query)
            return {name: slug for name, slug in rows} if rows else {}
        except Exception as e:
            log.error(f"خطا در دریافت نگاشت slug شهرها: {e}")
            return {}

