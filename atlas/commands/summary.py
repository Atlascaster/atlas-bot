from farcaster import Warpcast
from farcaster.models import Parent


class Summary:
    def __init__(self, fcc: Warpcast):
        self.fcc = fcc

    # Will break if a parent is deleted, but that's a problem for another day
    def start_summary(self, call_cast):
        call_cast = self.fcc.get_cast(call_cast.hash).cast
        print(call_cast)

        text = f"This is a sample command"
        parent = Parent(fid=call_cast.author.fid, hash=call_cast.hash)

        return text, parent


# THIS IS AN EXAMPLE COMMAND FILE
