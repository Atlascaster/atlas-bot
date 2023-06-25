import openai
import logging
from farcaster import Warpcast
from farcaster.models import Parent
import os
from dotenv import load_dotenv

from atlas.commands.text2img import Text2Img


load_dotenv()


class Cast:
    def __init__(self, username, content):
        self.username = username
        self.content = content


class Summary:
    def __init__(self, fcc: Warpcast):
        self.fcc = fcc
        self.t2i = Text2Img()

    def start_summary(self, call_cast):
        try:
            call_cast = self.fcc.get_cast(call_cast.hash).cast
            all_casts = self.fcc.get_all_casts_in_thread(call_cast.thread_hash).casts

            replies = [Cast(cast.author.username, cast.text) for cast in all_casts]
            root_cast = self.fcc.get_cast(hash=call_cast.thread_hash).cast
            text = self.summarize_replies(root_cast, replies)

            print(text)  # This is printing the output of GPT
            parent = Parent(fid=call_cast.author.fid, hash=call_cast.hash)

            return text, parent
        except Exception as e:
            logging.error(f"Error in start_summary method: {e}")
            raise

    def summarize_replies(self, root_cast, replies):
        try:
            # print("root " + root_cast.author.username)
            text_input = "Question: " + root_cast.text + "n"

            for i, reply in enumerate(replies):
                text_input += (
                    f'Reply {i + 1}: {reply.username} said, "{reply.content}"n'
                )

            text_input += (
                "nSummarize the entire thing laconically, don't mention users."
            )

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": text_input}],
            )

            summary = response.choices[0].message.content
            if len(summary) > 320:
                print("summary" + summary)
                img_url = self.t2i.convert(text=summary)
                print("url " + img_url)
                summary = img_url
                print(img_url)
            return summary
        except Exception as e:
            logging.error(f"Error in summarize_replies method: {e}")
            raise
