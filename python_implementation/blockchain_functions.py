# -----------------------------------------------------------
# List of functions used by the other scripts
#
# 15/09/2023 Steven Mathey
# email steven.mathey@gmail.ch
# -----------------------------------------------------------

import json
import rsa
import sys
import glob
import numpy as np
import datetime as dt
from web3 import Web3, AsyncWeb3
import pytz

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
        
    if genesis.get('story_title', chapter_data['story_title']) != chapter_data['story_title']:
        print('The story title does not correspond to the one in the genesis block.')
        test = False
        
    return test

def import_json(file_name, stop_if_fail = True):

    if file_name[-5:].lower() != '.json':
        print('The file name ('+file_name+') must end with \'.json\'.')
        return 'error'
        
    try:
        with open(file_name, encoding='utf-8') as file:
            json_data = json.load(file)
        return json_data

    except:
        if stop_if_fail:
            if file_name in glob.glob('*.json'):
                print('Something is wrong withe '+file_name+'.')
                return 'error'
            else:
                print('Could not find '+file_name+'.')
                return 'error'
        else:
            if file_name in glob.glob('*.json'):
                print('Something is wrong withe '+file_name+'.')
            else:
                print('Could not find '+file_name+'.')
            return {}
            
def write_chapter_to_readable_file(chapter_data):
    # This makes a readable text file with all the data provided by the author.
    
    to_write = [(k.replace('_',' ')+':').title() + ' ' + str(chapter_data[k])+'\n\n' for k in chapter_data.keys() if k!='text']
    to_write.append('\n\n\n' + chapter_data['text'])
    
    file_name = (chapter_data['story_title'].title().replace(' ','') + '_' + str(chapter_data['chapter_number']).rjust(3, '0') + '_'+chapter_data['author'].title().replace(' ','')+'.txt')
    
    with open(file_name, "w") as outfile:
        outfile.writelines(to_write)
    
    print('The chapter content was saved in an easily readable form in the working directory in '+file_name+'.')
    
    return file_name
        
def get_genesis_block(story_title):
    # Get the genesis block. Use the validated blockchain file if available and default to the local file 'genesis_block.json' if not.
    # With the validated blockchain, check the integrity of the genesis block and stop the script if the hash value does not match.
    
    files = glob.glob('*.json')
    
    files = [f for f in files if (all([x.isdigit() for x in import_json(f, False).keys()]) and (len(import_json(f, False)) != 0))]
    files = [f for f in files if import_json(f)['0']['block_content']['story_title'] == story_title]
    
    if len(files) == 0:
        print('The genesis block is not validated. Using the file \'genesis_block.json\'.')
        return import_json('genesis_block.json', False)
    
    file_index = np.argmax(np.array([max([int(x) for x in import_json(f).keys()]) for f in files]))
    file_name = files[file_index]
    try:
        blockchain = import_json(file_name, False)
        if check_hash(blockchain['0']['hash'],blockchain['0']['block_content']):
            print('Using the genesis block from \''+file_name+'\'.')
            return blockchain['0']['block_content']

    except:
        print('The genesis block is not validated. Using the file \'genesis_block.json\'.')
        return import_json('genesis_block.json', False)
    
    print('The genesis block from this file has been tampered with. Don\'t use it.')
    return 'error'

def write_signed_chapter_to_file(signed_chapter_data):
    
    chapter_data = signed_chapter_data['chapter_data']
    signed_file_name = 'signed_'+chapter_data['story_title'].title().replace(' ','') + '_' + str(chapter_data['chapter_number']).rjust(3, '0') + '_'+chapter_data['author'].title().replace(' ','')+'.json'
    with open(signed_file_name, "w",  encoding='utf-8') as outfile:
        json.dump(signed_chapter_data, outfile, ensure_ascii = False, sort_keys = True)
        
    print('The signed chapter data was saved in the working directory in '+signed_file_name+'.')

def check(statement,message):
    # This function works like the assert statement, but does not raise an error. It just prints a message and terminates the script.
    
    if not(statement):
        print(message)
        return 'error'
        #sys.exit()
        
def check_hash(provided_hash,block_content):
    computed_hash = rsa.compute_hash(json.dumps(block_content, ensure_ascii = False, sort_keys = True).encode('utf8'), 'SHA-256').hex()
    
    if computed_hash == provided_hash:
        return True
    return False

def validate_chapter_data(signed_chapter_data, genesis):
    # This validates the signed chapter data. It checks:
    #    - that the chapter data complies with the rules of the genesis block.
    #    - that the digital signature of the signed chapter data is right.
    
    test = check_chapter_data(signed_chapter_data['chapter_data'], genesis)
    
    clear_chapter_data = json.dumps(signed_chapter_data['chapter_data'], ensure_ascii = False, sort_keys = True).encode('utf8')
    encrypted_hashed_chapter = bytes.fromhex(signed_chapter_data['encrypted_hashed_chapter'])
    public_key = rsa.PublicKey.load_pkcs1(bytes.fromhex(signed_chapter_data['public_key']))
    try:
        temp = rsa.verify(clear_chapter_data, encrypted_hashed_chapter, public_key) == 'SHA-256'
    except:
        test = False
        print('The signed chapter data has been modified.')
    
    return test

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

    start_time = get_now()
    approx_nb_blocks = int(np.ceil((start_time-target_date).total_seconds()/(12.5)))
    latest_block = w3.eth.get_block('latest').number
    target_block = latest_block - approx_nb_blocks
    block_timestamp = pytz.utc.localize(dt.datetime.utcfromtimestamp(w3.eth.get_block(target_block).timestamp))

    while (block_timestamp > target_date) & (get_now() < start_time+dt.timedelta(minutes = 5)):
        # stop if the function iterates for more than 5 minutes.
        approx_nb_blocks = int(np.ceil((block_timestamp-target_date).total_seconds()/(12.5)))
        target_block = target_block - approx_nb_blocks
        block_timestamp = pytz.utc.localize(dt.datetime.utcfromtimestamp(w3.eth.get_block(target_block).timestamp))
    target_block += 1
    
    if (pytz.utc.localize(dt.datetime.utcfromtimestamp(w3.eth.get_block(target_block).timestamp)) < target_date):
        # If we overshoot, come back one block at a time. This should only happen when a block is missing close to the target time.
        while (pytz.utc.localize(dt.datetime.utcfromtimestamp(w3.eth.get_block(target_block).timestamp)) < target_date):
            target_block += 1
    
    if ((get_now() > start_time+dt.timedelta(minutes = 5)) or
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
            return 'error'
            #sys.exit(0)
        
    if w3.eth.get_block('finalized').number < target_block:
        # If the obtained block number is larger than the last finalised block number, then warn the user.
        print('The ETH block is not finalised yet. Wait about 15 minutes to be sure to mine effectively.')
        
    return w3.eth.get_block(target_block).hash.hex()

def get_now():
    # This function constructs a datetime object for right now, UTC time zone and the seconds rounded to the closest integer.
    # Thanks: stack overflow: https://stackoverflow.com/questions/47792242/rounding-time-off-to-the-nearest-second-python
    
    now = dt.datetime.now(tz = pytz.UTC)
    if now.microsecond >= 500000:
        now = now + dt.timedelta(seconds = 1)
    
    return now.replace(microsecond = 0)