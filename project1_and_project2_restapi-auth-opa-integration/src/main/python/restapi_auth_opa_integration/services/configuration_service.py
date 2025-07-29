from __future__ import annotations

from dataclasses import is_dataclass, fields
from typing import Type, TypeVar, get_origin, get_args, Union, get_type_hints
from collections.abc import Mapping
from envyaml import EnvYAML

T = TypeVar("T")


class ConfigurationService:
    def __resolve_type(self, field_type):
        origin = get_origin(field_type)
        if origin is Union:
            args = get_args(field_type)
            non_none_args = [arg for arg in args if arg is not type(None)]
            return non_none_args[0] if non_none_args else field_type
        return field_type

    def __config_loader_dict(self, data: Mapping, config_class: Type[T]) -> T:
        config_dict = {}
        type_hints = get_type_hints(config_class)

        for field in fields(config_class):
            field_type = self.__resolve_type(type_hints[field.name])
            raw_value = data.get(field.name, field.default)

            if is_dataclass(field_type) and isinstance(raw_value, Mapping):
                config_dict[field.name] = self.__config_loader_dict(raw_value, field_type)
            else:
                config_dict[field.name] = raw_value

        return config_class(**config_dict)

    def load(self, path: str, config_class: Type[T], prefix: str | None = None) -> T:
        yaml_data = EnvYAML(path, strict=True, include_environment=True)
        data_section = yaml_data if prefix is None else yaml_data.get(prefix, {})

        config_dict = {}
        type_hints = get_type_hints(config_class)

        for field in fields(config_class):
            field_type = self.__resolve_type(type_hints[field.name])
            raw_value = data_section.get(field.name, field.default)

            if is_dataclass(field_type) and isinstance(raw_value, Mapping):
                config_dict[field.name] = self.__config_loader_dict(raw_value, field_type)
            else:
                config_dict[field.name] = raw_value

        return config_class(**config_dict)
