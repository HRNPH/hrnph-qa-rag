import os
from promptflow.core import tool
import re
from dotenv import load_dotenv

from flows.utils.ai_services import AIServices
from promptflow.tracing import trace, start_trace

start_trace(collection="hrnph-rag-tag-rw")
load_dotenv()


class PostProcess:
    @staticmethod
    def clean_tags(tags: list) -> list:
        """
        Strips whitespace, removes empty tags, and filters out special characters
        except underscores (_) and hyphens (-).
        """
        cleaned_tags = [
            re.sub(
                r"[^\w\s_-]", "", tag
            ).strip()  # Remove special characters except _ and -
            for tag in tags
            if tag.strip()  # Remove empty tags
        ]
        return [tag for tag in cleaned_tags if tag]  # Ensure no empty strings remain


@trace
@tool
def tag_rewrite(
    system_prompt: str, user_prompt: str, model: str = os.environ["OPENAI_MODEL"]
):
    for i in range(3):
        result = (
            AIServices.OPENAI_CLIENT.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                # Increase temperature for each retry, in case the answer is not in the right format
                temperature=0 + i / 2,
            )
            .choices[0]
            .message.content
        )
        if "<NO>" in result:
            return []  # No tags Necessary/Found

        result = result.split(",")
        if "," not in result:
            # Cleanup
            tags = PostProcess.clean_tags(result)
            return tags

    raise ValueError("Failed to rewrite tags")
