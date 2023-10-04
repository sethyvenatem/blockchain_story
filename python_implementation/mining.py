# -----------------------------------------------------------
# Perform the mining and generate finished block
#
# This script validates and adds one block to the existing story. If it is run with two arguments it
#    - Imports the genesis block. The file name is the first argument and the file is placed in the working directory.
#    - Estimate the difficulty of the mining of the first block.
#    - Computes the hash of the genesis block.
#    - Save it ['story_title'].title().replace(' ','')+'_000.json' (in the working directory) as the story with the first validated block
# If it is run with three arguments then it:
#    - Imports the up-until-now-validated story. The file name is the first argument and the file is placed in the working directory.
#    - Imports the signed chapter to validate. The file name is the second argument and the file is placed in the working directory.
#    - It performs as many checks as possible in order to avoid un-necessary mining. It checks that
#        - The signed chapter data is conform to the rules in the genesis block and is signed correctly
#        - The chapter number of the block to validate is right.
#        - The mining date of the previous block is far enough away in the past for the mining of the current block to take place.
#    - Initialise the block to validate with the hash of the previous block, the hash of the correct block of the ETH blockchain and the provided signed chapter data
#    - Performs the mining:
#        - Use the difficulty specified in the previous block
#        - Pick a nonce at random
#        - include the nonce, the current date and time, the number of guesses, the difficulty of the next block
#        - compute the hash of the current value
#        - retry unless the obtained hash is smaller than the max_hash (determined by the difficulty)
#    - The difficulty of the current block is determined with the 'intended_mining_time_days' attribute of the genesis block. If the mining time is shorter than 1/4 of the intented mining time, then the difficulty is set to the difficulty of the previous block plus 1 (effectively doubling the mining time). If the mining time is longer than 1/4 of the intented mining time, the the dificulty is set to the difficulty of the previous block minus one. In the other cases, the difficulty is the difficulty of the previous block.
#    - Once a suitable nonce is found, then the corresponding hash is included in the dictionary and the new story json file is saved to the working directory.
#
# 04/10/2023 Steven Mathey
# email steven.mathey@gmail.ch
# -----------------------------------------------------------

import json
import rsa
import datetime as dt
import sys
import pytz
import numpy as np
import random
from discord_webhook import DiscordWebhook, DiscordEmbed
from blockchain_functions import *

def time_to_mine_days(difficulty):
    # This function estimates the time to solve the mining problem as a function of the difficulty (in days).
    seconds_to_try_once = 0.0001
    return seconds_to_try_once*(2**difficulty)/(24*3600)

def estimate_difficulty(days):
    # This function estimates the difficulty as a function of the desired solution time (given in days).
    seconds_to_try_once = 0.0002
    # Use floor to be nice.
    return int(np.floor(np.log(24*3600*days/seconds_to_try_once)/np.log(2)))

def set_new_block_difficulty_and_mining_date(new_block, genesis, difficulty, mining_date_previous_block, story_age_previous_block):
    # Set the difficulty and mining date of the new block. 'mining_date_previous_block' is given as a timedelta.
    
    mining_date = get_now()
    mining_delay = dt.timedelta(days = genesis['mining_delay_days'])
    intended_mining_time = dt.timedelta(days = genesis['intended_mining_time_days'])
    grace = 0.25*intended_mining_time
    
    new_block['mining_date'] = dt.datetime.strftime(mining_date, '%Y/%m/%d %H:%M:%S')
    new_block['story_age_seconds'] = story_age_previous_block + round((mining_date - pytz.utc.localize(dt.datetime.strptime(genesis['mining_date'], '%Y/%m/%d %H:%M:%S'))).total_seconds())
      
    if mining_date > mining_date_previous_block + mining_delay + intended_mining_time + grace:
        # Too hard, reduce the difficulty.
        new_block['difficulty'] = difficulty - 1
    elif mining_date < mining_date_previous_block + mining_delay + intended_mining_time - grace:
        # Too easy, increase the difficulty.
        new_block['difficulty'] = difficulty + 1
    else:
        # Just right.
        new_block['difficulty'] = difficulty
    return new_block

