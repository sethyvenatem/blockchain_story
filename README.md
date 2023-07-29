# Blockchain Story

This is an implementatio of a blockchain to tell a story. The story is written collaboratively, one chapter at a time and each chapter is validated and appended at the end of the blockchain with a proof of work protocol. The participants can take (up to) two roles: writer and/or miner. The writers each write their version of the next chapter of the story and share it with the community. Then the miners can pick one of the chapters and try to add it to the blockchain. If the chapter is popular, then many miners will try to validate it and it will have a high chance of being finalised. This is not an efficient way to tell a story (even collaboratively), but it it provides a story that can be written in a decentralised way and with a canon that is cryptographically immutable. It's only possible to change the story by writing the next chapters and taking it somewhere interesting. The past can not be changed. Moreover, it provides an interesting and original way to learn about blockchain technologies.

This is a slow blockchain. Indeed, writers need some time to write their submissions and miners need time to read all the submissions. For this reason, there is no need to automatise the peer-to-peer communication. This blockchain is intended to be shared manually (uploading the submissions and validated story) over a dedicated discord server, https://discord.gg/5X8MM3Jz.

In principle, such a blockchain only has to be defined before it can start growing. Anyone can read the rules and definitions and code up their own implementation. The current implementation serves muliptle goals:
- It is a proof of concept. If it's possible to code, then the rules make sense and can be implemented.
- It makes it easier for participants to participate. There is no need to code. Just use this implementation.
- It has teaches all the basics of blockchain technology.
- It provides a formal and precise definition of the blockchain ant its rules.

The repository provides all the tools necessary to participate in the story-writing: One script to digitally sign the chapter to be validated (chapter_signature.py), one script to validate the chapter and add it to the blockchain (mining.py) and one script to make sure that any given blockchain has not been tampered with and follows the rules set up at the beginning (check_block.py). The third script also creates an easily readable *.txt file with only the story content. The story does not have to be written in english. The encoding is utf8. This implementation was however not tested with special characters.

## Blockchain rules

This blockchain is not about currencies or any type of transactions. Instead it's all about who gets to control the story. The writers are expected to want their contributions to be validated (and will probably be miners themselves). The miners want their favorite submission to be validated. The rules of the blockchain are designed to encourage a fair and fun writing process with this motivation in mind. In particular, a delay is imposed between the validation of any block and the beginning of the mining of the next one. This delay can change from story to story, but is intended to be about 1 week so that the writers have time to prepare the next submissions after each block is validated.

The details of the rules to add a chapter to the story are inserted in the first block, the genesis block. This block contains the information necessary for 'narrative' as well as 'blockchain' rules.

- The 'narrative' rules are:
    - The title of the story is fixed at the beginning and must be repeated correctly in each block.
    - The amount of characters in the chapter title, author name and chapter text is limited.
    - The total amount of chapters in the story is limited.
These narrative rules can be different for every new story. Except for the story title, they are actually even optional. To skip any of them, the user can just ommit the corresponding field in the genesis block. These rules are imposed by first validating the genesis block and then checking each new block against it.

- The 'blockchain' rules are:
    - Every block keeps track of its mining date.
    - There is an imposed delay between the mining of two consecutive blocks.
    - Each block contains a difficulty parameter that is determined by the block's mining time and is applied to the next block. The difficulty is defined by requiring that the block hashes be smaller than (the hexadecimal representation of) 2**(256-difficulty)-1. This means that, on average, about 2**difficulty guesses will be necessary to validate a block.
    - The difficulty is adjusted unless the intended mining time is reached.
    
These rules are imposed with the use of different systems:
- Although it is possible for the miner to lie about the mining date, this is restricted and descentivised:
    - The mining date of any given block must be at least later than the mining date of the previous block plus the set delay.
    - It is possible for a miner to write a date in the blockchain that is earlier than the actual mining date. This will enablem them to reduce the intended delay between blocks and start mining the next block faster than expected. This will however also increase the difficulty of the next block and thus make the actual mining longer.
    - The miners can freely report a mining date that is later than the actual mining date. They however run the risk that another miner validates a block with an earlier mining date. Then this block which will then have finality over their block and they will loose the invested mining work.
    - The miner is preventef from pre-mining a block (with a reported mining date in the future) before the set delay by the requirement that the hash value of a specific block from the Ethereum blockchain be present in each block (except for the genesis block). The block is defined to be the earliest block following the earliest authorised mining date.
