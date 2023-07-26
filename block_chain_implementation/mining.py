# -----------------------------------------------------------
# Perform the mining and generate finished block
#
#This script validates and adds one block to the existing story. If it is run with two arguments it
#    - Imports the genesis block. The file name is the first argument and the file is placed in the working directory.
#    - Estimate the difficulty of the mining of the first block.
#    - Computes the hash of the genesis block.
#    - Save it ['story_title'].title().replace(' ','')+'_000.json' (in the working directory) as the story with the first validated block
#If it is run with three arguments then it:
#    - Imports the up-until-now-validated story. The file name is the first argument and the file is placed in the working directory.
#    - Imports the signed chapter to validate. The file name is the second argument and the file is placed in the working directory.
#    - It performs as many checks as possible in order to avoid un-necessary mining. It checks that
#        - The signed chapter data is conform to the rules in the genesis block and is signed correctly
#        - The chapter number of the block to validate is right.
#        - The mining date of the previous block is far enough away in the past for the mining of the current block to take place.
#    - Initialise the block to validate with the hash of the previous block, the hash of the correct block of the ETH blockchain and the provided signed chapter data
#    - Performs the mining:
#        - Use the difficulty specified in the previous block
#        - Pick a nonce at random
#        - include the nonce, the current date and time, the number of guesses, the difficulty of the next block
#        - compute the hash of the current value
#        - retry unless the obtained hash is smaller than the max_hash (determined by the difficulty)
#    - The difficulty of the current block is determined with the 'intended_mining_time_days' attribute of the genesis block. If the mining time is shorter than 1/4 of the intented mining time, then the difficulty is set to the difficulty of the previous block plus 1 (effectively doubling the mining time). If the mining time is longer than 1/4 of the intented mining time, the the dificulty is set to the difficulty of the previous block minus one. In the other cases, the difficulty is the difficulty of the previous block.
#    - Once a suitable nonce is found, then the corresponding hash is included in the dictionary and the new story json file is saved to the working directory.
#
# 26/07/2023 Steven Mathey
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
import random

def check_chapter_data(chapter_data, genesis):
    # This checks that the chapter to submit does not violate the rules given in the genesis block.
    
    test = True
    for key in genesis['character_limits'].keys():
        if len(chapter_data[key]) > genesis['character_limits'][key]:
            print('The field '+key+' can only contain '+str(genesis['character_limits'][key])+' characters. '+ str(len(chapter_data[key])-genesis['character_limits'][key])+' characters must be removed before it can be added to the story.')
            test = False
    if genesis.get('number_of_chapters',np.inf) < chapter_data['chapter_number']:
        # Only test that the chapter number is not too large if the field is present in the genesis block.
        print('This story can not have more than '+str(genesis['number_of_chapters'])+' chapters.')
        test = False
    return test

def validate_chapter_data(signed_chapter_data, genesis):
    # This validates the signed chapter data. It checks:
    #    - that the chapter data complies with the rules of the genesis block.
    #    - that the digital signature of the signed chapter data is right.
    
    test = check_chapter_data(signed_chapter_data['chapter_data'], genesis)
    
    clear_chapter_data = json.dumps(signed_chapter_data['chapter_data']).encode('utf8')
    encrypted_hashed_chapter = bytes.fromhex(signed_chapter_data['encrypted_hashed_chapter'])
    public_key = rsa.PublicKey.load_pkcs1(bytes.fromhex(signed_chapter_data['public_key']))
    try:
        temp = rsa.verify(clear_chapter_data, encrypted_hashed_chapter, public_key) == 'SHA-256'
    except:
        test = False
        print('The signed chapter data has been modified. Don\'t validate it.')
    
    return test

def import_json(file_name):
    
    if file_name[-5:].lower() != '.json':
        sys.exit('The file name ('+file_name+') must end with \'.json\'.')
        
    try:
        return json.load(open(file_name))
    except:
        sys.exit('Could not find '+file_name+'.')