def mine_chapter(story_file, chapter_file, miner_name, send = None):
    
    if chapter_file == None:
        print('2 arguments provided, this validates the genesis block.')
        genesis = import_json(story_file)
        if genesis == 'error':
            return 'error'
        test = check('intended_mining_time_days' in genesis.keys(), 'The provided file is not a valid genesis block.')
        if test == 'error':
            return 'error'
        if 'difficulty' not in genesis.keys():
            genesis['difficulty'] = estimate_difficulty(genesis['intended_mining_time_days'])
        if 'miner_name' not in genesis.keys():
            genesis['miner_name'] = miner_name
        genesis_hash = rsa.compute_hash(json.dumps(genesis, sort_keys = True, ensure_ascii = False).encode('utf8'), 'SHA-256').hex()
        genesis = {'block_content': genesis.copy()}
        genesis['hash'] = genesis_hash
        file_name = genesis['block_content']['story_title'].title().replace(' ','')+'_000_'+genesis['block_content']['mining_date'].replace(' ','_').replace(':','_').replace('/','_')+'.json'
        with open(file_name, "w", encoding='utf8') as outfile:
            json.dump({'0': genesis}, outfile, sort_keys = True, ensure_ascii = False)
        return 'success'

    if len(miner_name) == 0:
        print('Empty miner name provided.')
        return 'error'
    
    # Import the data to validate
    story = import_json(story_file)
    if story == 'error':
        return 'error'
    signed_chapter_data = import_json(chapter_file)
    if signed_chapter_data == 'error':
        return 'error'

    # Check that the chapter data is valid.
    genesis = story['0']['block_content']
    test = check(validate_chapter_data(signed_chapter_data, story), 'The signed chapter data does not comply with the rules of this story.')
    if test == 'error':
        return 'error'

    # Check that the number of the provided chapter is one plus the largest block number and extract the previous block.
    test = check(signed_chapter_data['chapter_data']['chapter_number']-1 == max([int(n) for n in story.keys()]), 'The chapter number of the block to add is not the last chapter number of the story.')
    if test == 'error':
        return 'error'
    previous_block = story[str(signed_chapter_data['chapter_data']['chapter_number']-1)]

    # Get the mining date of the previous block and check that it is far enough in the past.
    mining_date_previous_block = pytz.utc.localize(dt.datetime.strptime(previous_block['block_content']['mining_date'], '%Y/%m/%d %H:%M:%S'))
    story_age_previous_block = previous_block['block_content']['story_age_seconds']
    mining_delay = dt.timedelta(days = genesis['mining_delay_days'])
    test = check(mining_date_previous_block + mining_delay <= get_now(), 'The previous block was mined on the ' + mining_date_previous_block.strftime("%Y/%m/%d, %H:%M:%S")+'. This is less than ' + str(genesis['mining_delay_days']) + ' days ago. This block can\'t be validated right now. Please wait ' + str(mining_date_previous_block + mining_delay - get_now()) + '.')
    if test == 'error':
        return 'error'

    # Initialise the new block
    new_block = {'signed_chapter_data': signed_chapter_data, 'hash_previous_block': previous_block['hash'], 'hash_eth': get_eth_block_info(mining_date_previous_block + mining_delay), 'miner_name': miner_name}
    if new_block['hash_eth'] == 'error':
        return 'error'

    # Now perform the actual mining!
    # It takes about (2)**difficulty tries to find a valid nonce. On my computer, it takes about 0.0001 seconds for each try. difficulty = 23 should take about 10 minutes.
    difficulty = previous_block['block_content']['difficulty']
    new_block = set_new_block_difficulty_and_mining_date(new_block, genesis, difficulty, mining_date_previous_block, story_age_previous_block)
    # Set the hash value below which the block hash has to be. Use powers of 2 so that the difficulty is doubled as difficulty increases by 1.
    max_hash = 2**(256-difficulty)-1
    print('Start mining (at '+ dt.datetime.strftime(get_now(), '%Y/%m/%d %H:%M:%S')+' UTC)! On my computer, I estimate it to take about '+str(round(time_to_mine_days(difficulty)*24,3))+' hours to complete.')
    nb_tries = 1
    start_time = pytz.utc.localize(dt.datetime.strptime(new_block['mining_date'], '%Y/%m/%d %H:%M:%S'))
    new_block['nb_tries'] = nb_tries
    new_block['nonce'] = ''.join(random.choice('0123456789abcdef') for _ in range(64))
    new_hash = rsa.compute_hash(json.dumps(new_block, sort_keys = True, ensure_ascii = False).encode('utf8'), 'SHA-256')
    while int.from_bytes(new_hash,'big') > max_hash:
        nb_tries += 1
        new_block = set_new_block_difficulty_and_mining_date(new_block, genesis, difficulty, mining_date_previous_block, story_age_previous_block)
        new_block['nb_tries'] = nb_tries
        new_block['nonce'] = ''.join(random.choice('0123456789abcdef') for _ in range(64))
        new_hash = rsa.compute_hash(json.dumps(new_block, sort_keys = True, ensure_ascii = False).encode('utf8'), 'SHA-256')

    try_time = get_now()-start_time
    print('The mining took',nb_tries,'tries and',try_time+'. This is',try_time/nb_tries,'per try.')
    new_block = {'block_content': new_block.copy()}
    new_block['hash'] = new_hash.hex()
    story[str(signed_chapter_data['chapter_data']['chapter_number'])] = new_block
    new_file_name = story['0']['block_content']['story_title'].title().replace(' ','')+'_'+str(signed_chapter_data['chapter_data']['chapter_number']).rjust(3, '0')+'_'+new_block['block_content']['mining_date'].replace(' ','_').replace(':','_').replace('/','_')+'.json'

    with open(new_file_name, "w", encoding='utf-8') as outfile:
        json.dump(story, outfile, sort_keys = True, ensure_ascii = False)
    print('The newly validated story was saved in the working directory in '+new_file_name+'.')

    if send == None:
        send = input('Hurray, you validated a new block! Do you want to send it automatically to the discord server (y/n)?')
    if send.lower() in ['y','yes']:
        # Thanks! https://www.reddit.com/r/Discord_Bots/comments/iirmzy/how_to_send_files_using_discord_webhooks_python/
        #Replace the webhook URL with your own
        webhook_url = 'https://discord.com/api/webhooks/1138436079448498176/ErxoQ7gHxjoowu5BNyxxhg9bUGkqK6CtkZzk9xjRoOs2MjyaLpoQkwq_njmhPyYltxIH'
        #Create a Discord webhook object
        webhook = DiscordWebhook(url=webhook_url)
        #Create a Discord embed object
        embed = DiscordEmbed()
        #Set the title and description of the embed
        embed.set_title('Miner '+miner_name+' validated a new chapter!')
        embed.set_description(new_file_name)
        #Add the embed to the webhook
        webhook.add_embed(embed)
        response = webhook.execute()

        webhook = DiscordWebhook(url=webhook_url)
        #Add the file or files to the embed
        with open(new_file_name, 'rb') as f: 
            file_data = f.read() 
        #new_file_name = 'SPOILER_'+new_file_name
        webhook.add_file(file_data, new_file_name)
        #Send the webhook
        response = webhook.execute()
    else:
        print('Your newly validated story was not sent to the discord server!')
        print('Quickly, upload it manually at https://discord.gg/wD8zs75tck')
        
################################# The program starts here ################################################

if __name__ == "__main__":
    if (len(sys.argv) == 3) or (len(sys.argv) == 2):
        genesis_file_name = sys.argv[1]
        genesis = import_json(genesis_file_name)
        if 'miner_name' not in genesis.keys():
            miner_name = sys.argv[2]
        else:
            miner_name = genesis['miner_name']
        status = mine_chapter(genesis_file_name, None, miner_name)
        print(status)
    else:
        story_file = sys.argv[1]
        signed_chapter_file = sys.argv[2]
        miner_name = sys.argv[3]
        status = mine_chapter(story_file, signed_chapter_file, miner_name)
        print(status)