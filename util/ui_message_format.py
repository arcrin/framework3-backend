from typing import Optional, Any, TypeVar, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class InputDetails:
    prompt: str
    type: str
    validation_pattern: Optional[str]

    def __init__(self, prompt: str, type: str, validation_pattern: Optional[str]) -> None:
        self.prompt = prompt
        self.type = type
        self.validation_pattern = validation_pattern

    @staticmethod
    def from_dict(obj: Any) -> 'InputDetails':
        assert isinstance(obj, dict)
        prompt = from_str(obj.get("prompt"))
        type = from_str(obj.get("type"))
        validation_pattern = from_union([from_str, from_none], obj.get("validationPattern"))
        return InputDetails(prompt, type, validation_pattern)

    def to_dict(self) -> dict:
        result: dict = {}
        result["prompt"] = from_str(self.prompt)
        result["type"] = from_str(self.type)
        if self.validation_pattern is not None:
            result["validationPattern"] = from_union([from_str, from_none], self.validation_pattern)
        return result


class UIMessageFormat:
    description: str
    input_details: InputDetails
    message_type: str
    request_id: str
    test_id: str

    def __init__(self, description: str, input_details: InputDetails, message_type: str, request_id: str, test_id: str) -> None:
        self.description = description
        self.input_details = input_details
        self.message_type = message_type
        self.request_id = request_id
        self.test_id = test_id

    @staticmethod
    def from_dict(obj: Any) -> 'UIMessageFormat':
        assert isinstance(obj, dict)
        description = from_str(obj.get("description"))
        input_details = InputDetails.from_dict(obj.get("inputDetails"))
        message_type = from_str(obj.get("messageType"))
        request_id = from_str(obj.get("requestId"))
        test_id = from_str(obj.get("testId"))
        return UIMessageFormat(description, input_details, message_type, request_id, test_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["description"] = from_str(self.description)
        result["inputDetails"] = to_class(InputDetails, self.input_details)
        result["messageType"] = from_str(self.message_type)
        result["requestId"] = from_str(self.request_id)
        result["testId"] = from_str(self.test_id)
        return result


def ui_message_format_from_dict(s: Any) -> UIMessageFormat:
    return UIMessageFormat.from_dict(s)


def ui_message_format_to_dict(x: UIMessageFormat) -> Any:
    return to_class(UIMessageFormat, x)
