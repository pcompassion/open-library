#!/usr/bin/env python3

from pathlib import Path
import types


def get_module_directory(module: types.ModuleType) -> Path:
    """Returns the directory of a given module.
    Example usage:
    import my_projroot  # replace with your actual module
    project_root = get_module_directory(my_projroot)
    print(project_root)
    """
    # Ensure the module has a __file__ attribute
    if not hasattr(module, "__file__"):
        raise ValueError("Module does not have a '__file__' attribute.")

    # Get the path to the module's file (typically the __init__.py for a package)
    module_path = Path(module.__file__)

    # Return the directory containing the module
    return module_path.parent
