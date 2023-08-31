from farcaster.models import ApiCast
import openai
import re
from farcaster import Warpcast
import os
from typing import List, Optional, Dict, Any


def get_ancestors(hash: str, casts: List[ApiCast]) -> List[ApiCast]:
    ancestor_chain: List[ApiCast] = []
    current_hash: Optional[str] = hash
    while current_hash:
        current_cast = next((cast for cast in casts if cast.hash == current_hash), None)
        if not current_cast:
            break
        ancestor_chain.insert(0, current_cast)
        current_hash = current_cast.parent_hash

    return ancestor_chain


def extract_messages(casts: List[ApiCast]) -> List[Dict[str, Any]]:
    def get_cast(c: ApiCast) -> Dict[str, Any]:
        return {
            "username": c.author.username,
            "text": re.sub(r"\s+", " ", c.text).strip(),
        }

    return list(map(get_cast, casts))


def get_conversation(thread_hash: str, cast_hash: str) -> List[Dict[str, Any]]:
    fcc = Warpcast(access_token=os.getenv("FARC_SECRET"))
    all_thread_casts = fcc.get_all_casts_in_thread(thread_hash=thread_hash)
    ancestors_chain = get_ancestors(cast_hash, all_thread_casts.casts)
    return extract_messages(ancestors_chain)


def stringify_messages(
    messages: List[Dict[str, Any]], total_messages: int = 8, username: str = "picture"
) -> str:
    out = ""
    messages = messages[-total_messages:]
    for message in messages:
        out += f"@{message['username']}: {message['text']}\n"

    out += f"@{username}: <YOUR_RESPONSE>"
    out += "\n\n"
    out += "Respond with a question, keep conversation interesting, use curious tone, "
    out += "respond laconically, no need to @-mention anyone."
    return out


th = "0xdf866226f22f9f36331038421e7eed4cc7b726e2"
h = "0x3879672d31a259330a61d5bc77df5693ac9bd121"
cs = get_conversation(th, h)
ms = stringify_messages(cs)
response = openai.ChatCompletion.create(
    model="gpt-4", messages=[{"role": "user", "content": ms}]
)

content = response["choices"][0]["message"]["content"]
print(content)
