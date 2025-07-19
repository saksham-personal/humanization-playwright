# humanization-playwright/__init__.py
__version__ = "0.1.0"

from .core import Humanization, HumanizationConfig

__all__ = [
    "Humanization",
    "HumanizationConfig",
]

from loguru import logger
logger.add("humanization.log", rotation="100 MB")