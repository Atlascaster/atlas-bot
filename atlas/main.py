import logging
import os
import time

import openai
from dotenv import load_dotenv
from farcaster import Warpcast
from farcaster.models import Parent

import atlas.commands.conversator as conversator
from atlas.commands.command_manager import Commands

load_dotenv()

logging.basicConfig(
    # filename="bot.log",
    level=logging.INFO,  # Set the log level to INFO
    format="%(asctime)s %(message)s",
)


def configure_main_function():
    fcc = Warpcast(access_token=os.getenv("FARC_SECRET"))
    bot_username = os.getenv("USERNAME")
    openai.api_key = os.getenv("OPENAI_API_KEY")

    return Commands(
        fcc=fcc,
        bot_username=bot_username,
    )


def start_notification_stream(commands_instance: Commands):
    fcc = commands_instance.fcc
    bot_username = commands_instance.bot_username

    for notif in fcc.stream_notifications():
        if notif and notif.content.cast.text.startswith(bot_username):
            commands_instance.handle_command(notif)
            pass

        if (
            notif
            and notif.content.cast.parent_hash is not None
            and notif.timestamp > int(time.time() * 1000) - 300000  # 5 minutes
        ):
            thread_hash = notif.content.cast.thread_hash
            hash = notif.content.cast.hash

            root = fcc.get_cast(hash=thread_hash)  # type: ignore
            if "conversator" not in root.cast.text:
                print(f"not replying to {notif.content.cast.hash}")
                continue

            logging.info(f"replying to {notif.content.cast.hash}")
            cs = conversator.get_conversation(thread_hash, hash)  # type: ignore
            ms = conversator.stringify_messages(cs)
            response = openai.ChatCompletion.create(
                model="gpt-4", messages=[{"role": "user", "content": ms}]
            )
            response = response["choices"][0]["message"]["content"]
            logging.info(f"gpt4 response: {response}")
            parent = Parent(fid=notif.actor.fid, hash=hash)
            fcc.post_cast(response, parent=parent)


def main():
    logging.info("Configuring main function")
    try:
        commands_instance = configure_main_function()
    except Exception as e:
        logging.error(f"Error occurred configuring main function: {e}")
        return

    logging.info("Starting notification stream in main")

    while True:
        try:
            start_notification_stream(commands_instance)
        except Exception as e:
            logging.error(f"Error occurred in notification stream, main function: {e}")
            time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Error occurred __main__ function: {e}")
