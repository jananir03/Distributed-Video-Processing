"""Consistent, simple logging configuration for all services."""
import logging
import os


def configure_logging(service_name: str) -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format=f"%(asctime)s %(levelname)s [{service_name}] %(name)s: %(message)s",
        force=True,
    )