- The mining time is actually not recorded but is assumed to be the time interval between the current mining date and the sum of the mining date of the previous block, the mining delay and the intended mining time. If this interval is shorter than three quarters of the intended mining time, then the difficulty parameter is decreased by one. If it is longer than five quarters of the intended mining time, then the difficulty is decreased by one. In the other cases, the difficulty parameter is not changed.

In the case of multiple forked stories, the reported mining dates are used to decide which one is final. The bitcoin rule (the story with the largest amount of blocks wins) can not be used here because some stories may have a predefined (and finite) number of chapters. The earliest mining date at the moment of the fork is not enough as well. Someone could rapidly mine one block and keep it secret while they mine the rest of the story as they want. It there are multiple stories sharing the same genesis block, then the longest one has finality. If there are multiple stories with the same number of blocks, then the 'story age' is computed as the sum (over all chapters) of the difference between the mining date and the mining date of the genesis block. The youngest story (with the smallest 'story age') is final.

## Description of json files

This implementation of a blockchain story is managed with *.json files. The main story is stored in files with name as [StoryTitle]_[largest_block_number].json. For example the first two blocks of test story are stored in TestStory_001.json, which looks like:

```json
{
	"0": {
		"block_content": {
			"story_title": "test story",
			"chapter_number": 0,
			"author": "Steven Mathey",
			"character_limits": {
				"chapter_title": 150,
				"author": 1000,
				"text": 30000
			},
			"number_of_chapters": 10,
			"mining_delay_days": 7,
			"intended_mining_time_days": 0.01,
			"mining_date": "2023/07/20 12:00:00",
			"story_age_days": 0.0,
			"miner_name": "steven",
			"difficulty": 22
		},
		"hash": "d3c275e7c25651fe9f9203d1ae9c22265c21aec6cd9a682df7373ea6faf7b0b2"
	},
	"1": {
		"block_content": {
			"signed_chapter_data": {
				"chapter_data": {
					"story_title": "test story",
					"chapter_number": 1,
					"author": "Steven Mathey",
					"chapter_title": "First chapter",
					"text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque aliquet, sapien sit amet cursus commodo, lorem nibh auctor augue, eget placerat metus nunc eu lorem. Aliquam lacinia porttitor arcu, sit amet tincidunt dui sodales ut. Cras id porttitor lorem, et fermentum nisi. Nam lacinia, leo non sollicitudin luctus, tellus est porta tortor, et eleifend lacus nulla in mi. Interdum et malesuada fames ac ante ipsum primis in faucibus. Quisque ultricies consectetur urna, vel pharetra arcu commodo sed. Pellentesque et pellentesque augue, id hendrerit magna. Suspendisse nibh risus, maximus eget dolor ac, elementum egestas est.\n\nFusce consectetur purus at porta imperdiet. Maecenas semper ligula a risus tristique, eu sodales nunc auctor. Aenean quis ipsum purus. Maecenas rhoncus consectetur mi ut cursus. Maecenas luctus lectus quis libero fermentum convallis. Aliquam varius, quam ac condimentum eleifend, quam risus accumsan tellus, vel luctus ante nisi ut nisl. Morbi consequat diam sem, et dictum magna iaculis egestas. Aliquam et aliquet velit. Integer sed tempor dui, quis porttitor turpis. Sed pretium diam odio, in sagittis sem tempus a. Integer porta convallis tempor. Cras eget dolor non libero egestas pretium. Quisque sagittis in odio at posuere.\n\nProin a urna semper, venenatis tortor vitae, ornare lorem. Pellentesque eget nulla arcu. Quisque et dui in risus sodales porta. Quisque ac nulla sed tortor tincidunt interdum nec eget augue. Aenean tincidunt elit sit amet sapien lacinia, vitae cursus lorem vulputate. Donec efficitur, turpis posuere dignissim ullamcorper, tellus diam feugiat purus, nec molestie justo ex nec metus. Nulla tincidunt, sem vel bibendum vulputate, magna sem porta nisl, et dapibus tellus dolor ut lacus."
				},
				"encrypted_hashed_chapter": "2aca7d50ca560a16d55c3426e3f39046fae76c0d4a4134f88daaa212146156dc879ddf238d23748f385ad0db7ccf0d58212a6b7617a6712d1f8d7605c84d843d9f55c3f36543fa70a0b03eeed4b2c6e127c72ac7549ac4fb7db31fe2fdd96e7d5f2b9ec3aea50ed6acdf078c62b1fc88e4332b5a837feae7ecad4941593ba273",
				"public_key": "2d2d2d2d2d424547494e20525341205055424c4943204b45592d2d2d2d2d0a4d49474a416f4742414948712b704553584a4c7a6c2f51304946535a2f5a653854694a4d364b496156344d474b5378387459756c536b4457796a4f32785730480a707547502b48666e5a6455615478597471316d3074445039423236304c69715a59564b4d4e314e57347549477536426e586768434c32706f5170373173646c4d0a4c4a5434463853516c6e537a59733557364e6436547267316873316978704267376c4264355270714f2b385057344d785965736841674d424141453d0a2d2d2d2d2d454e4420525341205055424c4943204b45592d2d2d2d2d0a"
			},
			"hash_previous_block": "d3c275e7c25651fe9f9203d1ae9c22265c21aec6cd9a682df7373ea6faf7b0b2",
			"hash_eth": "0x099580cbcee5ac8ae130b75b73060e23953298533d0962340bb78be68d596ff3",
			"miner_name": "sethyvenatem",
			"mining_date": "2023/07/27 21:00:15",
			"story_age_days": 7.375175638460648,
			"difficulty": 21,
			"nb_tries": 1146437,
			"nonce": "240446d36aabac74238fc456d3f6a393d2626fae5324ee96c0aa876d64972d53"
		},
		"hash": "0000011c6c8e8d139a83a9f1dfbd57b38dfa389db2922b1d635e813c6286a2ac"
	}
}
```

