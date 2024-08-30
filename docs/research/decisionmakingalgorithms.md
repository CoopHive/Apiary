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
  - Tempting
