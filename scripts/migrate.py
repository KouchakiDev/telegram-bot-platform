from __future__ import annotations

from importlib.resources import files

from alembic import command
from alembic.config import Config


def main() -> None:
    migrations_path = files("migrations")
    cfg = Config()
    cfg.set_main_option("script_location", str(migrations_path))
    command.upgrade(cfg, "head")


if __name__ == "__main__":
    main()
