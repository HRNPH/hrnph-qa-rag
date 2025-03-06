import os
from typing import Any, List
from promptflow.core import tool
import openai
from dotenv import load_dotenv

from flows.utils.ai_services import AIServices
from promptflow.tracing import trace, start_trace
import logging

from flows.utils.handle_history import HistoryHandler

logger = logging.getLogger()
start_trace(collection="hrnph-rag-tag-rw")
load_dotenv()


@trace
def reference_searching(
    tags: List[str], collection_name: str = os.environ["TARGET_COLLECTION_NAME"]
):
    results = AIServices.search_by_tags(collection_name=collection_name, tags=tags)
    # Create Reference String
    reference_string = ""
    for result in results:
        if result.title:
            reference_string += "# {}\n".format(result.title)
        reference_string += "{}\n".format(result.document)
        reference_string += "Tags: {}\n\n".format(", ".join(result.tags))

    return reference_string


@trace
def add_ipad_information(user_prompt: str, tags: List[str]):
    if not tags:
        raise ValueError("Tags must be provided to search for references.")
    reference_text = reference_searching(tags=tags)
    user_prompt += "\n\n**The Ipad Shown the Following Information**\n\n"
    user_prompt += "\nSearched: {}\n\n".format(tags)
    user_prompt += reference_text
    return user_prompt


@trace
@tool
def query_process(
    system_prompt: str,
    user_prompt: str,
    chat_history: List[Any],
    tags: List[str] = ["technologies"],
    model: str = os.environ["OPENAI_MODEL"],
):
    user_prompt = (
        add_ipad_information(user_prompt=user_prompt, tags=tags)
        if tags
        else user_prompt
    )
    history = HistoryHandler.process_history(chat_history)
    result = (
        AIServices.OPENAI_CLIENT.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
            ]
            + [
                # Chat History
                {
                    "role": "user" if chat.is_user else "assistant",
                    "content": chat.content,
                }
                for i, chat in enumerate(history)
            ]
            + [
                # User Prompt
                {"role": "user", "content": user_prompt},
            ],
        )
        .choices[0]
        .message.content
    )
    return result
