from node.tc_node import TCNode
from typing import List
import asyncio

class SampleProfile:
    def __init__(self) -> None:
        self._test_case_list: List[TCNode] = []

        tc1 = TCNode(task_func1)
        tc2 = TCNode(task_func2)
        tc3 = TCNode(task_func3)
        tc4 = TCNode(task_func4)
        tc5 = TCNode(task_func5)
        tc6 = TCNode(task_func6)
        tc7 = TCNode(task_func7)

        tc1.add_dependency(tc2)
        tc2.add_dependency(tc3)
        tc1.add_dependency(tc4)
        tc4.add_dependency(tc5)
        tc3.add_dependency(tc5)
        tc2.add_dependency(tc6)
        tc6.add_dependency(tc7) 

        self._test_case_list.append(tc1)
        self._test_case_list.append(tc2)
        self._test_case_list.append(tc3)
        self._test_case_list.append(tc4)
        self._test_case_list.append(tc5)
        self._test_case_list.append(tc6)
        self._test_case_list.append(tc7)

    @property
    def test_case_list(self) -> List[TCNode]:
        return self._test_case_list

    def add_test(self, tc: TCNode) -> None:
        self._test_case_list.append(tc)



def fib(n: int) -> int:
    if n <= 1:
        return n
    else:
        return (fib(n-1) + fib(n-2))

async def task_func1(task2: bool | None=None, task4: bool | None=None):
    await asyncio.sleep(1)
    print(f"Executed task1 with task2 result {task2} and task4 result {task4}")
    return True

async def task_func2(task3: bool | None=None, task6: bool | None=None):
    await asyncio.sleep(1)
    print(f"Executed task2 with task3 result {task3} and task6 result {task6}")
    return True

def task_func3(task5: bool | None=None) -> int:
    result = fib(10)
    print(f"Task 3: calculated fib(30) with task5 result {task5}")
    return result

# async def task_func3(task5: bool | None=None):
#     await asyncio.sleep(1)
#     print(f"Executed task3 with task5 result {task5}")
#     return True


async def task_func4(task5: bool | None=None):
    await asyncio.sleep(3)    
    print(f'Executed task4 with task5 result {task5}')
    return True

async def task_func5():
    await asyncio.sleep(5)    
    print('Executed task5')
    return True

async def task_func6(task7: bool | None=None):
    await asyncio.sleep(3)    
    print(f'Executed task6 with task7 result {task7}')
    return True

async def task_func7(): 
    await asyncio.sleep(5)   
    print("Executed task7")
    return True
    # await asyncio.sleep(2)
    # raise Exception("Task 7 failed with exception")