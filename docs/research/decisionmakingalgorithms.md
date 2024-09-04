## OVERVIEW

These are Aayushi Jain’s notes on the book “Algorithms for Decision Making” by Mykel J. Kochenderfer, Tim A. Wheeler, and Kyle H. Wray. Relevant chapters discussed are:

- **Chapter 1: Introduction**
- **Chapter 6: Simple Decisions**
- **Chapter 7: Exact Solution Methods**
- **Chapter 24: Multiagent Reasoning**
- **Chapter 25: Sequential Problems**

---

### Chapter 1: Introduction
- Interaction between agent and environment follows an observe-act cycle/loop.
- The agent receives an observation of the environment \(o_t\) at time \(t\) and chooses an action \(a_t\) through some decision-making process.
- The action may have a nondeterministic effect on the environment.
- Given the past sequence of observations \(o_1, …, o_t\) and knowledge of the environment, the agent must choose action \(a_t\) in the presence of:
  - Outcome uncertainty
  - Model uncertainty
  - State uncertainty
  - Interaction uncertainty
- **Methods for designing decision-making agents:**
  - **Explicit programming**: Anticipate all potential scenarios and explicitly program responses for each one.
  - **Supervised learning**: Show an agent what to do with training examples, and an automated learning algorithm must generalize from these examples.
  - **Optimization**: Specify the space of possible decision strategies and a performance measure to be maximized. Then perform a search in this space for the optimal strategy.
  - **Planning**: Focus on deterministic problems.
  - **Reinforcement learning**: The model is not always known ahead of time; the decision-making strategy is learned while the agent interacts with the environment. Only need to provide a performance measure.
- **Utility theory & maximum expected utility**
- **Game theory**: Understand the behavior of multiple agents acting in the presence of one another to maximize their interests.
- **Components of decision-making**: Probabilistic reasoning, sequential problems, model uncertainty, state uncertainty, multiagent systems.
- Represent uncertainty using probability distributions over many variables. Construct models, make inferences, and learn parameters and structure from data.

---

### Chapter 6: Simple Decisions
- Make a single decision under uncertainty (different from sequential problems).
- Model the preferences of an agent as a real-valued function over uncertain outcomes.
- **Value of information** measures utility gained through observing additional variables.
- **Constraints on rational preferences**:
  - **State preferences** (which can be subjective) and use preference operators to compare preferences over uncertain outcomes.
  - **Lottery**: Set of probabilities associated with a set of outcomes.
  - **Completeness**: Either prefer A over B, B over A, or are indifferent.
  - **Transitivity**: If A is preferred or indifferent to B, and B is preferred or indifferent to C, then A is preferred or indifferent to C.
  - **Continuity**: The continuity axiom states: If A ≽ C ≽ B, then there exists a probability \(p\) such that \([A : p; B : 1 − p] \sim C\).
    - This principle ensures that preferences are continuous and that there are no "jumps" in preference. It means that if you prefer outcome A to C, and C to B, then there must be some probability \(p\) where you'd be indifferent between:
      - a) Getting C for sure
      - b) A lottery that gives you A with probability \(p\) and B with probability \(1-p\).
    - This axiom allows for the mathematical representation of preferences using real-valued utility functions. It essentially says that you can always find a "middle ground" between two outcomes by adjusting probabilities.
  - **Independence**: If \(A ≻ B\), then for any C and probability \(p\), \([A : p; C : 1 − p] ≽ [B : p; C : 1 − p]\).
    - If you prefer outcome A to outcome B, then this preference should be maintained when A and B are part of identical compound lotteries.
    - The presence of a common consequence (C) with the same probability \(1-p\) in both lotteries should not affect your preference between A and B.
- **Utility functions**:
  - For a real-valued utility function \(U\), \(U(A) > U(B)\) if and only if \(A ≻ B\), and \(U(A) = U(B)\) if and only if \(A ∼ B\).
  - Utility function is unique across positive affine/linear transformations.
