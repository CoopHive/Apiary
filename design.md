# lilypad design doc

## context

The rules of players in the simulated world are:

 * you must correctly report your wallet address (we're not actually doing cryptography in the simulator)
 * we're ignoring gas
 * we MUST include a TX object with the correct address and value (which can be 0) in every tx call

## solver stages

 * stage 1 = centralized solver
   * single process solver service
   * job creator and resource provider api's are merged
 * state 2 = centralized solver with split api's
   * single process solver service
   * job creator and resource provider api's are split
 * stage 3 = centralized solver with edge api's
   * solver is now dumb transport
   * resource provider and job creator apis are now edge services
   * the solver only connects messages
 * stag 4 = libp2p
   * there is now no solver
   * libp2p replaces the solver transport

### stages (from Levi)

* Step 1) solver matches, but with marketplace of solvers
* Step 2) solver runs autonomous agents on behalf of nodes
* Step 3) autonomous agents are run locally and solver is used for transporting messages
* Step 4) solver is totally removed, nodes communicate via libp2p


## services

Services:

 * smart contract
 * resource provider
 * job creator
 * solver
 * mediator
 * directory

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
   * timeoutDeposit `uint`
     * the amount of deposit that will be lost if the job takes longer than timeout
     * this must equal msg._value
   
 * `submitResults`
  

 * `cancelDeal`

## solver

The solver will eventually be removed in favour of point to point communication.

For that reason - the solver has 2 distinct sides to it's api, the resource provider side and job creator side.

The resource provider and job creator will have their **own** api's - seperate to these that their respective CLI's will use.

The following api's are what the resource provider and job creator will use to communicate with the solver.

#### resource provider

 * `broadcastResourceOffer(resourceOfferID)`
   * resourceOfferID `CID`
   * tell everyone connected to this solver about the resource offer
   * this will emit an event and keep the state internally

 * `communicateResourceOffer(resourceOfferID, jobCreatorID)`
   * resourceOfferID `CID`
   * jobCreatorID `address`
   * tell one specific job creator about the resource offer
   * this will emit an event and keep the state internally

 * `cancelResourceOffer(resourceOfferID)`
   * resourceOfferID `CID`
   * cancel the resource offer for everyone

  

#### job creator

 * `broadcastJobOffer(jobOfferID)`
   * resourceOfferID `CID`

 * `communicateJobOffer(resourceOfferID, resourceProviderID)`
   * resourceOfferID `CID`
   * jobCreatorID `address`

#### both

 * `listResourceOffers() returns []ID`
   * returns an array of resourceOfferID's that the msg._sender can see
   * this means resource offers that have been broadcast to everyone AND ones that have been sent to the msg._sender directly

 * `listJobOffers() returns []ID`
   * returns an array of jobOfferID's that the msg._sender can see
   * this means job offers that have been broadcast to everyone AND ones that have been sent to the msg._sender directly

  * `subscribe`


### resource provider

 * register -> smart contract
 * create resource offer -> solver
 * update resource offer -> solver
 * cancel resource offer -> solver
 * hear about match <- solver
 * agree match -> smart contract

### job creator

 * register (*)
 * create job offer
 * update job offer
 * cancel job offer
 * hear about match
 * agree match (*)
 



