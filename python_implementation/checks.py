# -----------------------------------------------------------
# Check that a given *.json is right
#
# 12/09/2023 Steven Mathey
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

def check_file(file_name):

    data = import_json(file_name)
    if data == 'error':
        return 'error'

    if set(['story_title', 'chapter_number', 'author', 'chapter_title', 'text']) == set(data.keys()):
        # Unsigned chapter data

        genesis = get_genesis_block(data['story_title'])
        if genesis == 'error':
            return 'error'
        if len(genesis) == 0:
            print('You are checking and unsigend chapter and there is no genesis block available. No check is performed.')
            output_file = write_chapter_to_readable_file(data)
            return output_file
        
        test = check(check_chapter_data(data, genesis),'The chapter data does not comply with the rules of this story.')
        if test == 'error':
            return 'error'
        print('The submitted unsigned chapter data follows the rules of the story.')
        output_file = write_chapter_to_readable_file(data)
        return output_file

    elif set(['chapter_data', 'encrypted_hashed_chapter', 'public_key']) == set(data.keys()):
        # signed chapter data

        genesis = get_genesis_block(data['chapter_data']['story_title'])
        if genesis == 'error':
            return 'error'
        test = check(validate_chapter_data(data, genesis), 'The signed chapter data does not comply with the rules of this story.')
        if test == 'error':
            return 'error'
        print('The submitted signed chapter data:')
        if len(genesis) > 0:
            print('    - follows the rules of the story.')
        print('    - is signed correctly.')
        output_file = write_chapter_to_readable_file(data['chapter_data'])
        return output_file

    elif set(['block_content', 'hash']) == set(data.keys()):
        # isolated validated block
        test = check(check_hash(data['hash'], data['block_content']), 'The hash value of the provided block does not match its data.')
        if test == 'error':
            return 'error'

        data = data['block_content']
        if 'character_limits' in data.keys():
            # genesis block
            check(data['chapter_number'] == 0, 'The chapter number is not zero.')
            check(data['story_age_seconds'] == 0.0, 'The story age is not zero.')
            print('The provided genesis block has:')
            print('    - a consistent hash value.')
            print('    - consistent \'chapter_number\' and \'story_age_seconds\' fields.')
            print()
            return 'check_genesis'

        elif 'signed_chapter_data' in data.keys():
            # normal block
            genesis = get_genesis_block(data['signed_chapter_data']['chapter_data']['story_title'])
            if genesis == 'error':
                return 'error'
            test = check(validate_chapter_data(data['signed_chapter_data'], genesis), 'The signed chapter data does not comply with the rules of this story.')
            if test == 'error':
                return 'error'
            print('The provided isolated block has:')
            print('    - a consistent hash value.')
            if len(genesis) > 0:
                print('    - \'chapter_data\' that is consistent with the genesis bock.')
            print('    - consistently signed \'chapter_data\'.')
            output_file = write_chapter_to_readable_file(data['signed_chapter_data']['chapter_data'])
            print()
            return output_file

    elif all([x.isdigit() for x in data.keys()]):
        # full story

        test = check('0' in data.keys(), 'The genesis block is absent from the submitted story.')
        if test == 'error':
            return 'error'

        block_numbers = np.array([int(k) for k in data.keys()])
        block_numbers.sort()
        test = check((block_numbers == np.arange(len(data))).all(), 'At least one block is missing from the submitted story.')
        if test == 'error':
            return 'error'

        # genesis block
        genesis = data['0']
        test = check(check_hash(genesis['hash'], genesis['block_content']), 'The hash value of the genesis block does not match its data.')
        if test == 'error':
            return 'error'
        genesis = genesis['block_content']
        test = check(genesis['chapter_number'] == 0, 'The chapter number is not zero in the genesis block.')
        if test == 'error':
            return 'error'
        test = check(genesis['story_age_seconds'] == 0.0, 'The story age is not zero in the genesis block.')
        if test == 'error':
            return 'error'

        to_write = ['Story title: '+genesis['story_title']+'\n\n\n\n\n\n']
        block_number = 0
        for block_number in range(1,len(data)):
            # Chapter blocks

            block = data[str(block_number)]
            previous_block = data[str(block_number-1)]

            test = check(check_hash(block['hash'], block['block_content']), 'The hash value of block '+str(block_number)+' does not match its data.')
            if test == 'error':
                return 'error'

            max_hash = 2**(256-previous_block['block_content']['difficulty'])-1
            test = check(int.from_bytes(bytes.fromhex(block['hash']),'big') <= max_hash, 'The hash value of block '+str(block_number)+' is not consistent with the difficulty setting.')
            if test == 'error':
                return 'error'

            test = check(block['block_content']['hash_previous_block'] == previous_block['hash'], 'The hash of block '+str(block_number-1)+' does not match the \'hash_previous_block\' field of block '+str(block_number)+'.')
            if test == 'error':
                return 'error'

            block = block['block_content']
            previous_block = previous_block['block_content']

            earliest_mining_date = pytz.utc.localize(dt.datetime.strptime(previous_block['mining_date'], '%Y/%m/%d %H:%M:%S')) + dt.timedelta(days = genesis['mining_delay_days'])
            test = check(earliest_mining_date <= pytz.utc.localize(dt.datetime.strptime(block['mining_date'], '%Y/%m/%d %H:%M:%S')), 'The mining date of block '+str(block_number)+' is not consistent with the set mining delay.')
            if test == 'error':
                return 'error'

            test = check(get_eth_block_info(earliest_mining_date) == block['hash_eth'], 'The \'hash_eth\' field of block '+str(block_number)+' does not match the right ETH block.')
            if test == 'error':
                return 'error'

            test = check(previous_block['story_age_seconds'] + round((pytz.utc.localize(dt.datetime.strptime(block['mining_date'], '%Y/%m/%d %H:%M:%S'))-pytz.utc.localize(dt.datetime.strptime(genesis['mining_date'], '%Y/%m/%d %H:%M:%S'))).total_seconds()) == block['story_age_seconds'], 'The story age of block '+str(block_number)+' is not calculated correctly.')
            if test == 'error':
                return 'error'

            test = check(get_difficulty(genesis, block, previous_block) == block['difficulty'], 'The difficulty of block '+str(block_number)+' was not calculated correctly.')
            if test == 'error':
                return 'error'

            block = block['signed_chapter_data']

            test = check(validate_chapter_data(block, genesis), 'The signed chapter data of block '+str(block_number)+' does not comply with the rules of this story.')
            if test == 'error':
                return 'error'

            block = block['chapter_data']

            test = check(block['story_title'] == genesis['story_title'], 'The chapter title of block '+str(block_number)+' does not match the title in the genesis block.')
            if test == 'error':
                return 'error'

            test = check(block['chapter_number'] == block_number, 'The chapter number of block '+str(block_number)+' is not '+str(block_number)+'.')
            if test == 'error':
                return 'error'

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

            output_file = genesis['story_title'].title().replace(' ','') + '_' + str(block_number).rjust(3, '0') +'.txt'
            with open(output_file, "w") as outfile:
                outfile.writelines(to_write)
            print('The full story up until now was saved in an easily readable form in the working directory in '+output_file+'.')
            
            return output_file

        else:
            print('The provided genesis block has:')
            print('    - a consistent hash value.')
            print('    - consistent chapter numbering.')
            print('    - consistent \'story_age_seconds\' fields.')
            
            return 'check_genesis'

    else:
        print('The submitted file is not recognised.')
        
        return 'error'
        
################################# The program starts here ################################################

if __name__ == "__main__":
    file_name = sys.argv[1]
    status = check_file(file_name)
    print(status)