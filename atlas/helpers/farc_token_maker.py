import os

from dotenv import load_dotenv
from farcaster import Warpcast

# THIS FILE GENERATES AN ACCESS TOKEN USING YOUR MNEMONIC PHRASE FROM .env
# RUN VIA 'python3 ./token_maker.py' AND COPY THE OUTPUT TO YOUR .env FILE

load_dotenv()

# Make sure to set FARC_MNEMONIC in your .env file
fcc = Warpcast(os.getenv("FARC_MNEMONIC"))

# prints true if the client is connected to the farcaster node
print(fcc.get_healthcheck())

# expires in 1 year
minutes = 525600

# Generate a new access token
access_token = fcc.create_new_auth_token(expires_in=minutes)

# save it to FARC_SECRET in your .env file
print(access_token)
