# -----------------------------------------------------------
# Check that a given block is right
#
# 09/07/2023 Steven Mathey
# email steven.mathey@gmail.ch
# -----------------------------------------------------------


Import block
Local checks:
    - Compute hash of everything and check that it matches block hash
    - Compute hash of author data and compare to decrypted hash
    - check the number of characters in the author data different fields
previous block check
    - check that the block number is one more than the previous block
    - check that mining date is more than 1 week after previous block mining date
    - check that the previous block hash is right
Comparison to ETH
    - check that the eth hash is the right one.
    
Make readable pdf from:
    - chapter data
    - secure chapter data
    - validated block (isolated)
    - full story
In all cases, check as much as possible