The different blocks are indexed by their 'block_number' field (which is an integer represented as a string). Each block has two fields: 'block_content' and 'hash'. The second is the hash of the first. All the hashes are hexadecimal representations of the SHA-256 hash of the string containing the block content. All the blocks have 4 fields in common in their 'block_content' field:
- 'miner_name' This is the name of the miner and can be any string specified by the miner.
- 'mining_date' This is the mining date. It has the restrictions set above and should be the date at which the block was mined. For the genesis block, it can be set freely.
- 'difficulty' This is the mining difficulty of the next block. It is an integer between 0 and 256. For the genesis block, it can be set freely or be calculated based on the 'intended_mining_time' field and the speed of my computer.
- 'story_age_days' This is the 'age' of the story up until the corresponding block. It is the sum over all the previous block and including the current block of the difference between the block mining date and the mining date of the genesis block (in days). This field is used to determine finality in the case that multiple branches have the same number of blocks.

The genesis block (block number 0) has the following special fields that are not present in the other blocks:
- 'story_title' The title of the story is set here. This is a string.
- 'chapter_number' This is the block number and should be 0.
- 'author' This is the author of the genesis block. The person who initiates the story. Any string can be used here.
- 'character_limits' This contains (at most) 3 sub-fields restricting the length of the different elements of the story's chapters. It can restrict the length of the chapter titles, authors and texts. Any of these fields can also be ommitted to leave more freedom to the authors. The restrictions are specified as integer numbers.
- 'number_of_chapters' This is an integer denoting the maximum number of chapters that the story can contain. It can be used to write a finite story.
- 'mining_delay_days' This is a real number denoting the amount of days after which new blocks can be mined.
- 'intended_mining_time_days' This is a real number denoting the expected mining time (in days). It is used to dynamically set the difficulty of the mining.
These fields can be set freely before the first chapter is written but can not be modified afterwards. They then shape shape the story to come.

The other blocks (the actual chapters) have the following additional fields:
- signed_chapter_data' See below.
- 'hash_previous_block' This is the hash value of the previous block. It ensures that each block is bonded to the previous one.
- 'hash_eth' This is the hash of the first block of the ETH blockchain that comes after the first authorised mining date. This date is the sum of the mining date of the previous block and the mining delay set in the genesis block.
- 'nb_tries' This records the number of nonce values that were tried before an appropriate one was found. This field is there just because it's interesting, but is not used to secure the blockchain. It can be set to any integer, but it's nice if the miners report it honestly.
- 'nonce' This can be any hash value. Different values of the nonceproduce different block hashes and only hash values smaller than the value set by the mining difficulty allow for a block to be validated.

