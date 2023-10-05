# Blockchain Story

This is an implementation of a blockchain to tell a story. The story is written collaboratively, one chapter at a time and each chapter is validated and appended at the end of the blockchain with a proof of work protocol. The participants can take two roles: writer and/or miner. The writers each write their version of the next chapter of the story and share it with the community. Then the miners can pick one of the chapters and try to add it to the blockchain. If the chapter is popular, then many miners will try to validate it and it will have a high chance of being finalised. This is not an efficient way to tell a story (even collaboratively), but it provides a story that can be written in a decentralised way and with a canon that is cryptographically immutable. It's only possible to change the story by writing the next chapters and taking it somewhere interesting. The past cannot be changed. Moreover, it provides an interesting and original way to learn about blockchain technologies.

This is a slow blockchain. Indeed, writers need some time to write their submissions and miners need time to read all the submissions. For this reason, there is no need to automatise the peer-to-peer communication. This blockchain is intended to be shared manually between its participants. To this end, I created discord server: [https://discord.gg/wD8zs75tck](https://discord.gg/wD8zs75tck), where chapter submissions as well as validated stories can be uploaded.

In principle, such a blockchain only has to be defined before it can start growing. Anyone can read the rules and definitions and code up their own implementation. The current implementation serves multiple goals:

- It is a proof of concept. If it's possible to code, then the rules make sense and can be implemented.
- It makes it easier for participants to participate. There is no need to code. Just use this implementation.
- It teaches all the basics of blockchain technology.
- It provides a formal and precise definition of the blockchain ant its rules.

The repository provides all the tools necessary to participate in the story-writing: One script to digitally sign the chapter to be validated (chapter\_signature.py), one script to validate the chapter and add it to the blockchain (mining.py) and one script to make sure that any given blockchain has not been tampered with and follows the rules set up at the beginning (checks.py). The third script also creates an easily readable \*.txt file with only the story content. Moreover, a graphical user interface (gui.py) is also available. It provides access to the three other scripts through clickable buttons and forms. Finally, there is a script to scrape the discord server and download all the relevant \*.json files (get_files_from_discord.py). The story does not have to be written in English. The encoding is utf8. This implementation was however not tested with special characters.

## Blockchain rules

This blockchain is not about currencies or any type of transactions. Instead it's all about who gets to control the story. The writers are expected to want their contributions to be validated (and will probably be miners themselves). The miners want their favourite submission to be validated. The rules of the blockchain are designed to encourage a fair and fun writing process with this motivation in mind. In particular, a delay is imposed between the validation of any block and the beginning of the mining of the next one. This delay can change from story to story, but is intended to be about 1 week so that the writers have time to prepare the next submissions after each block is validated.

The details of the rules to add a chapter to the story are inserted in the first block, the genesis block. This block contains the information necessary for 'narrative' as well as 'blockchain' rules.

- The 'narrative' rules are:
    - The title of the story is fixed at the beginning and must be repeated correctly in each block.
    - The amount of characters in the chapter title, author name and chapter text can be limited.
    - The total amount of chapters in the story can be limited.

These narrative rules can be different for every new story. Except for the story title, they are optional. To skip any of them, the user can just omit the corresponding field in the genesis block. These rules are imposed by first validating the genesis block and then checking each new block against it.

- The 'blockchain' rules are:
    - Every block keeps track of its mining date.
    - There is an imposed delay between the mining of two consecutive blocks.
    - Each block contains a difficulty parameter (diff, integer between 0 and 256) that is determined by the block's mining time and is applied to the next block. The difficulty is defined by requiring that the block hashes be smaller than (the hexadecimal representation of) 2<sup>256-diff</sup>-1. This means that, on average, about 2<sup>diff</sup> guesses will be necessary to validate a block.
    - The difficulty is adjusted (in steps of plus or minus 1) unless the intended mining time is matched.
    - Blocks with identical authors must be signed with the same public key.
   
These rules are imposed with the use of different systems:

- Although it is possible for the miner to lie about the mining date, this is restricted and disincentivise:
    - The mining date of any given block must be at least later than the mining date of the previous block plus the set delay.
    - It is possible for a miner to write a date in the blockchain that is earlier than the actual mining date. This will enable them to reduce the delay between blocks and start mining the next block faster than expected. This will however also increase the difficulty of the next block and thus make the actual mining longer.
    - The miners can freely report a mining date that is later than the actual mining date. They however run the risk that another miner validates a block with an earlier mining date. Then this block will then have finality over their block and they will loose the invested mining work.
    - The miners are prevented from pre-mining a block (with a reported mining date in the future) before the set delay by the requirement that the hash value of a specific block from the [Ethereum blockchain](https://ethereum.org/en/) be present in each block (except for the genesis block). The block is defined to be the earliest block following the earliest authorised mining date.
- The mining time is actually not recorded but is assumed to be the time interval between the current mining date and the sum of the mining date of the previous block and the mining delay. If this interval is shorter than three quarters of the intended mining time, then the difficulty parameter is decreased by one. If it is longer than five quarters of the intended mining time, then the difficulty is decreased by one. In the other cases, the difficulty parameter is not changed. With this 'definition' of the mining time, stories with chapters that are not mined immediately become easier to mine and thus attractive to new miners.

In the case of a story with multiple forks, the reported mining dates are used to decide which one is final. The Bitcoin rule (the story with the largest amount of blocks wins) cannot be used here because some stories may have a predefined (and finite) number of chapters. The earliest mining date at the moment of the fork is not enough as well. Someone could rapidly mine one block and keep it secret while they mine the rest of the story. If there are multiple stories sharing the same genesis block, then the longest one has finality. If there are multiple stories with the same number of blocks, then the story age is computed as the sum (over all chapters) of the difference between the mining date and the mining date of the genesis block. The youngest story (with the smallest story age) is final.

## Description of *.json files

This implementation of a blockchain story is managed with *.json files. The main story is stored in files with name as \[StoryTitle\]\_\[largest\_block\_number\]\_\[mining\_date\_of\_latest\_block\].json. For example the first three blocks of 'test story' are stored in TestStory\_002\_2023\_08\_04\_09\_42\_57.json, which looks like:

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
			"mining_delay_days": 1,
			"intended_mining_time_days": 0.1,
			"mining_date": "2023/08/02 07:15:00",
			"story_age_seconds": 0,
			"difficulty": 25,
			"miner_name": "steven"
		},
		"hash": "7135b9046882b0d3a2dfdcb684c6be7aca7f83a1a0875c70dcad3d54a8fb244c"
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
			"hash_previous_block": "7135b9046882b0d3a2dfdcb684c6be7aca7f83a1a0875c70dcad3d54a8fb244c",
			"hash_eth": "0xa7783df451db614134404ada5a59ecf1878009cfc177185371b3b6a7bb41ced3",
			"miner_name": "sethyvenatem",
			"mining_date": "2023/08/03 07:54:22",
			"story_age_seconds": 88762,
			"difficulty": 26,
			"nb_tries": 9947889,
			"nonce": "a3042c0b36c50aac0ce60c8a03544680777eb7e07ed9f3f18e87d5fe2c17fe10"
		},
		"hash": "00000027679c692b638a776453aee15ea24a2c478dce5c30a920214d8b051edd"
	},
	"2": {
		"block_content": {
			"signed_chapter_data": {
				"chapter_data": {
					"story_title": "test story",
					"chapter_number": 2,
					"author": "sethyvenatem",
					"chapter_title": "second chapter",
					"text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque aliquet, sapien sit amet cursus commodo, lorem nibh auctor augue, eget placerat metus nunc eu lorem. Aliquam lacinia porttitor arcu, sit amet tincidunt dui sodales ut. Cras id porttitor lorem, et fermentum nisi. Nam lacinia, leo non sollicitudin luctus, tellus est porta tortor, et eleifend lacus nulla in mi. Interdum et malesuada fames ac ante ipsum primis in faucibus. Quisque ultricies consectetur urna, vel pharetra arcu commodo sed. Pellentesque et pellentesque augue, id hendrerit magna. Suspendisse nibh risus, maximus eget dolor ac, elementum egestas est.\n\nFusce consectetur purus at porta imperdiet. Maecenas semper ligula a risus tristique, eu sodales nunc auctor. Aenean quis ipsum purus. Maecenas rhoncus consectetur mi ut cursus. Maecenas luctus lectus quis libero fermentum convallis. Aliquam varius, quam ac condimentum eleifend, quam risus accumsan tellus, vel luctus ante nisi ut nisl. Morbi consequat diam sem, et dictum magna iaculis egestas. Aliquam et aliquet velit. Integer sed tempor dui, quis porttitor turpis. Sed pretium diam odio, in sagittis sem tempus a. Integer porta convallis tempor. Cras eget dolor non libero egestas pretium. Quisque sagittis in odio at posuere.\n\nProin a urna semper, venenatis tortor vitae, ornare lorem. Pellentesque eget nulla arcu. Quisque et dui in risus sodales porta. Quisque ac nulla sed tortor tincidunt interdum nec eget augue. Aenean tincidunt elit sit amet sapien lacinia, vitae cursus lorem vulputate. Donec efficitur, turpis posuere dignissim ullamcorper, tellus diam feugiat purus, nec molestie justo ex nec metus. Nulla tincidunt, sem vel bibendum vulputate, magna sem porta nisl, et dapibus tellus dolor ut lacus."
				},
				"encrypted_hashed_chapter": "55c5a7f8a8fb9eafadf9babfc5dced7d3eb9dfcaee39e437e68fd2232d9c65ae558ef552b91c3a51982d41dd6f7c1565aaaec2bba3a4666c4b7a8e75e167624f1cdf668ad78c5725939d67a05602450d614f5707641ceccfe494c33367e43acf040ac00a9a6d04698b2a52e7071d5e803834729ab1486cf73bd5eeb815e7178f",
				"public_key": "2d2d2d2d2d424547494e20525341205055424c4943204b45592d2d2d2d2d0a4d49474a416f4742414e4b3069786a714e507a416b74477962586a312f687674504d376b574e774e6e6e39696c4f764871376e4b415464646449432b6f576a530a362f6a68465a366371394f3863546f443534417074627447677a536f6354486d4c546949717553534f636e2b6c666d5261667733346f71476a304a56776937590a38576f415050667462316337594375793275597a55704b4a6a6869555855335968525668723039584643616e355a636e4b34357441674d424141453d0a2d2d2d2d2d454e4420525341205055424c4943204b45592d2d2d2d2d0a"
			},
			"hash_previous_block": "00000027679c692b638a776453aee15ea24a2c478dce5c30a920214d8b051edd",
			"hash_eth": "0xb5d7f472d532b96bbabf996d95417cc51ccecce04f4a6cf242de7af428da0931",
			"miner_name": "sethy",
			"mining_date": "2023/08/04 09:42:57",
			"story_age_seconds": 270439,
			"difficulty": 26,
			"nb_tries": 25886391,
			"nonce": "2b7bac769ebba7ee6fc3e5e95cd7420644171fd687423c22451932972f096941"
		},
		"hash": "00000022bbd18e3c2950daeb6ce19a0e5b74326dfc1b70fad54d2c486bff0bcd"
	}
}
```

The different blocks are indexed by their 'block\_number' field (which is an integer represented as a string). Each block has two fields: 'block\_content' and 'hash'. The second is the hash of the first. All the hashes are hexadecimal representations of the SHA-256 hash of the string containing the block content alphabetically sorted by key. All the blocks have 4 fields in common in their 'block\_content' field:

- 'miner\_name' This is the name of the miner and can be any string specified by the miner. It can't have any spaces.
- 'mining\_date' This is the mining date (string with format %Y/%m/%d %H:%M:%S). The date is reported in the UTC time zone and with the seconds rounded to the closest integer. Within the restrictions discussed above, it can be set freely. It should however be the date at which the block was mined. For the genesis block, it can be set entirely freely.
- 'difficulty' This is the mining difficulty of the next block. It is an integer between 0 and 256. For the genesis block, it can be set freely or be calculated based on the 'intended\_mining\_time' field and the speed of my computer.
- 'story\_age\_seconds' This is the age of the story up until the corresponding block. It is an integer. It is the sum of the ages of all previous block (including the current block). The age of each block is the difference between the block mining date and the mining date of the genesis block rounded to the closest second. This field is used to determine finality in the case that multiple branches have the same number of blocks.

The genesis block (block '0') has the following special fields that are not present in the other blocks:

- 'story\_title' The title of the story is set here. This is a string.
- 'chapter\_number' This is the block number and should be 0.
- 'author' This is the author of the genesis block. The person who initiates the story and chooses the rules. Any string can be used here.
- 'character\_limits' This contains (at most) 3 sub-fields restricting the length of the different elements of the story's chapters. It can restrict the length of the chapter titles, author names and texts. Any of these fields can also be omitted to leave more freedom to the authors. The restrictions are specified as integer numbers.
- 'number\_of\_chapters' This is an integer denoting the maximum number of chapters that the story can contain.
- 'mining\_delay\_days' This is a float denoting the amount of days after which new blocks can be mined.
- 'intended\_mining\_time\_days' This is a float denoting the expected mining time (in days). It is used to dynamically set the difficulty of the mining.

These fields can be set freely before the first chapter is written but cannot be modified afterwards. They shape the story to come. The other blocks (the actual chapters) have the following additional fields:

- 'signed\_chapter\_data' See below.
- 'hash\_previous\_block' This is the hash value of the previous block. It ensures that each block is bonded to the previous one.
- 'hash\_eth' This is the hash of the first block of the ETH blockchain that comes after the first authorised mining date. This date is the sum of the mining date of the previous block and the mining delay set in the genesis block.
- 'nb\_tries' This records the number of nonce values that were tried before an appropriate one was found. This field is there just because it's interesting, but is not used to secure the blockchain. It can be set to any integer, but it's nice if the miners report it honestly.
- 'nonce' This can be any hash value. Different values of the nonce produce different block hashes and only hash values smaller than the value set by the mining difficulty allow for a block to be validated.

The chapter submissions are read from signed-chapter-data files. The file name pattern is signed\_\[StoryTitle\]\_\[chapter number\]\_\[ChapterAuthor\].json. For example, the first chapter of the above story is stored in signed\_TestStory\_001\_StevenMathey.json and looks like:

```json
{
   "chapter_data":{
      "author":"Steven Mathey",
      "chapter_number":1,
      "chapter_title":"First chapter",
      "story_title":"test story",
      "text":"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque aliquet, sapien sit amet cursus commodo, lorem nibh auctor augue, eget placerat metus nunc eu lorem. Aliquam lacinia porttitor arcu, sit amet tincidunt dui sodales ut. Cras id porttitor lorem, et fermentum nisi. Nam lacinia, leo non sollicitudin luctus, tellus est porta tortor, et eleifend lacus nulla in mi. Interdum et malesuada fames ac ante ipsum primis in faucibus. Quisque ultricies consectetur urna, vel pharetra arcu commodo sed. Pellentesque et pellentesque augue, id hendrerit magna. Suspendisse nibh risus, maximus eget dolor ac, elementum egestas est.\n\nFusce consectetur purus at porta imperdiet. Maecenas semper ligula a risus tristique, eu sodales nunc auctor. Aenean quis ipsum purus. Maecenas rhoncus consectetur mi ut cursus. Maecenas luctus lectus quis libero fermentum convallis. Aliquam varius, quam ac condimentum eleifend, quam risus accumsan tellus, vel luctus ante nisi ut nisl. Morbi consequat diam sem, et dictum magna iaculis egestas. Aliquam et aliquet velit. Integer sed tempor dui, quis porttitor turpis. Sed pretium diam odio, in sagittis sem tempus a. Integer porta convallis tempor. Cras eget dolor non libero egestas pretium. Quisque sagittis in odio at posuere.\n\nProin a urna semper, venenatis tortor vitae, ornare lorem. Pellentesque eget nulla arcu. Quisque et dui in risus sodales porta. Quisque ac nulla sed tortor tincidunt interdum nec eget augue. Aenean tincidunt elit sit amet sapien lacinia, vitae cursus lorem vulputate. Donec efficitur, turpis posuere dignissim ullamcorper, tellus diam feugiat purus, nec molestie justo ex nec metus. Nulla tincidunt, sem vel bibendum vulputate, magna sem porta nisl, et dapibus tellus dolor ut lacus.\n"
   },
   "encrypted_hashed_chapter":"4e16ce853c68d029bcae183162cf8e6a0ee77460b084fe4d543921a215222efa6a4bc7dcacd46b2c1322f5bad2dbc7a088f6d723b668aa9f6ba4057ed8f91630258c5de9674f19b403b925c4690c708f25047b4791e6096fdcb8f5037336a0043888b1e313fd7637842fdb56848daf19f37b1844176e4594033996e982586125",
   "public_key":"2d2d2d2d2d424547494e20525341205055424c4943204b45592d2d2d2d2d0a4d49474a416f474241496b704e436d64575273474e72754174342f57396273304f4f72624c4b30496c6f706a766e3557335437586f674238316a564c786e73480a6e357556447373506d39354c4b5277674835535775754e514649722b2b354348326f482b5571644c473261516b2b5a33594a6b57534758317678584e50724c550a4d6d30734b42345358577a724372394a6d6e6e65786643516873324c4c4d626857656e62536278776a575550366d7636416f425841674d424141453d0a2d2d2d2d2d454e4420525341205055424c4943204b45592d2d2d2d2d0a"
}
```
These files contain 3 fields:

- 'chapter\_data' This is the actual content of the chapter to validate. It contains 5 sub-fields 'story\_title', 'chapter\_number', 'author', 'chapter\_title' and 'text'. The chapter\_number is an integer and all the other fields are strings. The story\_title must coincide with the story\_title reported in the genesis block. The chapter number must be one plus the largest validated block number. Line returns are included in the text by including the string '\n'. This is handled automatically if the chapter is signed by providing the text as a *.txt file in chapter\_signature.py.
- 'encrypted\_hashed\_chapter' and 'public\_key' provide the digital signature through the RSA protocol. The chapter data is encrypted with the author's private key and the public key is provided to enable the proof that the text has not been changed.

## How to use the python scripts

Additional details on how the python scripts work are in the scripts as comments. Here are instructions on how to use them:

### chapter\_signature.py

This script performs a digital signature on any given chapter. This is done with the [RSA cryptosystem](https://en.wikipedia.org/wiki/RSA_(cryptosystem)). The script searches the working folder for a key file with the corresponding author. If the file is not found, a new pair of private and public keys are generated. The private key is used to encrypt the (hash of) the chapter data and both the encrypted hash and the public key are provided together with the chapter data. The public key can be used to decrypt the data and check that it is the same as the clear data. This test proves that the chapter data has not been modified because only the holder of the corresponding private key can produce such an encryption.

The key file is a json file wit the following file name pattern is keys\_\[ChapterAuthor\].json. For example, my key file is called keys\_\StevenMathey.json and looks like:

```json
{
	"author": "Steven Mathey",
	"private_key": "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
	"public_key": "2d2d2d2d2d424547494e20525341205055424c4943204b45592d2d2d2d2d0a4d49474a416f474241496b704e436d64575273474e72754174342f57396273304f4f72624c4b30496c6f706a766e3557335437586f674238316a564c786e73480a6e357556447373506d39354c4b5277674835535775754e514649722b2b354348326f482b5571644c473261516b2b5a33594a6b57534758317678584e50724c550a4d6d30734b42345358577a724372394a6d6e6e65786643516873324c4c4d626857656e62536278776a575550366d7636416f425841674d424141453d0a2d2d2d2d2d454e4420525341205055424c4943204b45592d2d2d2d2d0a"
}
```

The chapter data can be provided in two ways:

- Place it in a json file, put the file in the same directory as the script and call the script with the name of the file as argument. The json file must have the following fields: 'story\_title', 'chapter\_number', 'author', 'chapter\_title' and 'text'. The 'chapter\_number' value must be an integer. The other field values are strings. New lines must be indicated by '\n'.
- Call the script with no argument. Then the script prompts the user for the necessary information. The user will be prompted to provide a file name for the text of the chapter. This text must be placed in a \*.txt file in the same directory as the script. Line returns are then handled by the \*.txt format and converted to '\n' by the script.

If possible, the script checks that the chapter data to sign is consistent with the genesis block. It looks through the working directory and uses the genesis block of the longest validated story if there is one. If not, it looks for a file called 'genesis\_block.json'. If neither are available, then the test is skipped.

The script creates 2 or 3 files in the working directory:

- the signed chapter data (\*.json file).
- a \*.json file with the private and public keys (only if absent)
- a \*.txt file with the chapter data displayed in an easily readable way.

### mining.py

This script validates and adds one block to the existing story. It is used a bit differently for the genesis block and the others. To validate an ordinary block, run the script with three arguments: the file name of the up-until-now validated story, the file name for the signed chapter data and the miner name. To validate the genesis block, run it with only two arguments: the name of the genesis block \*.json file, and the miner name. All the files must be placed in the working directory.

This script performs the mining operation and can run for a very long time. It is however not a problem a problem to interrupt it and start again because the mining is done randomly. 

The script creates one file with the newly validated story in the working directory. The script offers to send the \*.json file of the obtained validated story directly to the discord server through a webhook. Type in 'y' ('yes', 'Y', 'YES', ..., or 'yEs') then 'enter' when prompted.

### checks.py

This script checks that the submitted data follows all the rules of the blockchain. It is called with the filename (a \*.json file) of the data to check as its single argument. There are 4 possibilities which are identified from the keys of the submitted \*.json file:

- The user submits unsigned chapter data. The script tries to find a genesis block in the working directory by first looking for a validated story (story title pulled from the submitted data and filename pattern \[StoryTitle\]\_\[largest\_block\_number\]\_\[mining\_date\_of\_latest\_block\].json). If this does not work, it looks for a file called genesis_block.json. If a genesis block is available, then the script checks that the submitted chapter has the right 'story\_title', 'character\_limits' and 'number\_of\_chapters'. No checks are performed if there is no genesis block available.
- The user submits a signed chapter data. The scripts tries to find a genesis block as above and performs the same checks. Furthermore, it checks that the chapter data is signed correctly. Without a genesis block, only the digital signature is checked.
- The user submits a single complete block. All the above checks are performed as above (except if the submitted block is number '0', genesis block). Moreover, the hash value is recalculated and compared to the provided one.
- The user submits multiple linked blocks. The script checks that these are a list of consecutive blocks starting with block '0'. Then all the above checks are performed independently on each block (with the genesis block being block '0'). Furthermore, the script checks that all the blocks are linked correctly. In particular, it checks the chapter numbering, the story\_age\_seconds field, the hash value of the ETH block, the hash value of the previous block, the mining date, the correct application of the difficulty setting and the difficulty setting its self.

In all cases, the submitted file must be placed in the working directory. Furthermore, unless the user submits a genesis block and if all the tests are passed, the script produces a \*.txt file with the entire submitted the story in a readable form.

### gui.py

The graphical user interface can run any of the above three scripts. Start it and answer the questions! Once it is finished, it shows a summary of what happened.

- The chapter signature is done through a form. The chapter content can be pasted in directly.
- The chapter mining is done by selecting the new chapter and the story from two lists. The script searches the working directory for any signed chapter and validated story files and displays them in two separate tables. The user can then click the chapter file to validate and the story to add it to and click a button to run the mining process. There is also a tick-box to tell the script if the validated story should be automatically sent to the discord server (through the webhook) or not.
- The chapter checking creates a list (from the files in the working directory) of all the files that can be checked. The user can then click any file and check it. The script then produces two text boxes. The left one is a summary of the checks that were performed and the right one shows the story content of the selected file in an easier-to-read way.

### get\_files\_from\_discord.py

This script implements a discord bot that logs onto the server, downloads all the available \*.json files to the working directory and shuts down. This automatises a simple task. This script requires a discord bot token to work. The user should generate their own token (from the discord developer portal) and place it in a file called discord_token.txt in the working directory.

## Disclaimer

This is a beginner's project which has taught me everything that I know about blockchains. It surely contains mistakes and oversights. Any feedback would be greatly appreciated. In particular:

- I tested everything as well as possible by myself. The next phase of testing is to get other people to participate and share files between writers and miners. In any case, bugs never really go away. Can you find any?
- What attacks can you imagine taking place against this blockchain. Is it well enough protected?

There still is much more to do:

- get people to write a story.
- How much can the mining be sped up by keeping track of the nonce values that were already tried? Beyond which difficulty does this become impractical and/or irrelevant?
- switch out the \*.json files for ASN.1.
- set up a proper p2p network.
- what else?