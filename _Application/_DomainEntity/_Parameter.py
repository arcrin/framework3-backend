from abc import ABC, abstractmethod
from typing import Any, Union, Dict


class Parameter(ABC):
    def __init__(self, parameter_name: str):
        self._parameter_name: str = parameter_name
        self._description: str = ""

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
    
class SingleValueParameter(Parameter):
    def __init__(self, parameter_name: str,
                 expected_value: Union[str, int, float]):
        super().__init__(parameter_name)
        self._expected_value: Union[str, int, float] = expected_value
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
            "description": self.description
        }