The chapter submissions are read from signed chapter data files. The file name pattern is signed_[StoryTitle]_[chapter number]_[ChapterAuthor].json. For example, the first chapter of the above story is stored in signed_TestStory_001_StevenMathey.json and looks like:

```json
{
	"chapter_data": {
		"story_title": "test story",
		"chapter_number": 1,
		"author": "Steven Mathey",
		"chapter_title": "First chapter",
		"text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque aliquet, sapien sit amet cursus commodo, lorem nibh auctor augue, eget placerat metus nunc eu lorem. Aliquam lacinia porttitor arcu, sit amet tincidunt dui sodales ut. Cras id porttitor lorem, et fermentum nisi. Nam lacinia, leo non sollicitudin luctus, tellus est porta tortor, et eleifend lacus nulla in mi. Interdum et malesuada fames ac ante ipsum primis in faucibus. Quisque ultricies consectetur urna, vel pharetra arcu commodo sed. Pellentesque et pellentesque augue, id hendrerit magna. Suspendisse nibh risus, maximus eget dolor ac, elementum egestas est.\n\nFusce consectetur purus at porta imperdiet. Maecenas semper ligula a risus tristique, eu sodales nunc auctor. Aenean quis ipsum purus. Maecenas rhoncus consectetur mi ut cursus. Maecenas luctus lectus quis libero fermentum convallis. Aliquam varius, quam ac condimentum eleifend, quam risus accumsan tellus, vel luctus ante nisi ut nisl. Morbi consequat diam sem, et dictum magna iaculis egestas. Aliquam et aliquet velit. Integer sed tempor dui, quis porttitor turpis. Sed pretium diam odio, in sagittis sem tempus a. Integer porta convallis tempor. Cras eget dolor non libero egestas pretium. Quisque sagittis in odio at posuere.\n\nProin a urna semper, venenatis tortor vitae, ornare lorem. Pellentesque eget nulla arcu. Quisque et dui in risus sodales porta. Quisque ac nulla sed tortor tincidunt interdum nec eget augue. Aenean tincidunt elit sit amet sapien lacinia, vitae cursus lorem vulputate. Donec efficitur, turpis posuere dignissim ullamcorper, tellus diam feugiat purus, nec molestie justo ex nec metus. Nulla tincidunt, sem vel bibendum vulputate, magna sem porta nisl, et dapibus tellus dolor ut lacus."
	},
	"encrypted_hashed_chapter": "2aca7d50ca560a16d55c3426e3f39046fae76c0d4a4134f88daaa212146156dc879ddf238d23748f385ad0db7ccf0d58212a6b7617a6712d1f8d7605c84d843d9f55c3f36543fa70a0b03eeed4b2c6e127c72ac7549ac4fb7db31fe2fdd96e7d5f2b9ec3aea50ed6acdf078c62b1fc88e4332b5a837feae7ecad4941593ba273",
	"public_key": "2d2d2d2d2d424547494e20525341205055424c4943204b45592d2d2d2d2d0a4d49474a416f4742414948712b704553584a4c7a6c2f51304946535a2f5a653854694a4d364b496156344d474b5378387459756c536b4457796a4f32785730480a707547502b48666e5a6455615478597471316d3074445039423236304c69715a59564b4d4e314e57347549477536426e586768434c32706f5170373173646c4d0a4c4a5434463853516c6e537a59733557364e6436547267316873316978704267376c4264355270714f2b385057344d785965736841674d424141453d0a2d2d2d2d2d454e4420525341205055424c4943204b45592d2d2d2d2d0a"
}
```
These files contain 3 fields:
- 'chapter_data' This is the actual content of the chapter to validate. It contains 5 sub-fields 'story_title', 'chapter_number', 'author', 'chapter_title' and 'text'. The chapter_number is an integer and all the other fields are strings. The story_title must coincide with the story_title reported in the genesis block. The chapter number must be one plus the largest validated block number. Line returns are included in the text by including the string '\n'. This is handled automatically if the chapter is signed by providing the text as a *.txt file in chapter_signature.py
- 'encrypted_hashed_chapter' and 'public_key' provide the digital signature through the rsa protocol. The chapter data is encrypted with the author's private key and the public key is provided to enable the proof that the text has not been changed.


Decide terminology chapter - block

use spell checker