# -----------------------------------------------------------
# Check that a given *.json is right
#
# 07/09/2023 Steven Mathey
# email steven.mathey@gmail.ch
# -----------------------------------------------------------

import json
#import rsa
#import io
import datetime as dt
import sys
#from web3 import Web3, AsyncWeb3
import pytz
import numpy as np
#import glob
from blockchain_functions import *
        
def get_difficulty(genesis, block, previous_block):

    mining_delay = dt.timedelta(days = genesis['mining_delay_days'])
    intended_mining_time = dt.timedelta(days = genesis['intended_mining_time_days'])
    grace = 0.25*intended_mining_time
    mining_date = pytz.utc.localize(dt.datetime.strptime(block['mining_date'], '%Y/%m/%d %H:%M:%S'))
    previous_mining_date = pytz.utc.localize(dt.datetime.strptime(previous_block['mining_date'], '%Y/%m/%d %H:%M:%S'))

    if mining_date > previous_mining_date + mining_delay + intended_mining_time + grace:
        return previous_block['difficulty'] - 1
    elif mining_date < previous_mining_date + mining_delay + intended_mining_time - grace:
        return previous_block['difficulty'] + 1
    return previous_block['difficulty']

################################# The program starts here ################################################

# The name of the file to check is provided as argument
data = import_json(sys.argv[1])

if set(['story_title', 'chapter_number', 'author', 'chapter_title', 'text']) == set(data.keys()):
    # Unsigned chapter data
    
    genesis = get_genesis_block(data['story_title'])
    if len(genesis) == 0:
        print('You are checking and unsigend chapter and there is no genesis block available. No check is performed.')
        write_chapter_to_readable_file(data)
        input('Press enter to end.')
        sys.exit(0)

    check(check_chapter_data(data, genesis),'The chapter data does not comply with the rules of this story.')
    print('The submitted unsigned chapter data follows the rules of the story.')
    write_chapter_to_readable_file(data)
    input('Press enter to end.')
    sys.exit(0)
    
elif set(['chapter_data', 'encrypted_hashed_chapter', 'public_key']) == set(data.keys()):
    # signed chapter data
    
    genesis = get_genesis_block(data['chapter_data']['story_title'])
    check(validate_chapter_data(data, genesis), 'The signed chapter data does not comply with the rules of this story.')
    print('The submitted signed chapter data:')
    if len(genesis) > 0:
        print('    - follows the rules of the story.')
    print('    - is signed correctly.')
    write_chapter_to_readable_file(data['chapter_data'])
    input('Press enter to end.')
    sys.exit(0)
    
elif set(['block_content', 'hash']) == set(data.keys()):
    # isolated validated block
    check(check_hash(data['hash'], data['block_content']), 'The hash value of the provided block does not match its data.')
    
    data = data['block_content']
    if 'character_limits' in data.keys():
        # genesis block
        check(data['chapter_number'] == 0, 'The chapter number is not zero.')
        check(data['story_age_seconds'] == 0.0, 'The story age is not zero.')
        print('The provided genesis block has:')
        print('    - a consistent hash value.')
        print('    - consistent \'chapter_number\' and \'story_age_seconds\' fields.')
        print()
        input('Press enter to end.')
        sys.exit(0)
        
    elif 'signed_chapter_data' in data.keys():
        # normal block
        genesis = get_genesis_block(data['signed_chapter_data']['chapter_data']['story_title'])
        check(validate_chapter_data(data['signed_chapter_data'], genesis), 'The signed chapter data does not comply with the rules of this story.')
        print('The provided isolated block has:')
        print('    - a consistent hash value.')
        if len(genesis) > 0:
            print('    - \'chapter_data\' that is consistent with the genesis bock.')
        print('    - consistently signed \'chapter_data\'.')
        write_chapter_to_readable_file(data['signed_chapter_data']['chapter_data'])
        print()
        input('Press enter to end.')
        sys.exit()
        
