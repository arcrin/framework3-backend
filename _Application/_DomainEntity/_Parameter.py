from abc import ABC, abstractmethod
from typing import Any, Union, Dict


class Parameter(ABC):
    def __init__(self, parameter_name: str):
        self._parameter_name: str = parameter_name
        self._description: str = ""
        self._result: bool

    @property
    def result(self) -> bool:
        return self._result

    @result.setter
    def result(self, value: bool) -> None:
        self._result = value

    @property
    def name(self) -> str:
        return self._parameter_name

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    @property
    @abstractmethod
    def expected_value(self) -> Any:
        raise NotImplementedError

    @property
    @abstractmethod
    def measured_value(self) -> Any:
        raise NotImplementedError

    @measured_value.setter
    @abstractmethod
    def measured_value(self, value: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def as_dict(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def start_measurement(self, expected_value: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop_measurement(
        self, measured_value: Any, description: str, result: bool
    ) -> None:
        raise NotImplementedError


class SingleValueParameter(Parameter):
    def __init__(
        self,
        parameter_name: str,
    ):
        super().__init__(parameter_name)
        self._expected_value: Union[str, int, float]
        self._measured_value: Union[str, int, float]

    @property
    def expected_value(self) -> Union[str, int, float]:
        return self._expected_value

    @property
    def measured_value(self) -> Union[str, int, float]:
        return self._measured_value

    @measured_value.setter
    def measured_value(self, value: Union[str, int, float]) -> None:
        self._measured_value = value

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "expected": self.expected_value,
            "measured": self.measured_value,
            "description": self.description,
            "result": self.result,
            "id": self.name
        }

    def start_measurement(self, expected_value: Union[str, int, float]) -> None:
        self._expected_value = expected_value

    def stop_measurement(
        self, measured_value: Any, description: str, result: bool
    ) -> None:
        self._measured_value = measured_value
        self._description = description
        self._result = result
