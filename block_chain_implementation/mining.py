# -----------------------------------------------------------
# Perform the mining and generate finished block
#
# 15/07/2023 Steven Mathey
# email steven.mathey@gmail.ch
# -----------------------------------------------------------

import json
import warnings
import rsa
import io
import datetime
import sys
from web3 import Web3, AsyncWeb3
import pytz
import numpy as np
import random

def check_chapter_data(chapter_data, genesis):
    # This checks that the chapter to submit does not violate the rules given in the genesis block.
    
    test = True
    for key in genesis['character_limits'].keys():
        if len(chapter_data[key]) > genesis['character_limits'][key]:
            warnings.warn('The field '+key+' can only contain '+str(genesis['character_limits'][key])+' characters. '+ str(len(chapter_data[key])-genesis['character_limits'][key])+' characters must be removed before it can be added to the story.')
            test = False
    if int(genesis.get('number_of_chapters',1000)) < int(chapter_data['chapter_number']):
        # Only test that the chapter number is not too large if the field is present in the genesis block. If there are more than 1000 chapters, then this script needs to be updated!
        warnings.warn('This story can only have more than '+str(genesis['number_of_chapters'])+' chapters.')
        test = False
    return test

def validate_chapter_data(secure_chapter_data):
    # This validates teh secure chapter data. It checks:
    #    - that the chapter data complies with the rules of the genesis block
    #    - that the digital signature of the secure chapter data is right.
    
    test = check_chapter_data(secure_chapter_data['chapter_data'])
    
    clear_chapter_data = json.dumps(secure_chapter_data['chapter_data']).encode('utf8')
    encrypted_hashed_chapter = bytes.fromhex(secure_chapter_data['encrypted_hashed_chapter'])
    public_key = rsa.PublicKey.load_pkcs1(bytes.fromhex(secure_chapter_data['public_key']))
    try:
        temp = rsa.verify(clear_chapter_data, encrypted_hashed_chapter, public_key) == 'SHA-256'
    except:
        test = False
        warnings.warn('The secure chapter data has been modified. Don\'t validate it.')
    
    return test

def import_json(file_name, stop_if_fail = True):
    try:
        return json.load(open(file_name))
    except:
        if stop_if_fail:
            sys.exit('Could not find '+file_name+'.')
        else:
            warnings.warn('Could not find '+file_name+'.')
            return {}

def get_eth_block_info(target_date, success = True):
    
    api = 'https://eth-mainnet.public.blastapi.io'
    w3 = Web3(Web3.HTTPProvider(api))
    #w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(api))
    #w3 = Web3(Web3.WebsocketProvider(api))
    if target_date.tzinfo is None:
        target_date = pytz.utc.localize(target_date)

    start_time = datetime.datetime.now(tz = pytz.UTC)
    approx_nb_blocks = int(np.ceil((start_time-target_date).total_seconds()/(12.5)))
    latest_block = w3.eth.get_block('latest').number
    target_block = latest_block - approx_nb_blocks
    block_timestamp = pytz.utc.localize(datetime.datetime.utcfromtimestamp(w3.eth.get_block(target_block).timestamp))

    while (block_timestamp > target_date) & (datetime.datetime.now(tz = pytz.UTC) < start_time+datetime.timedelta(minutes = 5)):
        # stop if the function iterates for more than 5 minutes.
        approx_nb_blocks = int(np.ceil((block_timestamp-target_date).total_seconds()/(12.5)))
        target_block = target_block - approx_nb_blocks
        block_timestamp = pytz.utc.localize(datetime.datetime.utcfromtimestamp(w3.eth.get_block(target_block).timestamp))
    target_block += 1
    
    if (pytz.utc.localize(datetime.datetime.utcfromtimestamp(w3.eth.get_block(target_block).timestamp)) < target_date):
        # If we overshoot, come back one block at a time. This should only happen when a block is missing close to the targed time.
        while (pytz.utc.localize(datetime.datetime.utcfromtimestamp(w3.eth.get_block(target_block).timestamp)) < target_date):
            target_block += 1
    
    if ((datetime.datetime.now(tz = pytz.UTC) > start_time+datetime.timedelta(minutes = 5)) or 
        (block_timestamp > target_date) or 
        (pytz.utc.localize(datetime.datetime.utcfromtimestamp(w3.eth.get_block(target_block).timestamp)) < target_date) or
        (pytz.utc.localize(datetime.datetime.utcfromtimestamp(w3.eth.get_block(target_block-1).timestamp)) > target_date)):
        # check that the search did not time out, that it passed the target block, that the target block is after the target date and that the block just before the target block is before the target date.
        if success:
            # Try a second time in case that it's a network problem.
            target_block = get_eth_block_info(target_date, False)
            if target_block is None:
                return None
        else:
            warnings.warn('Could not find ETH block.')
            return None
        
    if w3.eth.get_block('finalized').number < target_block:
        warnings.warn('The ETH block is not finalised yet. Wait about 15 minutes to be sure to mine effectively.')
        
    return w3.eth.get_block(target_block).hash.hex()