def get_eth_block_info(target_date, retry = True):
    # This finds the right block from the ETH blockchain and returns its hash value.
    # The block is the first block that comes after the target_date.
    # The algorithm starts from the current block and makes a conservative guess to jump to another block in the past. Then it uses the timestamp of the obtained block as a new current date. It repeates this until the obtained block timestamp is before the target_date. The corresponding block should be just before the target block.
    # This works fine, but can fail if one block is missing (time interval betwen block is more than 12 seconds) close to the target block. In that case, the obtained block is to far in the past. Then, the block number is increased one-by-one until the block timestamp passed again.
    # The search terminates if it lasts more than 10 minutes.
    
    api = 'https://eth-mainnet.public.blastapi.io'
    w3 = Web3(Web3.HTTPProvider(api))
    if target_date.tzinfo is None:
        target_date = pytz.utc.localize(target_date)

    start_time = dt.datetime.now(tz = pytz.UTC)
    approx_nb_blocks = int(np.ceil((start_time-target_date).total_seconds()/(12.5)))
    latest_block = w3.eth.get_block('latest').number
    target_block = latest_block - approx_nb_blocks
    block_timestamp = pytz.utc.localize(dt.datetime.utcfromtimestamp(w3.eth.get_block(target_block).timestamp))

    while (block_timestamp > target_date) & (dt.datetime.now(tz = pytz.UTC) < start_time+dt.timedelta(minutes = 5)):
        # stop if the function iterates for more than 5 minutes.
        approx_nb_blocks = int(np.ceil((block_timestamp-target_date).total_seconds()/(12.5)))
        target_block = target_block - approx_nb_blocks
        block_timestamp = pytz.utc.localize(dt.datetime.utcfromtimestamp(w3.eth.get_block(target_block).timestamp))
    target_block += 1
    
    if (pytz.utc.localize(dt.datetime.utcfromtimestamp(w3.eth.get_block(target_block).timestamp)) < target_date):
        # If we overshoot, come back one block at a time. This should only happen when a block is missing close to the target time.
        while (pytz.utc.localize(dt.datetime.utcfromtimestamp(w3.eth.get_block(target_block).timestamp)) < target_date):
            target_block += 1
    
    if ((dt.datetime.now(tz = pytz.UTC) > start_time+dt.timedelta(minutes = 5)) or
        (pytz.utc.localize(dt.datetime.utcfromtimestamp(w3.eth.get_block(target_block).timestamp)) < target_date) or
        (pytz.utc.localize(dt.datetime.utcfromtimestamp(w3.eth.get_block(target_block-1).timestamp)) > target_date)):
        # check that the search did not time out, that the target block is after the target date and that the block just before the target block is before the target date.
        # If this is not the case, try once more.
        if retry:
            # Try a second time in case that it's a network problem.
            target_block = get_eth_block_info(target_date, False)
            if target_block is None:
                return None
        else:
            print('Could not find ETH block.')
            sys.exit(0)
        
    if w3.eth.get_block('finalized').number < target_block:
        # If the obtained block number is larger than the last finalised block number, then warn the user.
        print('The ETH block is not finalised yet. Wait about 15 minutes to be sure to mine effectively.')
        
    return w3.eth.get_block(target_block).hash.hex()

def time_to_mine_days(difficulty):
    # This function estimates the time to solve the mining problem as a function of the difficulty (in days).
    seconds_to_try_once = 0.0002    
    return seconds_to_try_once*(2**difficulty)/(24*3600)

def estimate_difficulty(days):
    # This function estimates the difficulty as a function of the desired solution time (given in days).
    seconds_to_try_once = 0.0002
    # Use floor to be nice.
    return int(np.floor(np.log(24*3600*days/seconds_to_try_once)/np.log(2)))

def set_new_block_difficulty_and_mining_date(new_block, genesis, difficulty, mining_date_previous_block, story_age_previous_block):
    # Set the difficulty and mining date of the new block. 'mining_date_previous_block' is given as a timedelta.
    
    mining_date = dt.datetime.now(tz = pytz.UTC)
    mining_delay = dt.timedelta(days = genesis['mining_delay_days'])
    intended_mining_time = dt.timedelta(days = genesis['intended_mining_time_days'])
    grace = 0.25*intended_mining_time
    
    new_block['mining_date'] = dt.datetime.strftime(mining_date, '%Y/%m/%d %H:%M:%S')
    new_block['story_age_days'] = story_age_previous_block + (mining_date - genesis['mining_date']).total_seconds()/(24*3600)
      
    if mining_date > mining_date_previous_block + mining_delay + intended_mining_time + grace:
        # Too hard, reduce the difficulty.
        new_block['difficulty'] = difficulty - 1
    elif mining_date < mining_date_previous_block + mining_delay + intended_mining_time - grace:
        # Too easy, increase the difficulty.
        new_block['difficulty'] = difficulty + 1
    else:
        # Just right.
        new_block['difficulty'] = difficulty
    return new_block

def check(statement,message):
    if not(statement):
        print(message)
        sys.exit()
        
################################# The program starts here ################################################

