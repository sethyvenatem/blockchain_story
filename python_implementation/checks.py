# -----------------------------------------------------------
# Check that a given *.json is right
#
# 29/08/2023 Steven Mathey
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
import glob

def import_json(file_name, stop_if_fail = True):

    if file_name[-5:].lower() != '.json':
        print('The file name ('+file_name+') must end with \'.json\'.')
        input('Press enter to end.')
        sys.exit()
        
    try:
        return json.load(open(file_name))
    except:
        if stop_if_fail:
            if file_name in glob.glob('*.json'):
                print('Something is wrong withe the *.json file.')
                input('Press enter to end.')
                sys.exit(0)
            else:
                print('Could not find '+file_name+'.')
                input('Press enter to end.')
                sys.exit(0)
        else:
            if file_name in glob.glob('*.json'):
                print('Something is wrong withe the *.json file.')
            else:
                print('Could not find '+file_name+'.')
            return {}
        
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
    
    files = [x for x in files if x.startswith(story_title)]
    if len(files) == 0:
        print('The genesis block is not validated. Using the file \'genesis_block.json\'.')
        return import_json('genesis_block.json', False)
    
    file_index = np.argmax(np.array([int(x[len(story_title):len(story_title)+3]) for x in files]))
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
    input('Press enter to end.')
    sys.exit()
    
def check(statement,message):
    # This function works like the assert statement, but does not raise an error. It just prints a message and terminates the script.
    
    if not(statement):
        print(message)
        input('Press enter to end.')
        sys.exit()

def write_chapter_to_readable_file(chapter_data):
    # This makes a readable text file with all the data provided by the author.
    
    to_write = [(k.replace('_',' ')+':').title() + ' ' + str(chapter_data[k])+'\n\n' for k in chapter_data.keys() if k!='text']
    to_write.append('\n\n\n' + chapter_data['text'])
    
    file_name = (chapter_data['story_title'].title().replace(' ','') + '_' + str(chapter_data['chapter_number']).rjust(3, '0') + '_'+chapter_data['author'].title().replace(' ','')+'.txt')
    
    with open(file_name, "w") as outfile:
        outfile.writelines(to_write)
        
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
            input('Press enter to end.')
            sys.exit(0)
        
    if w3.eth.get_block('finalized').number < target_block:
        # If the obtained block number is larger than the last finalised block number, then warn the user.
        print('The ETH block is not finalised yet. Wait about 15 minutes to be sure to mine effectively.')
        
    return w3.eth.get_block(target_block).hash.hex()
        
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

def get_now():
    # This function constructs a datetime object for right now, UTC time zone and the seconds rounded to the closest integer.
    # Thanks stack overflow: https://stackoverflow.com/questions/47792242/rounding-time-off-to-the-nearest-second-python
    
    now = dt.datetime.now(tz = pytz.UTC)
    if now.microsecond >= 500000:
        now = now + dt.timedelta(seconds = 1)
    
    return now.replace(microsecond = 0)

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