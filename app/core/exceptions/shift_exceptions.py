from dataclasses import dataclass, field


@dataclass
class ShiftClosedErrorMessage(Exception):
    shift_id: str
    message: str = field(init=False)

    def __post_init__(self) -> None:
        self.message = f"Shift with id: {self.shift_id} is closed."



@dataclass
class ShiftOpenedErrorMessage(Exception):
    shift_id: str
    message: str = field(init=False)

    def __post_init__(self) -> None:
        self.message = f"Shift with id: {self.shift_id} is opened."



@dataclass
class GetShiftErrorMessage(Exception):
    shift_id: str
    message: str = field(init=False)

    def __post_init__(self) -> None:
        self.message = f"Shift with id: {self.shift_id} does not exist."

