from farcaster import Warpcast
from farcaster.models import Parent


class Summary:
    def __init__(self, fcc: Warpcast):
        self.fcc = fcc

    def start_summary(self, call_cast):
        call_cast = self.fcc.get_cast(call_cast.hash).cast
        all_casts = self.fcc.get_all_casts_in_thread(call_cast.thread_hash).casts

        for cast in all_casts:
            if cast.parent_hash == cast.thread_hash:
                print(cast.author.username + ": " + cast.text)

        text = f"This is a sample command"
        parent = Parent(fid=call_cast.author.fid, hash=call_cast.hash)

        return text, parent
