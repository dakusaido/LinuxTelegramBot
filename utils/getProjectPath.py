import os
import asyncio

__all__ = ['get_project_path']


def get_project_path():
    path = os.path.dirname(os.path.abspath(__file__))[:-5]
    return path
