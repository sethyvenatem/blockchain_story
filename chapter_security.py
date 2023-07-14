# -----------------------------------------------------------
# Put together the chapter and associated data is a way that ensures that the text can not be changed.
#
# 09/07/2023 Steven Mathey
# email steven.mathey@gmail.ch
# -----------------------------------------------------------
import json
import warnings
import rsa
import io
import sys

def check_chapter_data(chapter_data,genesis):
    test = True
    for key in genesis['character_limits'].keys():
        if len(chapter_data[key]) > genesis['character_limits'][key]:
            warnings.warn('The field '+key+' can only contain '+str(genesis['character_limits'][key])+' characters. It must be shortened before it can be added to the story.')
            test = False
    if int(genesis.get('number_of_chapters',10**10)) < int(chapter_data['chapter_number']):
        # Only test that the chapter number is not too large if the field is present in the genesis block. 10**10 is just a huge number. I don't expect and story to ever reach that number of chapters.
        warnings.warn('This story can only have '+str(genesis['number_of_chapters'])+' chapters.')
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
    to_write = [(k.replace('_',' ')+':').title() + ' ' + chapter_data[k]+'\n\n' for k in chapter_data.keys() if k!='text']
    to_write.append('\n\n\n' + chapter_data['text'])
    
    file_name = (chapter_data['story_title'].title().replace(' ','') + '_' + chapter_data['chapter_number'].rjust(3, '0') + '_'+chapter_data['author'].title().replace(' ','')+'.txt')
    
    with open(file_name, "w") as outfile:
        outfile.writelines(to_write)
        
################################# The program starts here ################################################
    
# Get the chapter data and constraints
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
            
genesis = import_json('genesis_block.json', False)
    
# Check that the chapter fits the constraints
assert check_chapter_data(chapter_data,genesis), 'The chapter data does not comply with the rules of this story.'

# Generate public and private keys
(public_key, private_key) = rsa.newkeys(1024)
# Hash the chapter_data and encrypt it with the private key
encrypted_hashed_chapter = rsa.sign(json.dumps(chapter_data).encode('utf8'), private_key, 'SHA-256')

# Assemble the signed chapter data and save it as a json file
secure_chapter_data = {'chapter_data':chapter_data,'encrypted_hashed_chapter': encrypted_hashed_chapter.hex(),'public_key':public_key.save_pkcs1().hex()}
with open("secure_chapter_data.json", "w") as outfile:
    outfile.write(json.dumps(secure_chapter_data))

# Save the keys to another json file
public_key = public_key.save_pkcs1().hex()
private_key = private_key.save_pkcs1().hex()
keys = {'public_key': public_key, 'private_key': private_key}
keys = json.dumps(keys)
with open("keys.json", "w") as outfile:
    outfile.write(keys)
    
# generate a single .txt file to read the chapter
write_chapter_to_file(chapter_data)