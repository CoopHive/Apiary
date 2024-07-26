# Coophive Multi-Agent System Design

## Abstract

This is a document to conceptualize the high-level design choices of Coophive, with regards to its multi-agent systems, data-driven optimal control, agent-to-agent negotiation. It is currently an unstructured set of notes, based on the legacy design, existing documents such as legacy white paper, Figma Compute Market Achitecture. It serves as the reference point to define the building blocks of the agent marketplace. When possible, the discussion is kept general, while when necessary the specificities of the exchanged assets (storage, compute) will be introduced. 

The framework is nevertheless defined for "validatable, terminable tasks with collateral transfer after validation". In this context, we talk about "stateless" tasks to stress their inner reproducibility (their lack of dependence against client-specific state variables). The presence of agent-based modeling (whose policy is potentially data-driven, tapping into ML/RL), is motivated by the need to orchestrate a decentralized network of agents in a way that leads to competitive pricing/scheduling, from the user perspective. At the same time, the use of blockchain is motivate by the trustless and automatic transfer of collateral after validation.

## Introduction

The problem statement starts with the presence of a chain-generic/asset generic marketplace to interact optimally against. There are deep implications about going for a chain-generic or more specific marketplace, but this does not seem to have implications on the multi-agent system.

The value of the protocol is in recognizing, for example, the existance of idle computational power on the planet and of existing computational tasks that could be interested offering something in exchange for such a task to be performed. This creates an off-chain market of negotiation in which agents compete/cooperate to cut a good deal, i.e., they act optimally with respect to their fitness landscape, their action space and their state space (like in every market, negotiation helps the bid inform a "fair market value").

While the outcome of each negotiation goes on chain, negotiations are performed off-chain, and both on-chain and off-chain data can be used to inform various negotiation strategies.

A big part of the off-chain information are centralized in a pubsub que, a set of recorded messages, more or less public, that every agent can listen to (and store locally for memory). A question is for example how important it is for agents to observe the negotiation dynamics before an agreement vs learning from the final transaction only: this has consequences on the privacy of offers, as it may be valuable to enforce the publicity of intra-negotiation offers for a more transparent auction mechanism. We need to define better the pubsub cue, equivalent in many ways to a broker order book.

On this, see:
- https://pintu.co.id/en/academy/post/what-is-decentralized-order-book
- https://github.com/dyn4mik3/OrderBook
- https://pypi.org/project/sortedcontainers/

A set of environmental variables appear necessary for actors to construct optimal policies. These include:

- L1 and L2 tokens price. We believe the dynamics of the protocol, being based on smart contracts and EVM technology, to be driven by the state of the L1 (Ethereum) and L2 (???) protocols. One proxy for this is the point-in-time price of the two protocols.

- Gas Fees. Because of the need to record the outcome of a negotiation on the blockchain, the point-in-time gas fees is necessary to build policies. It's like having a time-dependent transaction cost model in trad-fi: the profitability of a position is a function of the current transaction costs. Here we are referring to the gas fees of the L2, but the gas fee of Ethereum may be relevant in modeling the dynamics of costs.

- Electricity costs. This is a space-time dependent variable defining the cost of electricity in the world. Agents, aware of their location, are interested in measuring the point-in-time field of the cost of electricity to understand the hedge they may have against other potential agents in different locations. This means that agents may have a module solely focused on the forecasting of the local (or even global) electricity price to enhance the state space and then use that as an input for the optimal controller. On this see, among others: https://arxiv.org/abs/2106.06033

It appears necessary to associate to each block (each deal), the wallet of the address, its hardware specifications, geolocation, timestamp. This means that in the transaction we need to have the IPFS CID, in which the computational cost of a task is specified (to be clarified with which quantitative metrics). A tricky point here is how to verify that the hardware specifications of a given wallet address in a given CID are true. Agents may be interested in hiding this information to other agents, and if they are able to do so, it is meaningless to build a protocol around the truthfulness of this information. About this, see the subject of verifiable provisioning of hardware: https://github.com/orgs/akash-network/discussions/614

One solution could be to enable an emergent secondary marketplace of jobs specifications, in which machines can associate (and this can be verified) their hardware specifications to a given Job. The market is emergent as if agents want to become autonomous and this dataset is valuable, they will create it. We may want to investigate this ourselves. An important point, on this, is that agents an agent looking at a given open job is in principle not able to say exactly its computational cost. It can learn from past data only if they are associated with specific schemas that enable the agent to interpolate the input space of the task for that schema (in the presence of enough datapoints to approximate the cost function).

Some examples of a Job Schema are:
- A docker image and its input(s);
- A github repository and an associated command;

Even in the open source (git) case, it makes sense to leverage the secondary marketplace, even if the estimation of the task cost is not done via interpolation of previous runs, but via analysis of the source code of the task (for which even analytical estimates of the cost may exist).

