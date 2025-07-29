from typing import Callable, Type, Any, Dict
import inspect

class Container:
    _factories: Dict[Type, Callable[..., Any]] = {}

    @classmethod
    def register(cls, interface: Type, factory: Callable[..., Any]):
        cls._factories[interface] = factory

    @classmethod
    def resolve(cls, interface: Type, **kwargs) -> Any:
        if interface not in cls._factories:
            raise Exception(f"No factory registered for {interface}")

        factory = cls._factories[interface]
        sig = inspect.signature(factory)
        accepted_args = {
            name: kwargs[name]
            for name in sig.parameters
            if name in kwargs
        }

        try:
            return factory(**accepted_args)
        except TypeError as e:
            raise TypeError(
                f"Failed to resolve {interface.__name__} with arguments {accepted_args}. "
                f"Check your factory signature. Original error: {str(e)}"
            )
