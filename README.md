# blockchain_story

This is a blockchain implementation to tell a story. The story is written collaboratively, one chapter at a time and each chapter is validated and appended at the end of the blockchain with a proof of work protocol. Anyone can write the next chapter of the story and share it with the community. If the chapter is popular, then many miners will try to validate it and it will have a high chance of being finalised. This is a particualily inefficient way to tell a story (even collaboratively), but it it provides a story that can be written in a decentralised way and with a canon that is cryptographically immutable. It's only possible to change the story by writing the next chapters and taking it somewhere interesting. The past can not be changed.

The repository provides all the tools necessary to write the story: One script to digitally sign the chapter to be validated (chapter_signature.py), one script to validate the chapter and add it to the story (mining.py) and one sript to make sure that any given story has not been tampered with and follows the rules set up at the beginning (check_block.py).

# Description of json files