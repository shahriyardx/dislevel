from dataclasses import dataclass


@dataclass
class Field:
    name: str
    type: str
    primary: bool = False
    null: bool = True
    default: str = None
