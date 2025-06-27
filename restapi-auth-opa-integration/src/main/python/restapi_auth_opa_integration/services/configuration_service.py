
from dataclasses import fields
from envyaml import EnvYAML
from typing import Type, TypeVar

T = TypeVar("T")


class ConfigurationService:
    def load(self, path: str, config_class: Type[T], prefix: str | None = None) -> T:
        yaml_data = EnvYAML(path, strict=False)
        data_section = yaml_data if prefix is None else yaml_data.get(prefix, {})

        config_dict = {}
        for field in fields(config_class):
            raw_value = data_section.get(field.name, field.default)
            field_type = field.type

            try:
                if raw_value is not None and not isinstance(raw_value, field_type):
                    config_dict[field.name] = field_type(raw_value)
                else:
                    config_dict[field.name] = raw_value
            except Exception:
                config_dict[field.name] = raw_value  # fallback

        return config_class(**config_dict)