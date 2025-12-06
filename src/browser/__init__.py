"""Browser module"""
from .driver import create_driver, create_wait
from .navigator import Navigator

__all__ = ['create_driver', 'create_wait', 'Navigator']