elif all([x.isdigit() for x in data.keys()]):
    # full story
    
    check('0' in data.keys(), 'The genesis block is absent from the submitted story.')
    
    block_numbers = np.array([int(k) for k in data.keys()])
    block_numbers.sort()
    check((block_numbers == np.arange(len(data))).all(), 'At least one block is missing from the submitted story.')

    # genesis block
    genesis = data['0']
    check(check_hash(genesis['hash'], genesis['block_content']), 'The hash value of the genesis block does not match its data.')
    genesis = genesis['block_content']
    check(genesis['chapter_number'] == 0, 'The chapter number is not zero in the genesis block.')
    check(genesis['story_age_seconds'] == 0.0, 'The story age is not zero in the genesis block.')
    
    to_write = ['Story title: '+genesis['story_title']+'\n\n\n\n\n\n']
    block_number = 0
    for block_number in range(1,len(data)):
        # Chapter blocks
        
        block = data[str(block_number)]
        previous_block = data[str(block_number-1)]
        
        check(check_hash(block['hash'], block['block_content']), 'The hash value of block '+str(block_number)+' does not match its data.')
        
        max_hash = 2**(256-previous_block['block_content']['difficulty'])-1
        check(int.from_bytes(bytes.fromhex(block['hash']),'big') <= max_hash, 'The hash value of block '+str(block_number)+' is not consistent with the difficulty setting.')
        
        check(block['block_content']['hash_previous_block'] == previous_block['hash'], 'The hash of block '+str(block_number-1)+' does not match the \'hash_previous_block\' field of block '+str(block_number)+'.')
        
        block = block['block_content']
        previous_block = previous_block['block_content']
        
        earliest_mining_date = pytz.utc.localize(dt.datetime.strptime(previous_block['mining_date'], '%Y/%m/%d %H:%M:%S')) + dt.timedelta(days = genesis['mining_delay_days'])
        check(earliest_mining_date <= pytz.utc.localize(dt.datetime.strptime(block['mining_date'], '%Y/%m/%d %H:%M:%S')), 'The mining date of block '+str(block_number)+' is not consistent with the set mining delay.')
        
        check(get_eth_block_info(earliest_mining_date) == block['hash_eth'], 'The \'hash_eth\' field of block '+str(block_number)+' does not match the right ETH block.')
        
        check(previous_block['story_age_seconds'] + round((pytz.utc.localize(dt.datetime.strptime(block['mining_date'], '%Y/%m/%d %H:%M:%S'))-pytz.utc.localize(dt.datetime.strptime(genesis['mining_date'], '%Y/%m/%d %H:%M:%S'))).total_seconds()) == block['story_age_seconds'], 'The story age of block '+str(block_number)+' is not calculated correctly.')
        
        check(get_difficulty(genesis, block, previous_block) == block['difficulty'], 'The difficulty of block '+str(block_number)+' was not calculated correctly.')
        
        block = block['signed_chapter_data']
        
        check(validate_chapter_data(block, genesis), 'The signed chapter data of block '+str(block_number)+' does not comply with the rules of this story.')
        
        block = block['chapter_data']
        
        check(block['story_title'] == genesis['story_title'], 'The chapter title of block '+str(block_number)+' does not match the title in the genesis block.')
        
        check(block['chapter_number'] == block_number, 'The chapter number of block '+str(block_number)+' is not '+str(block_number)+'.')
        
        to_write = to_write + ([(k.replace('_',' ')+':').title() + ' ' + str(block[k])+'\n\n' for k in block.keys() if (k!='text') and (k!='story_title')])
        to_write.append('\n' + block['text'] + '\n\n\n\n\n\n')
    
    if block_number > 0:
        
        print('Each block of the provided story has:')
        print('    - consistent hash values.')
        print('    - consistent chapter numbering.')
        print('    - consistent \'story_age_seconds\' fields.')
        print('    - the hash value of the right ETH block.')
        print('    - a \'signed_chapter_data\' field with a consistent digital signature.')
        print('    - a \'chapter_data\' that is consistent with the genesis bock.')
        print()
        print('The blocks are correctly linked to each other:')
        print('    - Each block correctly references the hash of the previous block.')
        print('    - All the reported \'mining_date\' fields are consistent.')
        print('    - All the reported \'difficulty\' fields are set correctly.')
        print('    - Each block hash value conform to the difficulty set by the previous block.')
        
        if genesis['number_of_chapters'] == block_number:
            to_write.append('\n\nThe end.')
    
        file_name = genesis['story_title'].title().replace(' ','') + '_' + str(block_number).rjust(3, '0') +'.txt'
        with open(file_name, "w") as outfile:
            outfile.writelines(to_write)
        print('The full story up until now was saved in an easily readable form in the working directory in '+file_name+'.')
        
    else:
        print('The provided genesis block has:')
        print('    - a consistent hash value.')
        print('    - consistent chapter numbering.')
        print('    - consistent \'story_age_seconds\' fields.')
        
else:
    print('The submitted file is not recognised.')