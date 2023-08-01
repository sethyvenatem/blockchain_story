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

def write_chapter_to_readable_file(chapter_data):
    # This makes a readable text file with all the data provided by the author.
    
    to_write = [(k.replace('_',' ')+':').title() + ' ' + str(chapter_data[k])+'\n\n' for k in chapter_data.keys() if k!='text']
    to_write.append('\n\n\n' + chapter_data['text'])
    
    file_name = (chapter_data['story_title'].title().replace(' ','') + '_' + str(chapter_data['chapter_number']).rjust(3, '0') + '_'+chapter_data['author'].title().replace(' ','')+'.txt')
    
    with open(file_name, "w") as outfile:
        outfile.writelines(to_write)
        
################################# The program starts here ################################################

# The name of the file to check is provided as argument
data = import_json(sys.argv[2])

if set(['story_title', 'chapter_number', 'author', 'chapter_title', 'text']) == set(data.keys()):
    # Unsigned chapter data
    
    genesis = get_genesis_block(data['story_title'])
    if len(genesis) == 0:
        print('You are checking and unsigend chapter and there is no genesis block available. No check is performed.')
        write_chapter_to_readable_file(data)
        sys.exit(0)

    check(check_chapter_data(data, genesis),'The chapter data does not comply with the rules of this story.')
    print('The submitted unsigned chapter data follows the rules of the story.')
    write_chapter_to_readable_file(data)
    sys.exit(0)
    
elif set(['chapter_data', 'encrypted_hashed_chapter', 'public_key']) == set(data.keys()):
    # signed chapter data
    
    genesis = get_genesis_block(data['chapter_data']['story_title'])
    check(validate_chapter_data(data, genesis), 'The signed chapter data does not comply with the rules of this story.')
    print('The submitted signed chapter data:')
    print('    - follows the rules of the story.')
    print('    - is signed correctly.')
    write_chapter_to_readable_file(data['chapter_data'])
    sys.exit(0)
    
elif set(['block_content', 'hash']) == set(data.keys()):
    # isolated validated block
    check(check_hash(data['hash'], data['block_content']), 'The hash value of the provided block does not match its data.')
    
    data = data['block_content']
    if 'character_limits' in data.keys():
        # genesis block
        check(data['chapter_number'] == 0, 'The chapter number is not zero.')
        check(data['story_age_days'] == 0.0, 'The story age is not zero.')
        print('The provided genesis block has:')
        print('    - a consistent hash value.')
        print('    - consistent \'chapter_number\' and \'story_age_days\' fields.')
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
        sys.exit()
        
elif all([x.isdigit() for x in data.keys()]):
    # full story
    
    # genesis block
    genesis = data['0']
    check(check_hash(genesis['hash'], genesis['block_content']), 'The hash value of the genesis block does not match its data.')
    genesis = genesis['block_content']
    check(genesis['chapter_number'] == 0, 'The chapter number is not zero in the genesis block.')
    check(genesis['story_age_days'] == 0.0, 'The story age is not zero in the genesis block.')
    
    for block_number in range(1,len(data)):
        block = data[str(block_number)]
        
        
        