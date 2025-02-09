from typing import Any, Literal, List, Optional, Union
from pydantic import BaseModel, ValidationError


class PfHistoryFormat(BaseModel):
    inputs: dict[Literal["query"], str]
    outputs: dict[Literal["answer"], str]


class NormalHistoryFormat(BaseModel):
    is_user: bool
    content: str


class HistoryHandler:
    @staticmethod
    def process_history(history: List[Any]) -> List[NormalHistoryFormat]:
        # Try to parse as PromptFlow history, and if it fails, parse as normal history
        result = None
        try:
            result = [PfHistoryFormat(**item) for item in history]
        except ValidationError as pf_error:
            try:
                return [NormalHistoryFormat(**item) for item in history]
            except ValidationError as normal_error:
                raise ValueError(
                    f"Failed to parse history as either PromptFlow or Normal history.\n"
                    f"PromptFlow error: {pf_error}\n"
                    f"Normal history error: {normal_error}"
                )

        # Format into normal format if it's PromptFlow history
        history: List[NormalHistoryFormat] = []
        for item in result:
            history.append(
                NormalHistoryFormat(is_user=True, content=item.inputs["query"])
            )
            history.append(
                NormalHistoryFormat(is_user=False, content=item.outputs["answer"])
            )
        return history
