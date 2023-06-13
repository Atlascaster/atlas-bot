import logging
import os

from dotenv import load_dotenv
from farcaster import Warpcast
from farcaster.models import Parent

from atlas.commands.summary import Summary

load_dotenv()
DEV_MODE = bool(os.getenv("DEV_MODE") == "TRUE")
SUMMARY_COM = "summary"
HELP_COM = "help"
print(DEV_MODE)


class Commands:
    def __init__(self, fcc: Warpcast, bot_username):
        self.fcc: Warpcast = fcc
        self.bot_username = bot_username
        self.summary = Summary(fcc)

    def handle_command(self, notif):
        command_mapping = {
            SUMMARY_COM: self.handle_summary_command,
            HELP_COM: self.handle_help_command,
        }

        command_prefix = f"{self.bot_username} "
        for command, handler in command_mapping.items():
            if notif.content.cast.text.lower().startswith(command_prefix + command):
                handler(notif)
                break

    def handle_generic_command(self, notif, command, perform_func):
        if self.should_command_run(
            notif.content.cast.hash,
        ):
            try:
                perform_func(notif)
                self.mark_command_run(notif.content.cast.hash)
            except Exception as e:
                self.handle_error(e, f"Error while handling {command} command")

    def handle_summary_command(self, notif):
        self.handle_generic_command(notif, SUMMARY_COM, self.perform_summary_command)

    def handle_help_command(self, notif):
        self.handle_generic_command(notif, HELP_COM, self.perform_help_command)

    def should_command_run(self, hash: str):
        try:
            likes = self.fcc.get_cast_likes(cast_hash=hash, limit=100)
            for like in likes.likes:
                if like.reactor.username == self.bot_username.lstrip("@"):
                    return False
            return True
        except Exception as e:
            self.handle_error(e, "Error while checking if command should run: {hash}")
            return False

    def mark_command_run(self, hash: str):
        try:
            if DEV_MODE:
                logging.info("Marking command as run (but dev mode)")
            else:
                self.fcc.like_cast(cast_hash=hash)
        except Exception as e:
            self.handle_error(e, "Error while marking command as run")

    def post_to_farcaster(self, text: str, parent: Parent):
        try:
            if DEV_MODE:
                logging.info("Posting to farcaster (but dev mode)")
            else:
                self.fcc.post_cast(text=text, parent=parent)
        except Exception as e:
            self.handle_error(e, "Error while posting to farcaster")

    def post_thread_to_farcaster(self, replies: list, parent: Parent):
        try:
            if DEV_MODE:
                logging.info("Posting to farcaster (but dev mode)")
            else:
                for reply in replies:
                    res = self.fcc.post_cast(text=reply, parent=parent)
                    parent = res.cast.parent_hash
        except Exception as e:
            self.handle_error(e, "Error while posting to farcaster")

    # This is a generic command example not meant for production
    def perform_summary_command(self, notif):
        logging.info("Performing summary command")
        reply, parent = self.summary.start_summary(notif.content.cast)
        self.post_to_farcaster(text=reply, parent=parent)
        logging.info("Summary command completed")

    def perform_help_command(self, notif):
        logging.info("Performing help command")
        reply = (
            "Thanks for your interest in atlas bot! "
            "Tag @alexpaden for further assistance. "
        )
        parent = Parent(fid=notif.content.cast.author.fid, hash=notif.content.cast.hash)
        self.post_to_farcaster(text=reply, parent=parent)
        logging.info("Help command completed")

    def handle_error(self, error, message):
        # Log the error and take any necessary action to handle it
        logging.error(f"{message}: {error}")
