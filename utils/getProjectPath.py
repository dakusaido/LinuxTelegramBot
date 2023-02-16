import os

__all__ = ['get_project_path']


def get_project_path():
    return os.path.dirname(os.path.abspath(__file__))[:-5]
