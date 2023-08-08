# simulations

A list of the simulations we need to run

 * RP = resource provider
 * JC = job creator
 * RO = resource offer
 * JO = job offer

## boot

Register solver and then load solver address into RP & JC

 * register solver
 * boot as RP - load solver address from smart contract
 * boot at JC - load solver address from smart contract

## sanity

Just checks the simulator is up and functional:

 * same steps as `boot` simulation
 * post RO
 * post JO
 * solver matches
 * RP/JC hear match
 * RP/JC agree match