# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Object Script Entities (OSE) module for the engine.
"""

from . import Entity
from .types import EntityScriptType

from typing import Any


class ObjectScriptEntity(Entity):
    def __new__(cls, *args: Any, scriptobj: EntityScriptType, **kwargs: Any):
        kwargs["scriptfile"] = None
        entity = Entity(*args, **kwargs)

        entity.scriptfile_funcs = {
            "init": hasattr(scriptobj, "init"),
            "update": hasattr(scriptobj, "update"),
            "event": hasattr(scriptobj, "event")
        }

        setattr(entity, "scriptfile_module", scriptobj)  # noqa: B010

        return entity

    def __init__(self, *args, scriptobj, **kwargs):
        ...
