# This script does the following:
#    - It checks that the provided chapter data is consistent with the rules set in the genesis block. The genesis block is taken from the validated story if available and from 'genesis_block.json' if not. The files must be placed in the local directory.
#    - It assembles the chapter and associated data is a way that ensures that the text can not be changed (with rsa).
#    - It generates a *.json file with the chapter data together with the digital signature and places it in the local directory.
#    - It generates a *.json file with the private and public keys that were used to sign the chapter data and places it in the local directory.
#    - It generates a readable *.txt file with all the provided chapter data.
#
#The chapter data can be provided in two ways:
#    - Place it in a json file, put the file in the same directory as the script and call the script with the name of the file as argument. The json file must have the following fields: 'story_title', 'chapter_number', 'author', 'chapter_title' and 'text'. The 'chapter_number' value must be an integer. The other field values are strings. New lines must be indicated by '\n'.
#    - Call the script with no argument. Then the script prompts the user for the necessary information. The user will be prompted to provide a file name for the text of the chapter. This text must be placed in a *.txt file in the same directory as the script. Line returns are then handled by the *.txt format and converted to '\n' by the script.
#
#
# 06/08/2023 Steven Mathey
# email steven.mathey@gmail.ch
# -----------------------------------------------------------
import json
import rsa
import io
import sys
import glob
import numpy as np

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
        sys.exit('The file name ('+file_name+') must end with \'.json\'.')
        
    try:
        return json.load(open(file_name))
    except:
        if stop_if_fail:
            if file_name in glob.glob('*.json'):
                print('Something is wrong withe the *.json file.')
                sys.exit(0)
            else:
                print('Could not find '+file_name+'.')
                sys.exit(0)
        else:
            if file_name in glob.glob('*.json'):
                print('Something is wrong withe the *.json file.')
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
        
def get_genesis_block(story_title):
    # Get the genesis block. Use the validated blockchain file if available and default to the local file 'genesis_block.json' if not.
    # With the validated blockchain, check the integrity of the genesis block and stop the script if the hash value does not match.
    
    story_title = story_title.title().replace(' ','')+'_'
    files = glob.glob('*.json')
    files = [x[:-5] for x in files if x.startswith(story_title)]
    
    if len(files) == 0:
        print('The genesis block is not validated. Using the file \'genesis_block.json\'.')
        return import_json('genesis_block.json', False)
    
    try:
        block_number = max([int(x[len(story_title):len(story_title)+3]) for x in files])
        file_name = story_title+str(block_number).rjust(3, '0')+'.json'

        blockchain = import_json(file_name, False)

        if check_hash(blockchain['0']['hash'],blockchain['0']['block_content']):
            print('Using the genesis block from \''+file_name+'\'.')
            return blockchain['0']['block_content']
        
    except:
        print('The genesis block is not validated. Using the file \'genesis_block.json\'.')
        return import_json('genesis_block.json', False)
    
    sys.exit('The genesis block from this file has been tampered with. Don\'t use it.')

def write_signed_chapter_to_file(signed_chapter_data):
    
    chapter_data = signed_chapter_data['chapter_data']
    signed_file_name = 'signed_'+chapter_data['story_title'].title().replace(' ','') + '_' + str(chapter_data['chapter_number']).rjust(3, '0') + '_'+chapter_data['author'].title().replace(' ','')+'.json'
    with open(signed_file_name, "w") as outfile:
        outfile.write(json.dumps(signed_chapter_data))

def write_keys_to_file(public_key,private_key):
    
    public_key = public_key.save_pkcs1().hex()
    private_key = private_key.save_pkcs1().hex()
    keys = {'public_key': public_key, 'private_key': private_key}
    keys_file_name = 'keys_'+chapter_data['story_title'].title().replace(' ','') + '_' + str(chapter_data['chapter_number']).rjust(3, '0') + '_'+chapter_data['author'].title().replace(' ','')+'.json'
    with open(keys_file_name, "w") as outfile:
        outfile.write(json.dumps(keys))

def check(statement,message):
    # This function works like the assert statement, but does not raise an error. It just prints a message and terminates the script.
    
    if not(statement):
        print(message)
        sys.exit()
        
def check_hash(provided_hash,block_content):
    computed_hash = rsa.compute_hash(json.dumps(block_content).encode('utf8'), 'SHA-256').hex()
    
    if computed_hash == provided_hash:
        return True
    return False

################################# The program starts here ################################################
    
# Get the chapter data
if (len(sys.argv)  == 2):
    file_name = sys.argv[1]
    chapter_data = import_json(file_name)
else:
    print('Please provide the chapter data.')
    chapter_data = {}
    chapter_data['story_title'] = input('Story title: ')
    chapter_data['chapter_number'] = int(input('Chapter number: '))
    chapter_data['author'] = input('Author name: ')
    chapter_data['chapter_title'] = input('Chapter title: ')
    text_file_name = input('File name for the chapter text (use a *.txt file): ')
    if text_file_name[-4:].lower() == '.txt':
        with open(text_file_name, 'r') as infile:
            chapter_data['text'] = infile.read()
    else:
        sys.exit('The file name must end with \'.txt\'.')

genesis = get_genesis_block(chapter_data['story_title'])

# Check that the chapter fits the constraints
check(check_chapter_data(chapter_data, genesis),'The chapter data does not comply with the rules of this story.')

# Generate public and private keys
(public_key, private_key) = rsa.newkeys(1024)
# Hash the chapter_data and encrypt it with the private key
encrypted_hashed_chapter = rsa.sign(json.dumps(chapter_data).encode('utf8'), private_key, 'SHA-256')

# Assemble the signed chapter data and save it as a json file
signed_chapter_data = {'chapter_data': chapter_data,'encrypted_hashed_chapter': encrypted_hashed_chapter.hex(),'public_key': public_key.save_pkcs1().hex()}
write_signed_chapter_to_file(signed_chapter_data)

# Save the keys to another json file
write_keys_to_file(public_key,private_key)
    
# generate a single readable *.txt file with the chapter data
write_chapter_to_readable_file(chapter_data)