"""skill_loader.py – discover and register skills dynamically with configurable package path and structured logging."""

import importlib
import pkgutil
import os
from typing import Callable, Dict

# Global registry mapping skill name to callable that accepts a dict and returns a dict
_registry: Dict[str, Callable[[dict], dict]] = {}

def _import_module(module_name: str):
    """Safely import a module; raise ImportError with context on failure."""
    try:
        return importlib.import_module(module_name)
    except Exception as exc:
        raise ImportError(f"Failed to import skill module '{module_name}': {exc}") from exc

def discover_skills(package_path: str = os.getenv("SKILL_DIR", "skills")) -> None:
    """
    Populate the global registry by scanning ``package_path`` for modules exposing a
    ``run`` function or a ``Skill`` class with an ``execute`` method.
    Emits structured log events via ``log_skill_event``.
    """
    import logging_config  # local import to avoid circular dependencies
    logging_config.log_skill_event("discovery_start", package=package_path)

    # Compatibility fix for pkgutil.iter_modules
    for _, mod_name, is_pkg in pkgutil.iter_modules([package_path]):
        if is_pkg:
            continue
        try:
            module = _import_module(f"{package_path}.{mod_name}")
        except ImportError as e:
            logging_config.log_skill_event("import_error", module=mod_name, error=str(e))
            continue

        module_name_lower = mod_name.lower()
        registered = False
        # Prefer a function named `run`; fall back to a class named `Skill` with an `execute` method
        if hasattr(module, "run") and callable(module.run):
            _registry[mod_name] = module.run
            registered = True
        elif hasattr(module, "Skill") and issubclass(getattr(module, "Skill"), object):
            cls = getattr(module, "Skill")
            if hasattr(cls, "execute") and callable(cls.execute):
                _registry[mod_name] = lambda payload, c=cls: c().execute(payload)
                registered = True

        if registered:
            logging_config.log_skill_event("skill_registered", name=mod_name, package=package_path)
        else:
            logging_config.log_skill_event("no_entry_point", name=mod_name, package=package_path)

def get_skill(name: str) -> Callable[[dict], dict]:
    """Retrieve the callable for *name*; raise KeyError if not found."""
    try:
        return _registry[name]
    except KeyError:
        raise KeyError(f"Skill '{name}' not found. Available skills: {list(_registry.keys())}") from None

def list_skills() -> list:
    return list(_registry.keys())