# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Object Script Entities (OSE) module for the engine.
"""

from . import Entity
from .types import EntityScriptType

from typing import Any


def _script_defines(scriptobj: EntityScriptType, name: str) -> bool:
    """
    Check whether scriptobj itself defines `name`, rather than inheriting
    it from Entity. Since script classes are commonly subclasses of Entity
    (for typing convenience), a plain hasattr() check would also match
    Entity's own init/update/event, causing infinite recursion when they
    are dispatched.
    """

    func = getattr(scriptobj, name, None)
    return func is not None and func is not getattr(Entity, name, None)


class ObjectScriptEntity(Entity):
    def __new__(cls, *args: Any, scriptobj: EntityScriptType, **kwargs: Any) -> Any:
        kwargs["scriptfile"] = None
        entity = Entity(*args, **kwargs)

        entity.scriptfile_funcs = {
            "init": _script_defines(scriptobj, "init"),
            "update": _script_defines(scriptobj, "update"),
            "event": _script_defines(scriptobj, "event"),
        }

        setattr(entity, "scriptfile_module", scriptobj)  # noqa: B010

        return entity

    def __init__(self, *args: Any, scriptobj: EntityScriptType, **kwargs: Any) -> None: ...  # noqa: E704
