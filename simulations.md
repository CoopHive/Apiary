# simulations

A list of the simulations we need to run


## registrations of service providers

 * register resource provider
 * register job creator
 * register solver
 * register directory 
 * register mediator


## boot

 * boot as RP - load solver address from smart contract
 * boot at JC - load solver address from smart contract


## registrations of job and resource offers

 * RP registers resource offer to smart contract
 * JC registers job offer to smart contract


## matching

* solver matches job offer and resource offer
* solver creates deal CID from match
* solver indicates the match to the two parties
* (future) parties agree and sign transactions

## sanity

Just checks the simulator is up and functional:

 * check for overlapping addresses
 * check that amount of currency in circulation is constant (accounting for new amounts being added)
 * JC and RP agree to the same deal CID
 
