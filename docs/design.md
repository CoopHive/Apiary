# Coophive Multi-Agent System Design

## Abstract

This is a document to conceptualize the high-level design choices of Coophive, with regards to its multi-agent systems, data-driven optimal control, agent-to-agent negotiation and scheduling. It serves as the reference point to define the building blocks of the agent marketplace and its APIs to both on-chain and other off-chain modules of the protocol. When possible, the discussion is kept general, while when necessary the specificities of the exchanged assets (storage, compute) will be introduced. 

The framework is nevertheless defined for "validatable, terminable tasks with collateral transfer after validation". In this context, we talk about "stateless" tasks to stress their inner reproducibility (their lack of dependence against client-specific state variables). The presence of agent-based modeling (whose policy is potentially data-driven, tapping into ML/RL), is motivated by the need to orchestrate a decentralized network of agents in a way that leads to competitive pricing/scheduling, from the user perspective. At the same time, the use of blockchain is motivate by the trustless and automatic transfer of collateral after validation.

## Introduction

The problem statement starts with the presence of a chain-generic/asset generic marketplace to interact optimally against. There are deep implications about going for a chain-generic or more specific marketplace, but this does not seem to have implications on the multi-agent module of the protocol.

The value of this protocol lies in, for example, identifying idle computational resources around the world and potential tasks that might be willing to trade something in exchange for utilizing those resources. This landscape creates an off-chain market of negotiations in which agents compete/cooperate to cut a good deal, i.e., they act optimally with respect to their fitness landscape, their action space and their state space (like in every market, negotiation helps the bid inform a "fair market value").

While the outcome of each negotiation goes on chain, negotiations are performed off-chain, and both on-chain and off-chain data can be used to inform various negotiation strategies.

## The case for Agent-based modeling

The existance of distributed and heterogenous hardwares and the construction of data-driven policies for optimal decision making does not motivate by itself the usage of an agent-based perspective in the modeling of the system. For example, a centralized solver could be implemented to distribute jobs efficiently across the network. 

However, one conceptual advantage is that with an agent-based perspective nodes participating in the network keep *agency* over themselves, i.e. they are continuously able to accept or reject jobs, and this capatibility is never delegated to a central entity.