A task offer has to contain the CID of the data needed to perform the task. One could use this as a proxy for the computational cost of a task (even though a task could be associated with light data and be really expensive).

An on-chain recorded transaction can record the final amount payed in exchange for the computational power provided.

Every agent hardware specifications may limit the state space size. For example, some IoT actors would only be able to remember and act based on on-chain data, while others may be able to have a bigger memory and bigger state space. For the same reason, some agents may be unable to perform certain tasks (that may be costly and limited by time, in fact the validation could also check constraints in the tasks like the time it took to complete.). In other words, each agent has different constraints on both their state space and action space.

A task shall be associated with a variable specifying the possibility for it to be distributed. It could also specify the specific/maximum/minimum number of agents to take the task. The minimum case is to enforce federate learning in the case in which sensitive data needs to be broken down (problem, if agents can fake this IP, multiple virtual agents from the same malitious actor could fill up the task. Is this solvable? Similar issue as above). This creates a negotiation with some kind of waiting room in which people can subscribe to participate and can opt-out before the room is full.

A straightforward definition of fitness is profit.

About the integration of bundles of assets in the agent-to-agent negotiation picture, it regardless appears necessary to introduce a [Numéraire](https://en.wikipedia.org/wiki/Num%C3%A9raire) shared by all agents. If different agents have different priors on the value of a given asset, it becomes challanging to have a well posed interaction.

## Network Robustness

Reading “Timing Reliability for Local Schedulers in Multi-Agent Systems”: it seems pretty evident that in the setup of Multi-agent training following greedy policies, the system will end up being more fragile. I don’t think we can avoid an holistic training setup in which a degree of cooperation is instilled in each agent. This will have the consequence of each agent to behave suboptimally, and the system will become subscettible to greedy attacks. I believe the system will need to tollerate a certain degree of corruption/inefficiency in order to gain robustness.
Analogous situation in which greedy policies don’t work (see Section 5.1): https://web.stanford.edu/~boyd/papers/pdf/cvx_portfolio.pdf
Even more relevant, the concept of self-organized criticality: https://www.linkedin.com/posts/jean-philippe-bouchaud-bb08a15_how-critical-is-brain-criticality-activity-7000544505359654912-ETjz/

Not clear how to formalize/verify/deal with this point, but worth mentioning.

Reading "Local Scheduling in Multi-Agent Systems: getting ready for safety-critical scenarios”: is is clear that we need a deep conceptual and practical separation between the intelligent/strategic layer. This is a central node interacting with the agents competition pool, making sure agents are able to act and that the CPS as a whole is achieving what it needs to achieve.. This central node can learn general laws of behaviour based on the goals of the overall system and the behaviour of its components. In this sense, the competition sandbox and the brain are close to each other, conceptually. A deeper separation is with the communication layer/middleware. This module ensures the brain and the components access all the information possible.

Agents need to be robust against different kind of non-stationarities: agents could die, new appear, macrovariable drastically change. How to avoid the overall system of lead to an endogenous crisis triggered by a small variation is external variables? In other words, how to ensure a small degree of chaoticity/fragility against external perturbations?

# Legacy Notes to be Integrated in v2.

## types

These types are global data structures:

#### Range

Represents a range of values

 * min `uint`
 * max `uint`

#### Machine

The ID of the machine is the IPFS cid of the JSON document with the following structure.

Represents a hardware vm or other such machine that resource offers are made from.

This is read-only metadata used to inform the market place of the actual topology of the network.

This enables resource providers to advertise machine capacity without having to constantly post resource offers.
 
 * owner `address`
 * created `uint` UTC time stamp the machine was created
 * timeout `uint` the number of seconds since the created date the machine is no longer valid
 * CPU `uint`
 * GPU `uint`
 * RAM `uint`
 * labels `map[string]string`

#### ResourceOffer (RO)

The ID of the resource offer is the IPFS cid of the JSON document with the following structure.
 
 * owner `address`
 * target `address` (can be null - the job creator this offer is for)
 * created `uint` UTC time stamp the resource offer was created
 * timeout `uint` the number of seconds since the created date the resource offer is no longer valid
 * CPU `uint`
 * GPU `uint`
 * RAM `uint`
 * prices `map[string]uint`
   * this is price per instruction for each module
  
#### JobOffer (JO)

The ID of the job offer is the IPFS cid of the JSON document with the following structure.

 * owner `address`
 * target `address` (can be null - the resource provider this offer is for)
 * CPU `Range`
 * GPU `Range`
 * RAM `Range`
 * module `string`
 * price `uint`
   * this is price per instruction

#### Deal

The agreement of a RP and JC for a RO and JO

 * resourceProvider `address`
 * jobCreator `address`
 * resourceOffer `CID`
 * jobOffer `CID`
 * timeout `uint`
 * timeoutDeposit `uint`
 * jobDeposit `uint`
 * resultsMultiple `uint`
 
## identity

All services will have a `PRIVATE_KEY` used to sign messages.

It should be easy to derive an `address` from that private key that we can use as an identity.

We will use the same private key and address across both smart contract and non smart contract RPC calls.

Each of the services making and accepting api requests from other services must use the private key to sign and identify requests.

The simulator doesn't need to do actual crypto but it must use the concept of `an address signed this` to authenticate and authorise requests.

## IPFS, CIDs and directory service

There are various mentions of CIDs throughout this document - e.g. the Job Offers, Resource Offers and Deals are communicated with the smart contract only using their IPFS CID.

So, any service that interacts with the smart contract must be able to write and resolve CIDs to and from IPFS.

In the case of the results - we need to ensure the results were available to the job creator to ensure they cannot claim they could not download the results.

For this reason, we use a `directory` service that is used to store the results by the resource provider and confirm availability to the job creator.

The directory service will use the same CID to identify content and will utilize IPFS to store the content and distribute it to the rest of the IPFS network.

Job creators and resource providers can list their trusted directory services - if the config is not provided, it will use the default option registered on the contract (i.e. the default services run by us).

For a match to occur - both sides must have an overlap in their trusted directory services.

Nodes can run their own directory services and call `registerServiceProvider` and any other node can change which directory services they trust.

TODO: how do directory serices get paid? (is this v2 protocol?)

## solver

The service that matches resource offers and job offers.

The solver will eventually be removed in favour of point to point communication.

For that reason - the solver has 2 distinct sides to it's api, the resource provider side and job creator side.

The resource provider and job creator will have their **own** api's - seperate to these that their respective CLI's will use.

Job creators and resource providers can be configured to point at a different solver - if the config is not provided, it will use the default option registered on the contract (i.e. the default services run by us).

The match happens on the solver so the resource provider and job creator must be pointing at the same solver for matches to be made.

The default solver service will be run by us, other nodes can run their own directory services and call `registerServiceProvider`

#### solver stages

It should be possible for nodes to publish their offers to multiple solvers (as in advertise in multiple marketplaces).  However, the solver will be replaced by a libp2p transport in the future and so is a stop-gap and not worth.

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

## meditor

The service that re-runs jobs to check what happened.

Job creators and resource providers can list their trusted mediators - if the config is not provided, it will use the default option registered on the contract (i.e. the default services run by us).

For a match to occur - both sides must have an overlap in their trusted mediators.

Nodes can run their own mediator services and call `registerServiceProvider` and any other node can change which mediator services they trust.

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

 * `setDefaultServiceProvider(serviceType, ID)` (admin)
    * register the given service provider as a default
 * `unsetDefaultServiceProvider(serviceType, ID)` (admin)
    * un-register the given service provider as a default

 * `unregisterServiceProvider(serviceType)`
    * serviceType `ServiceType`
    * ID = msg._sender

 * `listServiceProviders(serviceType) returns []address`
    * serviceType `ServiceType`
    * returns an array of IDs for the given service type

 * `getServiceProvider(serviceType, ID) returns (url, metadata, isDefault)`
    * serviceType `ServiceType`
    * ID `address`
    * url `string`
    * metadata `CID`
    * isDefault `bool`
      * is this service provider a default
    * return the URL and metadata CID for the given service provider

#### deals

 * `agreeMatch(party, dealID, directoryService, mediatorService, timeout, resultsMultiple, timeoutDeposit, jobDeposit)`
   * for the deal to be valid - the second party to agree MUST match exactly the same values as the first
   * party `ServiceType` - this must be either resourceProvider or jobCreator
   * dealID `CID`
   * directoryService `address`
     * the mutually agreed directory service used to transport specs and results
   * mediatorService `address`
     * the mutually agreed mediator service used to mediate results
   * timeout `uint`
     * the agreed upper bounds of time this job can take - TODO: is this in seconds or blocks?
   * resultsMultiple `uint`
     * the agreed multiple of the fee the resource provider will post when submitting results
   * timeoutDeposit `uint`
     * the agreed amount of deposit that will be lost if the job takes longer than timeout
     * if ServiceType == 'resourceProvider' this must equal msg._value
   * jobDeposit `uint`
     * the amount of deposit that will be lost if the job creator does not submit results
     * if ServiceType == 'jobCreator' this must equal msg._value

 * `getDeal(ID) returns (Deal)`
   
 * `submitResults(dealID, resultsCID, instructionCount, resultsDeposit)`
    * dealID `CID`
    * resultsCID `CID`
    * instructionCount `uint`
    * resultsDeposit `uint` (msg._value)
    * submit the results of the job to the smart contract

#### events

 * `ServiceProviderRegistered(serviceType, ID, url, metadata)`
   * serviceType `ServiceType`
   * ID = msg._sender
   * url `string`
     * this is the advertised network URL, used by directory and solver
   * metadata `CID`

 * `ServiceProviderUnregistered(serviceType, ID)`
   * serviceType `ServiceType`
   * ID = msg._sender
  
 * `MatchAgreed(party, dealID, directoryService, mediatorService, timeout, resultsMultiple, timeoutDeposit, jobDeposit)`
   * party `ServiceType`
   * dealID `CID`
   * directoryService `address`
   * mediatorService `address`
   * timeout `uint`
   * resultsMultiple `uint`
   * timeoutDeposit `uint`
   * jobDeposit `uint`

 * `DealAgreed(dealID)`
   * dealID `CID`
   * is called once both parties have called `MatchAgreed`
   * can then use `getDeal(ID)` to get details of deal

## solver

The following api's are what the resource provider and job creator will use to communicate with the solver.

Each API method will have access to a `TX` object that contains the address of the client.

#### resource provider

 * `createMachine(machineID, machine)`
   * machineID `CID`
   * machine `Machine`
   * list all machines for the resource provider

 * `createResourceOffer(resourceOfferID, resourceOffer, target)`
   * resourceOfferID `CID`
   * resourceOffer `ResourceOffer`
   * target `address` (can be zero)
   * tell parties connected to this solver about the resource offer
     * if `target` is specified - only tell the job creator with that address

 * `cancelResourceOffer(resourceOfferID)`
   * resourceOfferID `CID`
   * cancel the resource offer for everyone
   * this should be called once a match is seen

 * `resetResourceProvider()`
   * reset the resource provider state based on the tx passed in

#### resource provider autonomous agent

 * pro-active
   * always post new resource offers of a configured arrangement
   * possibly over-subscribe offers
   * agree any match
   * don't over-subscribe active deals
 * passive
   * wait for job offers that match
   * only post resource offer in response
   * agree any match
   * don't over-subscribe active deals

#### job creator

 * `createJobOffer(jobOfferID, jobOffer, target)`
   * resourceOfferID `CID`
   * jobOffer `JobOffer`
   * target `address` (can be zero)
   * tell parties connected to this solver about the job offer
     * if `target` is specified - only tell the resource provider with that address

 * `cancelJobOffer(jobOfferID)`
   * jobOfferID `CID`
   * cancel the job offer for everyone
   * this should be called once a match is seen

 * `resetJobCreator()`
   * reset the job creator state based on the tx passed in

#### job creator autonomous agent

Keep track of jobs in flight and use a random chance to decide if to challenge - i.e. the bus ticket method.

#### both

Methods called by both sides - all methods are context aware i.e. only return targeted offers for that address.

 * `listMachines(query) returns []Machine`
   * query `map[string]string`
     * `owner` = the address of the resource provider
   * returns an array of machines registered with this solver matching the query

 * `listResourceOffers() returns []ResourceOffer`
   * returns an array of resourceOffers that the msg._sender can see
   * this means resource offers that have been broadcast to everyone AND ones that have been sent to the msg._sender directly

 * `getResourceOffer(resourceOfferID) returns ResourceOffer`
   * throw error if msg._sender cannot see the resource offer
   * this means resource offers that have been broadcast to everyone AND ones that have been sent to the msg._sender directly

 * `listJobOffers() returns []JobOffer`
   * returns an array of jobOfferID's that the msg._sender can see
   * this means job offers that have been broadcast to everyone AND ones that have been sent to the msg._sender directly

 * `getJobOffer(jobOfferID) returns JobOffer`
   * throw error if msg._sender cannot see the job offer
   * this means resource offers that have been broadcast to everyone AND ones that have been sent to the msg._sender directly

#### events

Global resource/job offers are broadcast to everyone
Targeted resource/job offers only sent to the target subscriber

 * `onResourceOfferCreated(handler)`
   * handler `function(resourceOfferID, ResourceOffer)`
   * called when new resource offers are seen
   
 * `onResourceOfferCancelled(handler)`
   * handler `function(resourceOfferID, ResourceOffer)`
   * called when resource offers are cancelled

 * `onJobOfferCreated(handler)`
   * handler `function(jobOfferID, JobOffer)`
   * called when new job offers (either global or targeted) are seen

 * `onJobOfferCancelled(handler)`
   * handler `function(jobOfferID, JobOffer)`
   * called when job offers are cancelled

 * `onMatch(handler)`
   * handler `function(jobOfferID, resourceOfferID)`
   * called when new matches are made

## resource provider

The resource provider will connect to a solver and create resource offers.

It will connect to the solver by listing solvers from the smart contract and then using one (or more) to create resource offers and agree to matches.

#### config

Things we configure the resource provider with:

 * private key
 * metadata CID
 * machine id
 * machine spec
 * directory addresses
 * mediator addresses
 * solver address