- **Utility elicitation**:
  - Fix the utility of the worst outcome \(S\) to 0 and the best outcome to 1.
  - As long as utilities of outcomes are bounded, we can translate and scale the utilities without altering preferences.
  - To determine the utility of outcome \(S\), determine \(p\) such that \(S ∼ [S : p; S : 1 − p]\). Thus, \(U(S) = p\).
  - Find a probability \(p\) such that the decision-maker is indifferent between:
    - a) Getting outcome \(S\) for certain
    - b) A gamble that gives the best outcome \((S*)\) with probability \(p\) and the worst outcome \((S*)\) with probability \(1-p\).
  - **Von Neumann-Morgenstern utility assignment**: If you're indifferent between a certain outcome and a gamble between the best and worst outcomes, the probability of getting the best outcome in that gamble represents your utility for the certain outcome.
    - This approach ensures that utilities are on a scale from 0 to 1.
- **Utility of wealth**:
  - Tempting to use monetary values to infer utility functions, but the utility of wealth is not linear.
  - We generally want to maximize the expected utility of wealth where different people have different utility functions.
  - **Risk neutral vs. risk seeking vs. risk averse**:
    - Common functional forms for modeling risk aversion of scalar quantities like wealth: quadratic utility, exponential utility, or power/logarithmic utility.
- **Maximum expected utility principle**: A rational agent should choose the action that maximizes expected utility.
- **Decision networks/influence diagrams**: Generalization of Bayesian networks to include action and utility nodes so we can represent probability and utility models defining a decision problem:
  - **Chance node** corresponds to a random variable (RV).
  - **Action node** corresponds to a decision variable.
  - **Utility node** corresponds to a utility variable and cannot have children.
  - **Conditional edge**: Ends in a chance node and indicates uncertainty that the chance node is conditioned on the values of its parents.
  - **Informational edge**: Ends in an action node and indicates that the decision associated with that node is made with knowledge of the values of its parents.
  - **Functional edge**: Ends in a utility node and indicates that the utility node is determined by the outcomes of its parents.
  - Cannot have cycles; utility of an action = sum of values at all utility nodes.
- **Value of information**: The increase in expected utility if that variable is observed.
  - Never negative.
  - The expected utility can increase only if additional observations can lead to different optimal decisions.
  - If observing a new variable \(O′\) makes no difference in the choice of action, then \(EU∗(o, o′) = EU∗(o)\) for all \(o′\), in which case equation (6.9) evaluates to 0.
  - For example, if the optimal decision is to treat the disease regardless of the outcome of the diagnostic test, then the value of observing the outcome of the test is 0.
  - The value of information is an important metric for choosing what to observe (greedy selection of observations).
- **Irrationality**:
  - A smaller gain that is certain is often preferred over a much greater gain that is only probable, in a way that the axioms of rationality are necessarily violated.
- Solving a simple decision involves inference in Bayesian networks and is thus NP-hard.

## SEQUENTIAL PROBLEMS

Sequential decision problems in stochastic environments. General formulation of sequential decision problems under the assumption that the model is known and that the environment is fully observable.

### Chapter 7: Exact Solution Methods

**Markov Decision Processes (MDPs)**
- **Model**: Represents sequential decision problems where effects of actions are uncertain.
- **A**: Set of possible actions/action space (not required to be finite).
- **S**: State space/set of possible states (not required to be finite).
- **Markov Assumption**: The next state depends only on the current state and action, not on any prior state or action.
- **Utility Function**: Decomposed into rewards \( R_1 - R_t \). The reward function \( R(s, a) \) represents the expected reward when executing action \( a \) from state \( s \). It is a deterministic function of \( s \) and \( a \) because it represents an expectation.
- **Discount Factor**: Used in infinite horizon problems where the discount factor \( \gamma \) is between 0 and 1. The utility is given by \( \sum_{t=1}^{\infty} \gamma^{t-1} r_t \). This value is sometimes called the discounted return. As long as \( 0 \leq \gamma < 1 \) and the rewards are finite, the utility will be finite. The discount factor makes rewards in the present worth more than those in the future. A discount factor close to 1 is desirable.
- **Policy**: Defines what action to select given the past history of states and actions. The action to select at time \( t \), given the history \( h_t = (s_{1:t}, a_{1:t-1}) \), is written \( \pi_t(h_t) \). Since future states and rewards depend only on the current state and action, policies can be restricted to depend only on the current state.
- **Stationary Policy**: Does not depend on time.
- **Finite Horizon Problems**: It can be beneficial to select different actions depending on how many time steps remain. For example, attempting a half-court shot in basketball is generally only a good strategy if there are only a few seconds remaining. Stationary policies can account for time by incorporating time as a state variable.

