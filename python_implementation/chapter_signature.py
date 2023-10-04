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
# 04/10/2023 Steven Mathey
# email steven.mathey@gmail.ch
# -----------------------------------------------------------
import json
import rsa
import sys
from blockchain_functions import *

def write_keys_to_file(public_key, private_key, author_name, keys_file_name):
    
    public_key = public_key.save_pkcs1().hex()
    private_key = private_key.save_pkcs1().hex()
    keys = {'public_key': public_key, 'private_key': private_key, 'author': author_name}
    with open(keys_file_name, "w",  encoding='utf-8') as outfile:
        json.dump(keys, outfile, ensure_ascii = False, sort_keys = True)
        
def sign_chapter(file_name):
    
    if type(file_name) == str:
        chapter_data = import_json(file_name)
        if chapter_data == 'error':
            return 'error'
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
            print('The file name must end with \'.txt\'.')
            return 'error'
    
    genesis = get_genesis_block(chapter_data['story_title'])
    if genesis == 'error':
        return 'error'

    # Check that the chapter fits the constraints
    test = check(check_chapter_data(chapter_data, genesis),'The chapter data does not comply with the rules of this story.')
    if test == 'error':
        return 'error'

    # get all json files
    json_files = glob.glob('*.json')
    # keep only the key files
    json_files = [f for f in json_files if set(['public_key', 'private_key', 'author']) == set(import_json(f, False).keys())]
    # get the file with the right author
    json_files = [f for f in json_files if import_json(f, False)['author'] == chapter_data['author']]
    if len(json_files) == 0:
        print('No key file was found. A new private-public key set was generated and saved to the working folder.')
        # Generate public and private keys
        (public_key, private_key) = rsa.newkeys(1024)
        
        # Save the keys to another json file
        keys_file_name = 'keys_'+chapter_data['author'].title().replace(' ','')+'.json'
        write_keys_to_file(public_key, private_key, chapter_data['author'], keys_file_name)
        
        # Hash the chapter_data and encrypt it with the private key
        encrypted_hashed_chapter = rsa.sign(json.dumps(chapter_data, ensure_ascii = False, sort_keys = True).encode('utf8'), private_key, 'SHA-256')
    elif len(json_files) == 1:
        print('A key file was found and used to validate the chapter. The file name is '+json_files[0]+'.')
        key_file = import_json(json_files[0])
        private_key = rsa.PrivateKey.load_pkcs1(bytes.fromhex(key_file['private_key']))
        public_key = rsa.PublicKey.load_pkcs1(bytes.fromhex(key_file['public_key']))
        # Hash the chapter_data and encrypt it with the private key
        encrypted_hashed_chapter = rsa.sign(json.dumps(chapter_data, ensure_ascii = False, sort_keys = True).encode('utf8'), private_key, 'SHA-256')
    else:
        print('Multiple key files with the same author name were found. Clean up the working directory.')
        return 'error'

    # Assemble the signed chapter data and save it as a json file
    signed_chapter_data = {'chapter_data': chapter_data,'encrypted_hashed_chapter': encrypted_hashed_chapter.hex(),'public_key': public_key.save_pkcs1().hex()}
    write_signed_chapter_to_file(signed_chapter_data)

    # generate a single readable *.txt file with the chapter data
    _ = write_chapter_to_readable_file(chapter_data)
    
################################# The program starts here ################################################

if __name__ == "__main__":
    if len(sys.argv) == 2:
        file_name = sys.argv[1]
    else:
        file_name = None

    status = sign_chapter(file_name)
    print(status)