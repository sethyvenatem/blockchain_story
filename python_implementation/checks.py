# -----------------------------------------------------------
# Check that a given *.json is right
#
# 31/07/2023 Steven Mathey
# email steven.mathey@gmail.ch
# -----------------------------------------------------------

import json
import rsa
import io
import datetime as dt
import sys
from web3 import Web3, AsyncWeb3
import pytz
import numpy as np

def import_json(file_name):
    
    if file_name[-5:].lower() != '.json':
        sys.exit('The file name ('+file_name+') must end with \'.json\'.')
        
    try:
        return json.load(open(file_name))
    except:
        sys.exit('Could not find '+file_name+'.')
        
################################# The program starts here ################################################

# The name of the file to check is provided as argument
data = import_json(sys.argv[2])

if set(['story_title', 'chapter_number', 'author', 'chapter_title', 'text']) == set(data.keys()):
    # Unsigned chapter data
    
elif set(['chapter_data', 'encrypted_hashed_chapter', 'public_key']) == set(data.keys()):
    # signed chapter data
    
elif set(['block_content', 'hash']) == set(data.keys()):
    # isolated validated block
    check hash
    
    data = data['block_content']
    if 'character_limits' in data.keys():
        # genesis block
        
    elif 'signed_chapter_data' in data.keys():
        # normal block
        
elif all([x.isdigit() for x in data.keys()]):
    # full story
    
    
#genesis_fields = ['story_title', 'chapter_number', 'author', 'character_limits', 'number_of_chapters', 'mining_delay_days', 'intended_mining_time_days', 'mining_date', 'story_age_days', 'miner_name', 'difficulty']
#block_fields = ['signed_chapter_data', 'hash_previous_block' 'hash_eth', 'miner_name', 'mining_date', 'story_age_days', 'difficulty', 'nb_tries', 'nonce']

Use file name as input.

From file_name, load json and look at keys.

Go from simle to complex:
    - if keys of chapter_data, check
    - if keys of signed_chapter_data, check
    ..

Import block
Local checks:
    - Compute hash of everything and check that it matches block hash
    - Compute hash of author data and compare to decrypted hash
    - check the number of characters in the author data different fields
previous block check
    - check that the block number is one more than the previous block
    - check that mining date is more than 1 week after previous block mining date
    - check that the previous block hash is right
Comparison to ETH
    - check that the eth hash is the right one.
    
Make readable pdf from:
    - chapter data
    - secure chapter data
    - validated block (isolated)
    - full story
In all cases, check as much as possible