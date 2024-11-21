from typing import Annotated, Optional, List
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import TypedDict
import time

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    current_step: Optional[int]
    total_steps: Optional[int]
    user_task: Optional[str]

class PlannerState:
    def __init__(self):
        self.start_time = time.time()
        self.system_time = 0
        self.steps: List[str] = []
        self.current_step = 0
    
    def get_elapsed_time(self) -> float:
        return time.time() - self.start_time
    
    def increment_step(self):
        self.current_step += 1
        if self.current_step >= len(self.steps):
            self.reset_steps()
    
    def reset_steps(self):
        self.steps = []
        self.current_step = 0
    
    def update_system_time(self):
        self.system_time += 1
    
    def can_add_steps(self) -> bool:
        return len(self.steps) <= self.current_step