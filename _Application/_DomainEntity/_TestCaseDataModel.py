from typing import Dict
from datetime import datetime
from _Parameter import Parameter

        
class TestRepetition:
    def __init__(self, 
                 repetition_count: int,
                 timestamp: datetime,
                 test_duration: float,
                 ):
        self._repetition_count: int = repetition_count
        self._timestamp: datetime = timestamp
        self._test_duration: float = test_duration
        self._parameters: Dict[str, Parameter] = dict()
            

class TestCaseDataModel:
    def __init__(self, test_case_name: str,
                 test_description: str):
        self._test_case_name: str = test_case_name
        self._test_description: str = test_description
        
