# Blockchain Story

This is a blockchain implementation to tell a story. The story is written collaboratively, one chapter at a time and each chapter is validated and appended at the end of the blockchain with a proof of work protocol. Anyone can write the next chapter of the story and share it with the community. If the chapter is popular, then many miners will try to validate it and it will have a high chance of being finalised. This is a particualily inefficient way to tell a story (even collaboratively), but it it provides a story that can be written in a decentralised way and with a canon that is cryptographically immutable. It's only possible to change the story by writing the next chapters and taking it somewhere interesting. The past can not be changed.

The repository provides all the tools necessary to write the story: One script to digitally sign the chapter to be validated (chapter_signature.py), one script to validate the chapter and add it to the story (mining.py) and one sript to make sure that any given story has not been tampered with and follows the rules set up at the beginning (check_block.py).

miner insentive

## Blockchain rules

The details of the rules to add a chapter to the story are inserted in the first block, the genesis block. This block contains the information necessary for 'narrative' as well as 'block-chain' rules.

The 'narrative' rules are:
    - The title of the story is fixed at the beginning and must be repeated correctly in each block.
    - The amount of characters in the chapter title, author name and chapter text is limited.
    - The total amount of chapters in the story is limited.
These narrative rules can be different for every new story. Except for the story title, they are actually even optional. To skip any of them, the user can just ommit the corresponding field in the genesis block. These rules are imposed by first validating the genesis block and then checking each new block against it.

The 'block-chain' rules are:
    - Every block keeps track of its mining date.
    - There is an imposed delay between the mining of two consecutive blocks.
    - Each block contains a difficulty parameter that is determined by the block's mining time and is applied to the next block.
    - The difficulty is adjusted unless the intended mining time is reached. 
These rules are imposed with the use of different systems:
    - Although it is possible for the miner to lie about the mining date, this is restricted and descentivised:
        - The mining date of any given block must be at least later than the mining date of the previous block plus the set delay.
        - It is possible for a miner to write a date in the blockchain that is earlier than the actual mining date. This will enablem them to reduce the intended delay between blocks and start mining the next block faster than expected. This will however also increase the difficulty of the next block and thus make the actual mining longer.
        - The miners can freely report a mining date that is later than the actual mining date. They however run the risk that another miner validates a block with an earlier mining date. Then this block which will then have finality over their block and they will loose the invested mining work.
        - The miner is preventef from pre-mining a block (with a reported mining date in the future) before the set delay by the requirement that the hash value of a specific block from the Ethereum blockchain be present in each block (except for the genesis block). The block is defined to be the earliest block following the earliest authorised mining date.
    - The mining time is actually not recorded but is assumed to be the time interval between the current mining date and the sum of the mining date of the previous block, the mining delay and the intended mining time. If this interval is shorter than three quarters of the intended mining time, then the difficulty parameter is decreased by one. If it is longer than five quarters of the intended mining time, then the difficulty is decreased by one. In the other cases, the difficulty parameter is not changed.

			"mining_delay_days": 0.003472222222222222,
			"intended_mining_time_days": 0.001388888888888889,
			"mining_date": "2023/07/21 20:27:00",

Why delay?
explain difficulty adjustement and possible lying miner
finality


## Description of json files