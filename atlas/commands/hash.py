from farcaster import Warpcast
from farcaster.models import Parent


class Hash:
    def __init__(self, fcc: Warpcast):
        self.fcc = fcc

    # Will break if a parent is deleted, but that's a problem for another day
    def start_hash(self, call_cast):
        if call_cast.parent_hash is None:
            text = f"The hash of the cast that called me is:\n{call_cast.hash}"
            parent = Parent(fid=call_cast.author.fid, hash=call_cast.hash)
        else:
            text = f"The hash of the cast you responded to is:\n{call_cast.parent_hash}"
            parent = Parent(fid=call_cast.author.fid, hash=call_cast.hash)

        return text, parent


# THIS IS AN EXAMPLE COMMAND FILE