Moreover, an [agent-based perspective](https://www.doynefarmer.com/publications) can be used to relax conventional assumptions in standard models and, in the spirit of [complex systems theory](https://www.econophysix.com/publications), views marco phenomena such as centralized solvers and order books, in our context, as *emerging properties* of the atomic units of behaviour. This perspective has the potential to avoid the suboptimality following the choice of a misspecificed macro model.

### 1 vs N, N vs 1, N vs N

The most generic case to be considered is an N (clients) vs N (resource providers). While in principle there are aspects of the generic case that are not captured by either kind of stacking of more specific cases, it is reasonable to start thinking about the N vs N as a set of more simple cases. 

In the 1 (agent) vs N (static environment of clients), the problem is mainly scheduling/path planning in the space of tasks. This would basically mean ignoring the presence of multiple agents and just ask ourselves how each of them, blind to the presence of their peers, would move in the space of posted jobs to maximize their utility.

In the N (agents) vs 1 dynamic client/job offer, the problem is more purely a negotiation problem.

It is reasonable to assume optimal policies will be characterized by a trade-off between negotiation and scheduling, related to the concept of [Explore-exploit dilemma](https://ml-compiled.readthedocs.io/en/latest/explore_exploit.html).

### Network Robustness

Reading “Timing Reliability for Local Schedulers in Multi-Agent Systems”: it seems pretty evident that in the setup of Multi-agent training following greedy policies, the system will end up being more fragile. I don’t think we can avoid an holistic training setup in which a degree of cooperation is instilled in each agent. This will have the consequence of each agent to behave suboptimally, and the system will become subscettible to greedy attacks. I believe the system will need to tollerate a certain degree of corruption/inefficiency in order to gain robustness.
Analogous situation in which greedy policies don’t work (see Section 5.1): https://web.stanford.edu/~boyd/papers/pdf/cvx_portfolio.pdf
Even more relevant, the concept of self-organized criticality: https://www.linkedin.com/posts/jean-philippe-bouchaud-bb08a15_how-critical-is-brain-criticality-activity-7000544505359654912-ETjz/

Not clear how to formalize/verify/deal with this point, but worth mentioning.

Related works about the chaotic nature of the learning trajectory, making it necessary for us to start with trivial/underfitted policies and slowly complexify things:

- https://pubmed.ncbi.nlm.nih.gov/11930020/
- https://pubmed.ncbi.nlm.nih.gov/29559641/
- https://pubmed.ncbi.nlm.nih.gov/23297213/

Reading "Local Scheduling in Multi-Agent Systems: getting ready for safety-critical scenarios”: is is clear that we need a deep conceptual and practical separation between the intelligent/strategic layer. This is a central node interacting with the agents competition pool, making sure agents are able to act and that the CPS as a whole is achieving what it needs to achieve. This central node can learn general laws of behaviour based on the goals of the overall system and the behaviour of its components. In this sense, the competition sandbox and the brain are close to each other, conceptually. A deeper separation is with the communication layer/middleware. This module ensures the brain and the components access all the information possible. What I called "brain" here could be a centralized solver. These considerations related to the design choice of pure agent-based scheduling/negotiation vs centralized solver for tasks allocation.

Agents need to be robust against different kind of non-stationarities: agents could die, new appear, macrovariable drastically change. How to avoid the overall system of lead to an endogenous crisis triggered by a small variation is external variables? In other words, how to ensure a small degree of chaoticity/fragility against external perturbations?

## State Space

Autonomous Agents are associated with policies why are defined in conjunction with a state space. The dimensions of such state space can be categorized in different ways. One way is distinguishing between both local states (i.e., variables associated with agents themselves) and global information (i.e., global, environmental variables which are not a function of the agent). Another categorization is distinguishing between off-chain and on-chain states.

### Messaging

A central piece, in the definition of global, off-chain states of agents is the centralized messaging node, the [PubSub](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern). This node contains a set of recorded messages, that every agent can listen to (and decide to store locally, to go back to a [Markovian framework](https://en.wikipedia.org/wiki/Markov_decision_process) in informing the policies, if necessary). A question is for example how important it is for agents to observe the negotiation dynamics before an agreement vs learning from final transactions only: this has consequences on the privacy of offers, as it may be valuable to enforce the publicity of intra-negotiation offers for a more transparent auction mechanism. The messaging scheme defines the most important block of the state space, informing negotiations and scheduling, and also defines part of the action space of agents.

### Global States

A set of environmental variables appearing necessary for actors to construct optimal policies include:

- L1 and L2 tokens price. We believe the dynamics of the protocol, being based on smart contracts and EVM technology, to be driven by the state of the L1 (Ethereum) and L2 protocol. One shallow proxy for this is the point-in-time price of the two protocols. A deeper understanding of the protocol dynamics could inform the modeling of payment token prices forecasting, informing the optimal behaviour of agents in this blockchain-based marketplace.

- Gas Fees: because of the need to record the outcome of a negotiation on the blockchain, the point-in-time gas fees of the protocol blockchain is necessary to build policies. This is akin to a time-dependent transaciton cost model in trad-fi: the profitability of a position is a function of the (current) transaction costs. Here we refer to the gas fees of the L2 associated with CoopHive; as per prices, the gas fee time series of Ethereum may be relevant in modeling the dynamics of costs for agents recording states on-chain in the interaction with the protocol.

- Electricity costs. This is a space-time dependent variable defining the cost of electricity in the world. Agents, aware of their own location, are interested in measuring the point-in-time field of the cost of electricity to understand the hedge they may have against other potential agents in different locations. This means that agents may have a module solely focused on the [modeling, forecasting and uncertainty quantification](https://arxiv.org/abs/2106.06033) of electricity prices to enhance the state space and then use that as an input for the optimal controller.

- On-chain states: the history of credible commitments recorded on chain is a valuable information to inform policies. While agents cannot be forced to share their local states on chain, one solution could be to enable an emergent secondary marketplace of jobs specifications, in which machines can associate (and this can be verified) their hardware specifications to a given job. The market is emergent as if agents want to become autonomous and this dataset is valuable, they will create it. An important point, on this, is that an agent looking at a given open job is in principle not able to say exactly its computational cost. It can learn from past data only if they are associated with specific schemas that enable the agent to interpolate the input space of the task for that schema (in the presence of enough datapoints to approximate the cost function).

### Local States

A task offer has to contain the CID of the data needed to perform the task. One could use this as a proxy for the computational cost of a task (even though a task could be associated with light data and be really expensive).

Every agent hardware specifications may limit the state space size. For example, some IoT actors would only be able to remember and act based on on-chain data, while others may be able to have a bigger memory and bigger state space. For the same reason, some agents may be unable to perform certain tasks (that may be costly and limited by time, in fact the validation could also check constraints in the tasks, like the time it took to complete.). In other words, each agent has different constraints on both their state space and action space.

A task shall be associated with a variable specifying the possibility for it to be distributed. It could also specify the specific/maximum/minimum number of agents to take the task. The minimum case is to enforce federate learning in the case in which sensitive data needs to be broken down. This creates a negotiation with some kind of waiting room in which people can subscribe to participate and can opt-out before the room is full. From the resource provider side, the federate learning scenario could also motivate the introduction of a *Swarm* abstraction, combining different agents that decide to cooperate to a certain degree, for example sharing their state space or their policies.

### Additional Considerations

A straightforward definition of fitness is profit.

About the integration of bundles of assets in the agent-to-agent negotiation picture, it regardless appears necessary to introduce a [Numéraire](https://en.wikipedia.org/wiki/Num%C3%A9raire) shared by all agents. If different agents have different priors on the value of a given asset, it becomes challanging to have a well posed interaction.

An important point is the generality of the action space of agents. While the main manifestation of policies is in they being triggered by messages/offers and returning messages/counteroffers, there are other actions, which include reading and writing of of-chain states (e.g., writing an attestation and linking it to a reply message) and the execution of the job itself, with all the required associated on-chain actions.

While the bulk of the policy, and its potential data-driven nature, resides in the production of messages defining actions in the domain of negotiation and scheduling, it's important to keep in mind the general action space of agents.

## Job

Some examples of a Job Schema are, for compute (stateless) tasks:
- A docker image and its input(s);
- A github repository and an associated command;

Because we are interested in storage tasks as well, a valuable perspective is decomposing Jobs into modular pieces associated with each other and creating a [DAG](https://en.wikipedia.org/wiki/Directed_acyclic_graph). This is a natural paradigm for expressing data processing pipelines, machine learning in particular.

 Triggers of modules of purely compute tasks are previous nodes, while for storage tasks sequential nodes are triggered by previous tasks and/or by a clock. In general, it makes sense to think about jobs using the lenses of MLOps and Orchestration, which are focused on the core part of CoopHive: in fact, once the trustless aspect is solved (blockchain), and once the distributed computing is solved (autonomous agents negotiation), we are back to the world of [traditional orchestration](https://www.prefect.io/opensource) of compute and storage tasks. This means there is added value in building things keeping in mind [orchestration compatibilities](https://docs.metaflow.org/metaflow/basics#the-structure-of-metaflow-code).

Here there is no need to explicitly define DAGs. An [agent-based perspective](https://www.prefect.io/controlflow) is maintained within the task framework.

For us, it is more relevant to think about agents when it comes to competition/cooperation when it comes to task allocation and pricing; nevertheless, with a modularization of compute and storage tasks, it is reasonable to keep in mind the agent-based perspective during the task as well. Collateral could be allocated to specific nodes of a DAG and agents to focus on individual modules of a task.

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

Question: how do directory serices get paid? (is this v2 protocol?)

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
     * the agreed upper bounds of time this job can take - Question: is this in seconds or blocks?
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


# tests

A list of the tests we need to run

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

 * RP registers resource offer to solver
 * JC registers job offer to solver


## matching

* solver matches job offer and resource offer
* solver creates deal CID from match
* solver indicates the match to the two parties
* (future) parties agree and sign transactions


## sanity checks

Just checks the simulator is up and functional:

 * check for overlapping addresses
 * check that amount of currency in circulation is constant (accounting for new amounts being added)
 * JC and RP agree to the same deal CID


## generic setup

* `registrations of service providers`
* `boot`
* `registrations of job and resource offers`
* `matching`
* `sanity checks`


## resource provider timeouts

* `generic setup`
* client gets RP timeout collateral
