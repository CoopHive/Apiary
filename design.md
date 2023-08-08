# lilypad design doc

## context

The rules of players in the simulated world are:

 * you must correctly report your wallet address (we're not actually doing cryptography in the simulator)
 * we're ignoring gas
 * we MUST include a TX object with the correct address and value (which can be 0) in every tx call

## solver stages

 * stage 1 = solver matches, but with marketplace of solvers
   * single process solver service
   * job creator and resource provider api's are merged
 * state 2 = solver runs autonomous agents on behalf of nodes
   * single process solver service
   * job creator and resource provider api's are split
 * stage 3 = autonomous agents are run locally and solver is used for transporting messages
   * solver is now dumb transport
   * resource provider and job creator apis are now edge services
   * the solver only connects messages
 * stage 4 = solver is totally removed, nodes communicate via libp2p
   * there is now no solver
   * libp2p replaces the solver transport

## services

Services:

 * smart contract
 * resource provider
 * job creator
 * solver
 * mediator
 * directory

## types

These types are global data structures:

#### Range

Represents a range of values

 * min `uint`
 * max `uint`

#### ResourceOffer

The ID of the resource offer is the IPFS cid of the JSON document with the following structure:
 
 * owner `address`
 * CPU `uint`
 * GPU `uint`
 * RAM `uint`
 * prices `map[string]uint`
   * this is price per instruction for each module
  
#### JobOffer

The ID of the job offer is the IPFS cid of the JSON document with the following structure:

 * owner `address`
 * CPU `Range`
 * GPU `Range`
 * RAM `Range`
 * module `string`
 * price `uint`
   * this is price per instruction

## smart contract

#### types

 * `type CID` - bytes32

 * `type ServiceType` - enum
    * resourceProvider
    * jobCreator
    * solver
    * mediator
    * directory

#### service provider discovery

 * `registerServiceProvider(serviceType, url, metadata)`
    * serviceType `ServiceType`
    * ID = msg._sender
    * url `string`
      * this is the advertised network URL, used by directory and solver
    * metadata `CID`

 * `unregisterServiceProvider(serviceType)`
    * serviceType `ServiceType`
    * ID = msg._sender

 * `listServiceProviders(serviceType) returns []address`
    * serviceType `ServiceType`
    * returns an array of IDs for the given service type
   
 * `getServiceProvider(serviceType, ID) returns (url, metadata)`
    * serviceType `ServiceType`
    * ID `address`
    * url `string`
    * metadata `CID`
    * return the URL and metadata CID for the given service provider

#### deals

 * `agreeDeal(party, dealID, jobOfferID, resourceOfferID, timeout, timeoutDeposit)`
   * party ServiceType
     * this should be resourceProvider that owns the resourceOfferID or jobCreator that owns the jobOfferID
   * dealID `CID`
   * jobOfferID `CID`
   * resourceOfferID `CID`
   * timeout `uint`
     * the upper bounds of time this job can take - TODO: is this in seconds or blocks?
   * timeoutDeposit `uint` (msg._value)
     * the amount of deposit that will be lost if the job takes longer than timeout
     * this must equal msg._value
   
 * `submitResults(dealID, resultsCID, instructionCount, resultsDeposit)`
    * dealID `CID`
    * resultsCID `CID`
    * instructionCount `uint`
    * resultsDeposit `uint` (msg._value)
    * submit the results of the job to the smart contract

## solver

The solver will eventually be removed in favour of point to point communication.

For that reason - the solver has 2 distinct sides to it's api, the resource provider side and job creator side.

The resource provider and job creator will have their **own** api's - seperate to these that their respective CLI's will use.

The following api's are what the resource provider and job creator will use to communicate with the solver.

#### resource provider

Each call to the solver on behalf of a resource provider will include the resource provider's address as part of a signed TX object.

This is to ensure authentication in services that are not the smart contract.

 * `broadcastResourceOffer(resourceOfferID, resourceOffer)`
   * resourceOfferID `CID`
   * resourceOffer `ResourceOffer`
   * tell everyone connected to this solver about the resource offer

 * `communicateResourceOffer(resourceOfferID, jobCreatorID, resourceOffer)`
   * resourceOfferID `CID`
   * jobCreatorID `address`
   * resourceOffer `ResourceOffer`
   * tell one specific job creator about the resource offer

 * `cancelResourceOffer(resourceOfferID)`
   * resourceOfferID `CID`
   * cancel the resource offer for everyone

#### job creator

 * `broadcastJobOffer(jobOfferID, jobOffer)`
   * resourceOfferID `CID`
   * jobOffer `JobOffer`
   * tell everyone connected to this solver about the job offers

 * `communicateJobOffer(resourceOfferID, resourceProviderID, jobOffer)`
   * resourceOfferID `CID`
   * jobCreatorID `address`
   * jobOffer `JobOffer`
   * tell one specific resource provider about the resource offer

 * `cancelJobOffer(jobOfferID)`
   * jobOfferID `CID`
   * cancel the job offer for everyone

#### both

 * `listResourceOffers() returns []ResourceOffer`
   * returns an array of resourceOffers that the msg._sender can see
   * this means resource offers that have been broadcast to everyone AND ones that have been sent to the msg._sender directly

 * `getResourceOffer(resourceOfferID) returns ResourceOffer`
   * returns an array of jobOffers that the msg._sender can see
   * throw error if msg._sender cannot see the resource offer
   * this means resource offers that have been broadcast to everyone AND ones that have been sent to the msg._sender directly

 * `listJobOffers() returns []JobOffer`
   * returns an array of jobOfferID's that the msg._sender can see
   * this means job offers that have been broadcast to everyone AND ones that have been sent to the msg._sender directly

 * `getJobOffer(resourceOfferID) returns ResourceOffer`
   * returns an array of jobOffers that the msg._sender can see
   * throw error if msg._sender cannot see the resource offer
   * this means resource offers that have been broadcast to everyone AND ones that have been sent to the msg._sender directly

 * `onResourceOfferCreated(handler)`
   * handler `function(resourceOfferID, ResourceOffer)`
   * called when new resource offers (either global or targeted) are seen

 * `onJobOfferCreated(handler)`
   * handler `function(jobOfferID, JobOffer)`
   * called when new job offers (either global or targeted) are seen

 


## resource provider

 * register -> smart contract
 * create resource offer -> solver
 * update resource offer -> solver
 * cancel resource offer -> solver
 * hear about match <- solver
 * agree match -> smart contract

## job creator

 * register (*)
 * create job offer
 * update job offer
 * cancel job offer
 * hear about match
 * agree match (*)
 



