# Intro

The story is written collaboratively, one chapter at a time. Each chapter must be validated before it is appended to the blockchain. The participants can take two roles: writer and miner. The writers each write their version of the next chapter of the story and share it with the community. Then the miners can pick one of the chapters and try to add it to the blockchain. This represents a significant amount of work for their computers. If the chapter is popular, then many miners will try to validate it and it will have a high chance of being quickly validated. This is important because the first validated chapter is then (modulo some technicalities) accepted as the true official chapter.

This is a slow blockchain. Indeed, writers need some time to write their submissions and miners need time to read all the submissions. This server was create for this purpose. The writers can upload their chapter submissions in #author-submissions. The miners can download them, validate them and upload the updated story to #validated-story.

Writing a story in this way has original and interesting features:

- The story is cryptographically immutable. It's only possible to change the story by writing the next chapters and taking it somewhere interesting. The past cannot be changed.
- Anyone can pick up the story and add to it. The only requirement is to be able (through good writing) to convince the miners to work on your chapter.
- There can be no discussion about what version of the story is canon or who is an acceptable author. All this is cryptographically fixed by a precise set of rules.
- It teaches about blockchain technology.
- It's fun and interesting to mix and match disconnected ideas.

# Implementation

I wrote a full implementation of the blockchain. The necessary scripts together with a detailed (and technical) description is available in the github repository: https://github.com/sethyvenatem/blockchain_story. In short, these scripts can be used to digitally sign author contributions, validate them and check that everything has been done correctly. They are available below. The three *.py files require python to be installed to run. They do the following:

- chapter_signature.py takes the chapter written by an author and adds a digital signature on top of it. This ensures that the miners can't modify the author's work before validating it. This script runs without argument. The author is prompted for the chapter meta-data (story title, author name, chapter number and chapter title) as well as the name of a *.txt file with the chapter text. This text file must be placed in the same directory as the chapter_signature.py script. The script produces a *.json file that must be uploaded to #author-submissions where the miners can get it. This script also produces a *.txt file where the chapter content is displayed in an easily readable form.
- mining.py performs the work to add a chapter to the blockchain. It must be called with the file names of the up-until-now validated story and the digitally signed chapter data as well as the name of the miner. The two files must be placed in the same directory as mining.py. Upon completion of the validation process, the miner is offered the possibility to send the newly validated story (placed in a *.json file) directly to the #validated-story channel of this server. They can also upload the file manually.
- checks.py checks that a given story file is valid. It must be run with the name of the file to check as argument. The selected file must be placed in the same directory as checks.py. This script can check chapter data, digitally signed chapter data, individual blocks and full (although possibly unfinished) stories. If all the checks are passed, then the scripts creates a *.txt file with the content of the story in an easily readable form.

The detailed rules of each individual story are set in the genesis block (chapter 0). The different field names make these rules quite self-explanatory. See genesis_block.json below and the github repository for the details.

# Recommandations

For the story writing to go on smoothly it is recommended that the miners only attempt to add a chapter to the earliest version of the validated story. Each block has a mining_date field that can be checked to be sure. If they use another version, then it is highly probable that another miner will validate their block before. Moreover, when there are multiple validated stories, then the validation date is used to decide which story is official. Attempting to append a block to an unofficial story will most likely lead to pointless work for the miner's computer.

Authors should proofread their submissions and run them through a spell-checker. Indeed, once a block is validated, it becomes impossible to change it. Typos will be there forever!

The mining procedure is like repeatedly throwing 10 dices until 10 sixes come out. There is no memory of what was tried and no progress. It's all about trying long enough until the right combination comes out. It is therefore completely ok to interrupt a computer engaged in mining and start again later. No progress will be lost and the chances of validating a block will not be reduced. The only thing that matters is the total amount of time that the computer is working.