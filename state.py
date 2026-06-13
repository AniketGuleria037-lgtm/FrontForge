from typing import TypedDict, Optional

class AgentState(TypedDict):
    user_prompt: str
    specs: Optional[dict]
    plan: Optional[dict]
    ui_architecture: Optional[dict]
    components: Optional[dict]
    style: Optional[dict]
    package: Optional[dict]
    review: Optional[dict]