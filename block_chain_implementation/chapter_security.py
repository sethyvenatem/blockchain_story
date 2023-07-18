# -----------------------------------------------------------
# This script does the following:
#    - It checks that the provided chapter data is consistent with the rules set in the genesis block. The genesis block is taken from the validated story if available and from 'genesis_block.json' if not. The files must be placed in the local directory.
#    - It assembles the chapter and associated data is a way that ensures that the text can not be changed (with rsa).
#    - It generates a *.json file with the chapter data together with the digital signature and places it in the local directory.
#    - It generates a *.json file with the private and public keys that were used to sign the chapter data and places it in the local directory.
#    - It generates a readable *.txt file with all the provided chapter data.
#
#The chapter data can be provided in two ways:
#    - Place it in a json file called 'chapter_data.json', put the file in the same directory as the script and call the script with the json argument.
#    - Call the script with no argument. Then the script prompts the user for the necessary information.
#
#
# 15/07/2023 Steven Mathey
# email steven.mathey@gmail.ch
# -----------------------------------------------------------
import json
import warnings
import rsa
import io
import sys
import glob

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

def import_json(file_name, stop_if_fail = True):
    
    try:
        return json.load(open(file_name))
    except:
        if stop_if_fail:
            sys.exit('Something is wrong with '+file_name+'.')
        else:
            warnings.warn('Something is wrong with '+file_name+'.')
            return {}

def write_chapter_to_file(chapter_data):
    # This makes a readable text file with all the data provided by the author.
    
    to_write = [(k.replace('_',' ')+':').title() + ' ' + chapter_data[k]+'\n\n' for k in chapter_data.keys() if k!='text']
    to_write.append('\n\n\n' + chapter_data['text'])
    
    file_name = (chapter_data['story_title'].title().replace(' ','') + '_' + chapter_data['chapter_number'].rjust(3, '0') + '_'+chapter_data['author'].title().replace(' ','')+'.txt')
    
    with open(file_name, "w") as outfile:
        outfile.writelines(to_write)
        
def get_genesis_block(story_title):
    # Get the genesis block. Use the validated blockchain file if available and default to the local file 'genesis_block.json' if not.
    # With the validated blockchain, check the integrity of the genesis block and stop the script if the hash value does not match.
    
    files = glob.glob('*.json')
    files = [x[:-5] for x in files if x.startswith(story_title.title().replace(' ','')+'_')]
    
    if len(files) == 0:
        warnings.warn('The genesis block is not validated.')
        return import_json('genesis_block.json', False)
    
    block_number = max([int(x[-3:]) for x in files])
    file_name = story_title.title().replace(' ','')+'_'+str(block_number).rjust(3, '0')+'.json'
    
    blockchain = import_json(file_name, False)
    
    provided_hash = blockchain['0']['hash']
    genesis = blockchain['0']['block_content']
    genesis_hash = rsa.compute_hash(json.dumps(genesis).encode('utf8'), 'SHA-256').hex()
    
    if genesis_hash == provided_hash:
        return genesis
    
    sys.exit('The genesis block from this file has been tampered with. Don\'t use it.')

def write_secure_chapter_to_file(secure_chapter_data):
    
    chapter_data = secure_chapter_data['chapter_data']
    securefile_name = 'secure_'+chapter_data['story_title'].title().replace(' ','') + '_' + chapter_data['chapter_number'].rjust(3, '0') + '_'+chapter_data['author'].title().replace(' ','')+'.json'
    with open(securefile_name, "w") as outfile:
        outfile.write(json.dumps(secure_chapter_data))
        
################################# The program starts here ################################################
    
# Get the chapter data
if (len(sys.argv)  == 2) and (sys.argv[1] == 'json'):
    chapter_data = import_json('chapter_data.json')
else:
    print('Please provide the chapter data.')
    chapter_data = {}
    chapter_data['story_title'] = input('Story title: ')
    chapter_data['chapter_number'] = input('Chapter number: ')
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
assert check_chapter_data(chapter_data,genesis), 'The chapter data does not comply with the rules of this story.'

# Generate public and private keys
(public_key, private_key) = rsa.newkeys(1024)
# Hash the chapter_data and encrypt it with the private key
encrypted_hashed_chapter = rsa.sign(json.dumps(chapter_data).encode('utf8'), private_key, 'SHA-256')

# Assemble the signed chapter data and save it as a json file
secure_chapter_data = {'chapter_data':chapter_data,'encrypted_hashed_chapter': encrypted_hashed_chapter.hex(),'public_key':public_key.save_pkcs1().hex()}
write_secure_chapter_to_file(secure_chapter_data)

# Save the keys to another json file
public_key = public_key.save_pkcs1().hex()
private_key = private_key.save_pkcs1().hex()
keys = {'public_key': public_key, 'private_key': private_key}
keys = json.dumps(keys)
with open("keys.json", "w") as outfile:
    outfile.write(keys)
    
# generate a single .txt file to read the chapter
write_chapter_to_file(chapter_data)