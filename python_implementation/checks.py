# -----------------------------------------------------------
# Check that a given *.json is right
#
# 01/08/2023 Steven Mathey
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
        print('The signed chapter data has been modified!')
    
    return test

def check_hash(provided_hash,block_content):
    computed_hash = rsa.compute_hash(json.dumps(block_content).encode('utf8'), 'SHA-256').hex()
    
    if computed_hash == provided_hash:
        return True
    return False

def get_genesis_block(story_title):
    # Get the genesis block. Use the validated blockchain file if available and default to the local file 'genesis_block.json' if not.
    # With the validated blockchain, check the integrity of the genesis block and stop the script if the hash value does not match.
    
    story_title = story_title.title().replace(' ','')+'_'
    files = glob.glob('*.json')
    files = [x[:-5] for x in files if x.startswith(story_title)]
    
    if len(files) == 0:
        print('The genesis block is not validated.')
        return import_json('genesis_block.json', False)
    
    block_number = max([int(x[-3:]) for x in files])
    file_name = story_title+str(block_number).rjust(3, '0')+'.json'
    
    blockchain = import_json(file_name, False)
    
    if check_hash(blockchain['0']['hash'],blockchain['0']['block_content']):
        return genesis
    
    sys.exit('The genesis block from this file has been tampered with. Don\'t use it.')
    
def check(statement,message):
    if not(statement):
        print(message)
        sys.exit()

################################# The program starts here ################################################

# The name of the file to check is provided as argument
data = import_json(sys.argv[2])

if set(['story_title', 'chapter_number', 'author', 'chapter_title', 'text']) == set(data.keys()):
    # Unsigned chapter data
    
    genesis = get_genesis_block(data['story_title'])
    if len(genesis) == 0:
        print('You are checking and unsigend chapter and there is no genesis block available. No check is performed.')
        sys.exit(0)

    check(check_chapter_data(data, genesis),'The chapter data does not comply with the rules of this story.')
    print('The submitted unsigned chapter data follows the rules of the story.')
    sys.exit(0)
    
elif set(['chapter_data', 'encrypted_hashed_chapter', 'public_key']) == set(data.keys()):
    # signed chapter data
    
    genesis = get_genesis_block(data['chapter_data']['story_title'])
    check(validate_chapter_data(data, genesis), 'The signed chapter data does not comply with the rules of this story.')
    print('The submitted signed chapter data:')
    print('    - follows the rules of the story.')
    print('    - is signed correctly.')
    sys.exit(0)
    
elif set(['block_content', 'hash']) == set(data.keys()):
    # isolated validated block
    check(check_hash(data['hash'], data['block_content']), 'The hash value of the provided block does not match its data.')
    
    data = data['block_content']
    if 'character_limits' in data.keys():
        # genesis block
        check((data['story_age_days'] == 0.0) and (data['chapter_number'] == 0), 'The chapter number or the story age are not zero.')
        print('The provided genesis block has:')
        print('    - a consistent hash value.')
        print('    - consistent \'chapter_number\' and \'story_age_days\' fields.')
        
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