### Policy Evaluation
- **Value Function**: \( U_\pi \) is the value function associated with an optimal policy \( \pi^* \). It can be computed iteratively.
- **Single-Step Utility**: If the policy is executed for a single step, the utility is \( U_1^\pi(s) = R(s, \pi(s)) \).
- **Lookahead State-Action Function**: Computed for further steps from a state \( s \) given an action \( a \), using an estimate of the value function \( U \) for the MDP \( \mathcal{P} \).
- **Iterative Computation**: Compute the value function for a policy \( \pi \) for MDP \( \mathcal{P} \) with discrete state and action spaces using \( k_{max} \) iterations with the lookahead function.
- **Direct Evaluation**: Policy evaluation can be done without iteration by solving the system of equations in the Bellman expectation equation directly.

### Value Function Policies
- **Value Function**: Tells us how good it is to be in a particular state.
- **Policy**: Tells us what action to take in a given state.

### Extracting a Policy from a Value Function
- **Greedy Policy**: Create a policy by always choosing the action that leads to the best expected outcome.

### Action Value Function (Q-function)
- **Q-function**: Calculates the value of taking a specific action in a state. It considers the immediate reward of the action plus the expected future value.
- **Using the Q-function**:
  - The value of a state is the maximum Q-value for any action in that state.
  - The best action to take is the one with the highest Q-value.

### Advantage Function
- **Advantage Function**: Tells us how much better (or worse) an action is compared to the best action.
- **Calculation**: Subtract the state value from the action value. The best action always has an advantage of zero, while worse actions have negative advantages.

### Policy Iteration
- **Method**: A way to compute an optimal policy. Iterate between policy evaluation and policy improvement through a greedy policy. Guaranteed to converge because there are finitely many policies, and every iteration improves the policy if it can be improved. It is an expensive process.

### Value Iteration
- **Updates the Value Function Directly**:  
  It begins with any bounded value function \( U \), meaning that \( |U(s)| < \infty \) for all \( s \). One common initialization is \( U(s) = 0 \) for all \( s \).
  
- **Bellman Backup/Bellman Update**:  
  The value function can be improved by applying the Bellman backup/Bellman update:
  \[
  U(s) = \max \left( R(s,a) + \gamma \sum_{s'} T(s' | s,a)U(s') \right)
  \]

### Computationally Intensive -> Async Value Iteration
- **Asynchronous Value Iteration**:  
  Only a subset of the states are updated with each iteration.
  
- **Gauss-Seidel Value Iteration**:  
  Does not require constructing a second value function in memory with each iteration.

### Linear Program Formulation
- **Convert Bellman Optimality Equation into a Linear Program**:  
  The number of variables is equal to the number of states, and the number of constraints is equal to the number of states times the number of actions.

### Linear Systems with Quadratic Rewards
- **Not Applicable to Us**

### Summary
- Discrete MDPs with bounded rewards can be solved exactly through dynamic programming.
- Policy evaluation for such problems can be done exactly through matrix inversion or can be approximated by an iterative algorithm.
- Policy iteration can be used to solve for optimal policies by iterating between policy evaluation and policy improvement.
- Value iteration and asynchronous value iteration save computation by directly iterating the value function.
- The problem of finding an optimal policy can be framed as a linear program and solved in polynomial time.
- Continuous problems with linear transition functions and quadratic rewards can be solved exactly.



### Chapter 24: [TODO]
### Chapter 25: [TODO]
