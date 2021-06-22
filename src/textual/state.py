from typing import Generic, Type, TypeVar


ParentType = TypeVar("ParentType")
ValueType = TypeVar("ValueType")


class Reactive(Generic[ValueType]):
    def __init__(self, default: ValueType) -> None:
        self._default = default

    def __set_name__(self, owner: object, name: str) -> None:
        self.internal_name = f"__{name}"
        setattr(owner, self.internal_name, self._default)

    def __get__(self, obj: object, obj_type: Type[object]) -> ValueType:
        print("__get__", obj, obj_type)

        return getattr(obj, self.internal_name)

    def __set__(self, obj: object, value: ValueType) -> None:
        print("__set__", obj, value)
        setattr(obj, self.internal_name, value)


class Example:
    def __init__(self, foo: int = 3) -> None:
        self.foo = foo

    color: Reactive[str] = Reactive("blue")


example = Example()

print(example.color)
example.color = "red"
print(example.color)
print(example.foo)
