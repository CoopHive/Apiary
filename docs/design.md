# Coophive Multi-Agent System Design

## Abstract

This is a document to conceptualize the high-level design choices of Coophive, with regards to its multi-agent systems, data-driven optimal control, agent-to-agent negotiation and scheduling. It serves as the reference point to define the building blocks of the agent marketplace and its APIs to both on-chain and other off-chain modules of the protocol. When possible, the discussion is kept general, while when necessary the specificities of the exchanged assets (storage, compute) will be introduced. 

The framework is nevertheless defined for "validatable, terminable tasks with collateral transfer after validation". In this context, we talk about "stateless" tasks to stress their inner reproducibility (their lack of dependence against client-specific state variables). The presence of agent-based modeling (whose policy is potentially data-driven, tapping into ML/RL), is motivated by the need to orchestrate a decentralized network of agents in a way that leads to competitive pricing/scheduling, from the user perspective. At the same time, the use of blockchain is motivated by the trustless and automatic transfer of collateral after validation.

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

It appears pretty evident that in the setup of Multi-agent training following greedy policies, the system will end up being [more fragile](https://ceur-ws.org/Vol-2156/paper1.pdf). 

This makes it necessary to have an holistic training setup in which the action space of agents is limited (equivalent of policy-making). This may have the consequence of each agent to [behave suboptimally](https://www.linkedin.com/posts/jean-philippe-bouchaud-bb08a15_how-critical-is-brain-criticality-activity-7000544505359654912-ETjz?utm_source=share&utm_medium=member_desktop), but the system may need to tolerate a certain degree of inefficiency in order to gain robustness.

Related works about the chaotic nature of the learning trajectory, make it necessary to willingly develop and implement underfitted policies to avoid ill-posed problem statements:

- https://pubmed.ncbi.nlm.nih.gov/11930020/
- https://pubmed.ncbi.nlm.nih.gov/29559641/
- https://pubmed.ncbi.nlm.nih.gov/23297213/

In this holistic perspective, a deep conceptual separation between the intelligent and strategic layer is necessary. This is a central node interacting with the agents competition pool, making sure agents are able to act and that the [Cyber-Physical System as a whole](https://retis.sssup.it/~nino/publication/eumas17.pdf) is achieving what it needs to achieve: in other terms, in the spirit of complex systems theory, the fitness function of the network is different from the sum of the fitness functions of agents composing it.

This central node can learn general laws of behaviour based on the goals of the overall system and the behaviour of its components.

The system need to be robust against different kind of non-stationarities: agents could disappear, new appear, macro-variable drastically change. How to avoid the overall system of lead to an endogenous crisis triggered by a small variation in its external variables? In other words, how to ensure a small degree of chaoticity/fragility against perturbations?

### Note On Centralized Solvers

We think of centralized solvers as particular kinds of agents, interested in allocating jobs, in the presence of agents lacking negotiation/scheduling capabilities. Behaviour resambling centralized solvers may emerge in a purely peer-to-peer system but the concept of solver is not a primitive building block within the protocol.

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

The specifications of the machine (hardware or virtual machine) associated with an agent (in turn, associated with a public key), include:

 * CPU
 * GPU
 * RAM

These information may or may not be recorded on-chain; regadless, profiling enables agent to know their own states and inform their policies with this information.

Together with a public key necessarily recorded on-chain, agents are associated with a private key used to sign messages as well.

Every agent hardware specifications may limit the state space size. For example, some IoT actors would only be able to remember and act based on on-chain data, while others may be able to have a bigger memory and bigger state space. For the same reason, some agents may be unable to perform certain tasks (that may be costly and limited by time, in fact the validation could also check constraints in the tasks, like the time it took to complete.). In other words, each agent has different constraints on both their state space and action space.

A task shall be associated with a variable specifying the possibility for it to be distributed. It could also specify the specific/maximum/minimum number of agents to take the task. The minimum case is to enforce federate learning in the case in which sensitive data needs to be broken down. This creates a negotiation with some kind of waiting room in which people can subscribe to participate and can opt-out before the room is full. From the resource provider side, the federate learning scenario could also motivate the introduction of a *Swarm* abstraction, combining different agents that decide to cooperate to a certain degree, for example sharing their state space or their policies.

### Additional Considerations

A straightforward definition of fitness is profit.

About the integration of bundles of assets in the agent-to-agent negotiation picture, it regardless appears necessary to introduce a [Numéraire](https://en.wikipedia.org/wiki/Num%C3%A9raire) shared by all agents. If different agents have different priors on the value of a given asset, it becomes challanging to have a well posed interaction.

An important point is the generality of the action space of agents. While the main manifestation of policies is in they being triggered by messages/offers and returning messages/counteroffers, there are other actions, which include reading and writing of of-chain states (e.g., singing an attestation and linking it to a reply message) and the execution of the job itself, with all the required associated on-chain actions.

While the bulk of the policy, and its potential data-driven nature, resides in the production of messages defining actions in the domain of negotiation and scheduling, it's important to keep in mind the general action space of agents, including interaction with on-chain states.

When necessary, data stored on IPFS is associated with smart contracts using [CIDs](https://docs.ipfs.tech/concepts/content-addressing/). Agents shall be able to interact with IPFS as well, reading, downloading, uploading data to the protocol and linking it to on-chain actions.

## Job

Some examples of a Job Schema are, for compute (stateless) tasks:
- A docker image and its input(s);
- A github repository and an associated command.

Because we are interested in storage tasks as well, a valuable perspective is decomposing Jobs into modular pieces associated with each other and creating a [DAG](https://en.wikipedia.org/wiki/Directed_acyclic_graph). This is a natural paradigm for expressing data processing pipelines, machine learning in particular.

 Triggers of modules of purely compute tasks are previous nodes, while for storage tasks sequential nodes are triggered by previous tasks and/or by a clock. In general, it makes sense to think about jobs using the lenses of MLOps and Orchestration, which are focused on the core part of CoopHive: in fact, once the trustless aspect is solved (blockchain), and once the distributed computing is solved (autonomous agents negotiation), we are back to the world of [traditional orchestration](https://www.prefect.io/opensource) of compute and storage tasks. This means there is added value in building things keeping in mind [orchestration compatibilities](https://docs.metaflow.org/metaflow/basics#the-structure-of-metaflow-code).

Here there is no need to explicitly define DAGs. An [agent-based perspective](https://www.prefect.io/controlflow) is maintained within the task framework.

For us, it is more relevant to think about agents when it comes to competition/cooperation when it comes to task allocation and pricing; nevertheless, with a modularization of compute and storage tasks, it is reasonable to keep in mind the agent-based perspective during the task as well. Collateral could be allocated to specific nodes of a DAG and agents to focus on individual modules of a task.
