#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import inspect
import logging
from telegram_bot_platform.compat.config.settings import BUTTONS

# Internal implementation note: legacy behavior is preserved during modernization.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(stream_handler)


class SmartSelector:
    """Legacy-compatible behavior preserved for this callable."""

    def __init__(self, main_instance):
        self.main_instance = main_instance
        logger.debug(
            f"SmartSelector initialized with main_instance of type {type(main_instance).__name__}")

    def _method_matches_input(self, method, user_input):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            user_input2 = ""
            for key, value in BUTTONS.items():
                if value == user_input:
                    user_input2 = f'BUTTONS["{key}"]'
                    logger.debug(
                        f"Mapped user_input {user_input!r} to {user_input2}")
                    break

            src = inspect.getsource(method)
        except (OSError, TypeError) as e:
            logger.error(f"Error reading source of method {method}: {e}")
            return False

        checks = [f"'{user_input}'", f'"{user_input}"']
        if user_input2:
            checks.append(f"'{user_input2}'")
            checks.append(f'"{user_input2}"')

        logger.debug(f"Conditions to check in {method.__qualname__}: {checks}")

        for line in src.splitlines():
            stripped = line.strip()
            if stripped.startswith('if ') or stripped.startswith('elif '):
                logger.debug(
                    f"Inspecting conditional line in {method.__qualname__}: {stripped}")
                if any(check in stripped for check in checks):
                    logger.debug(
                        f"Match found in {method.__qualname__} for input {user_input!r}")
                    return True

        logger.debug(f"No matching condition found in {method.__qualname__}")
        return False

    def _safe_get_attrs(self, instance):
        """Legacy-compatible behavior preserved for this callable."""
        try:
            return vars(instance).items()
        except TypeError:
            return []

    def _search_recursive(self, instance, user_input, visited, depth=0, max_depth=10):
        """Legacy-compatible behavior preserved for this callable."""
        if depth > max_depth:
            logger.warning(
                f"Maximum recursion depth {max_depth} reached at instance {type(instance).__name__}")
            return None

        if id(instance) in visited:
            return None
        visited.add(id(instance))

        for name, member in inspect.getmembers(instance, inspect.ismethod):
            if name.endswith('_selection'):
                logger.debug(
                    f"Checking method {member.__qualname__} for input {user_input!r}")
                if self._method_matches_input(member, user_input):
                    logger.info(
                        f"Matching method found: {member.__qualname__}")
                    return member

        for attr_name, attr_value in self._safe_get_attrs(instance):
            if hasattr(attr_value, '__class__'):
                logger.debug(
                    f"Recursively checking nested instance: {attr_name} ({type(attr_value).__name__})")
                result = self._search_recursive(
                    attr_value, user_input, visited, depth + 1, max_depth)
                if result:
                    return result

        return None

    def find_matching_method(self, user_input):
        logger.debug(
            f"Searching for methods ending with '_selection' matching input {user_input!r}")
        return self._search_recursive(self.main_instance, user_input, set())