################################# The program starts here ################################################

# To create the first block (and associated story json file), uses the options specified in genesis_block.json. If the first block already exists (in file_name), then get the file name from genesis_block.json or provide it as an argument.
if (len(sys.argv)  == 2) and (sys.argv[1] == 'genesis'):
    genesis = import_json('genesis_block.json')
    genesis_hash = rsa.compute_hash(json.dumps(genesis).encode('utf8'), 'SHA-256').hex()
    genesis['hash'] = genesis_hash
    file_name = genesis['story_title'].title().replace(' ','')+'_000.json'
    with open(file_name, "w") as outfile:
        outfile.write(json.dumps({'0':genesis}))
    sys.exit()
else:
    # The file is named as [story title with underscores instead of spaces]_[largest validated chapter number].json
    file_name = sys.argv[1]

# Import the block to validate and the beginning of the story
chapter_data_to_validate = input('Type in the file name of the chapter to validate: ')
if chapter_data_to_validate[-5:].lower() != '.json':
    sys.exit('The file name must end with \'.json\'.')
secure_chapter_data = import_json(chapter_data_to_validate)
story = import_json(file_name)
    
# Check that the chapter data is correct.
assert validate_chapter_data(secure_chapter_data), 'The secure chapter data does not comply with the rules of this story.'

# Import the previous block and get it's mining date
assert str(int(secure_chapter_data['chapter_data']['chapter_number'])-1) in story.keys(), 'The chapter number of the block to add is not the last chapter number of the story.'
previous_block = story[str(int(secure_chapter_data['chapter_data']['chapter_number'])-1)]

mining_date_previous_block = pytz.utc.localize(datetime.datetime.strptime(previous_block['mining_date'], '%Y/%m/%d %H:%M:%S'))
assert mining_date_previous_block+datetime.timedelta(days = int(genesis['mining_delay_days'])) <= datetime.datetime.now(tz = pytz.UTC), 'The previous block was mined on the ' + mining_date_previous_block.strftime("%Y/%m/%d, %H:%M:%S")+'. This is less than ' + genesis['mining_delay_days'] + ' days ago. This block can\'t be validated.'

new_block = {'secure_chapter_data':secure_chapter_data, 'hash_previous_block': previous_block['hash'], 'hash_eth': get_eth_block_info(mining_date_previous_block)}

# Now perform the actual mining!
# It takes about (16)**difficulty tries to find a valid nonce. It takes about 0.000046 seconds for each try. difficulty = 6 should take about 10 minutes.
difficulty = 6
max_hash = int('f'*(64-difficulty),16)
start_time = datetime.datetime.now(tz = pytz.UTC)
new_block['mining_date'] = datetime.datetime.strftime(datetime.datetime.now(tz = pytz.UTC), '%Y/%m/%d %H:%M:%S')
new_block['nonce'] = ''.join(random.choice('0123456789abcdef') for _ in range(64))
new_hash = rsa.compute_hash(json.dumps(new_block).encode('utf8'), 'SHA-256')
nb_tries = 1
print('Start mining! It should take about '+str(0.000046*(16**difficulty)/60)+' seconds to complete.')
while int.from_bytes(new_hash,'big') > max_hash:
    new_block['mining_date'] = datetime.datetime.strftime(datetime.datetime.now(tz = pytz.UTC), '%Y/%m/%d %H:%M:%S')
    new_block['nonce'] = ''.join(random.choice('0123456789abcdef') for _ in range(64))
    new_hash = rsa.compute_hash(json.dumps(new_block).encode('utf8'), 'SHA-256')
    nb_tries += 1                           
                           
try_time = datetime.datetime.now(tz = pytz.UTC)-start_time
print(try_time,nb_tries,try_time/nb_tries)
new_block['hash'] = new_hash.hex()
new_block['nb_tries'] = str(nb_tries)
story[secure_chapter_data['chapter_data']['chapter_number']] = new_block
new_file_name = story['0']['story_title'].title().replace(' ','')+'_'+secure_chapter_data['chapter_data']['chapter_number'].rjust(3, '0')+'.json'
with open(new_file_name, "w") as outfile:
    outfile.write(json.dumps(story))
    
Keep track of the difficulty
Make it harder if the mining time is exactly 1 week after the mining time of the previous block.