if len(sys.argv) <= 3:
    # The input is the genesis block without its hash value.
    genesis = import_json(sys.argv[1])
    check('intended_mining_time_days' in genesis.keys(), 'The provided file is not a valid genesis block.')
    if 'difficulty' not in genesis.keys():
        genesis['difficulty'] = estimate_difficulty(genesis['intended_mining_time_days'])
    if 'miner_name' not in genesis.keys():
        miner_name = sys.argv[2]
        genesis['miner_name'] = miner_name
    genesis_hash = rsa.compute_hash(json.dumps(genesis).encode('utf8'), 'SHA-256').hex()
    genesis = {'block_content': genesis.copy()}
    genesis['hash'] = genesis_hash
    file_name = genesis['block_content']['story_title'].title().replace(' ','')+'_000.json'
    with open(file_name, "w") as outfile:
        outfile.write(json.dumps({'0': genesis}))
    sys.exit()
    
# Import the data to validate
story = import_json(sys.argv[1])
signed_chapter_data = import_json(sys.argv[2])
miner_name = sys.argv[3]

# Check that the chapter data is valid.
genesis = story['0']['block_content']
check(validate_chapter_data(signed_chapter_data, genesis), 'The signed chapter data does not comply with the rules of this story.')

# Check that the number of the provided chapter is one plus the largest block number and extract the previous block.
check(signed_chapter_data['chapter_data']['chapter_number']-1 == max([int(n) for n in story.keys()]), 'The chapter number of the block to add is not the last chapter number of the story.')
previous_block = story[str(signed_chapter_data['chapter_data']['chapter_number']-1)]

# Get the mining date of the previous block and check that it is far enough in the past.
mining_date_previous_block = pytz.utc.localize(dt.datetime.strptime(previous_block['block_content']['mining_date'], '%Y/%m/%d %H:%M:%S'))
story_age_previous_block = previous_block['block_content']['story_age_days']
mining_delay = dt.timedelta(days = genesis['mining_delay_days'])
check(mining_date_previous_block + mining_delay <= dt.datetime.now(tz = pytz.UTC), 'The previous block was mined on the ' + mining_date_previous_block.strftime("%Y/%m/%d, %H:%M:%S")+'. This is less than ' + str(genesis['mining_delay_days']) + ' days ago. This block can\'t be validated right now. Please wait ' + str(mining_date_previous_block + mining_delay - dt.datetime.now(tz = pytz.UTC)) + '.')

# Initialise the new block
new_block = {'signed_chapter_data': signed_chapter_data, 'hash_previous_block': previous_block['hash'], 'hash_eth': get_eth_block_info(mining_date_previous_block + mining_delay), 'miner_name': miner_name}

# Now perform the actual mining!
# It takes about (2)**difficulty tries to find a valid nonce. On my computer, it takes about 0.0002 seconds for each try. difficulty = 21 should take about 10 minutes.
difficulty = previous_block['block_content']['difficulty']
new_block = set_new_block_difficulty_and_mining_date(new_block, genesis, difficulty, mining_date_previous_block, story_age_previous_block)
# Set the hash value below which the block hash has to be. Use powers of 2 so that the difficulty is doubled as difficulty increases by 1.
max_hash = 2**(256-difficulty)-1
print('Start mining! On my computer, it takes about '+str(time_to_mine_days(difficulty)/24)+' hours to complete.')
nb_tries = 1
start_time = pytz.utc.localize(dt.datetime.strptime(new_block['mining_date'], '%Y/%m/%d %H:%M:%S'))
new_block['nb_tries'] = nb_tries
new_block['nonce'] = ''.join(random.choice('0123456789abcdef') for _ in range(64))
new_hash = rsa.compute_hash(json.dumps(new_block).encode('utf8'), 'SHA-256')
while int.from_bytes(new_hash,'big') > max_hash:
    nb_tries += 1
    new_block = set_new_block_difficulty_and_mining_date(new_block, genesis, difficulty, mining_date_previous_block, story_age_previous_block)
    new_block['nb_tries'] = nb_tries
    new_block['nonce'] = ''.join(random.choice('0123456789abcdef') for _ in range(64))
    new_hash = rsa.compute_hash(json.dumps(new_block).encode('utf8'), 'SHA-256')
                           
try_time = dt.datetime.now(tz = pytz.UTC)-start_time
print('The mining took',nb_tries,'tries and',try_time,'. This is',try_time/nb_tries,'per try.')
new_block = {'block_content': new_block.copy()}
new_block['hash'] = new_hash.hex()
story[signed_chapter_data['chapter_data']['chapter_number']] = new_block
new_file_name = story['0']['block_content']['story_title'].title().replace(' ','')+'_'+str(signed_chapter_data['chapter_data']['chapter_number']).rjust(3, '0')+'.json'
with open(new_file_name, "w") as outfile:
    outfile.write(json.dumps(story))