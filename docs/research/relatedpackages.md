### OVERVIEW
After reviewing several related autonomous agent/AI projects, there seems to be a trend of a scheduler/agent set superclass as well as a resource/grid/action space/state superclass. Can also sometimes be a policy superclass that drives agents.


### classes_crewai.png (https://docs.crewai.com/)
- **Crew class**: Each crew is comprised of multiple base agents. Each agent is a subclass of `BaseAgent` and has a `CrewAgentExecutor` which logs, iterates, and calls the LLM.
- Each crew also has a list of tasks, where each task has:
  - Base agent
  - Task output
  - Expected output
  - Task context
  - etc.

### classes_mava.png (https://mava.gitbook.io/mava-docs/introducing-mava/what-is-mava)
- **MavaLogger superclass**: Contains multiple logger subclasses.
- **Wrapper classes**: Manage global state, including:
  - Number of agents
  - Action dimensions
  - Time
- **Neural Network**: Appears to be a neural network with values that are passed forward, hidden states, and learner states.
- **Sequential Data**: RNNs handle sequential data where the order of input matters. They maintain a hidden state that updates as each element in the sequence is processed, allowing them to "remember" previous inputs in the sequence.

### classes_meltingpot.png (https://meltingpot.cc/system)
- **Puppeteer superclass**: Has a state and a step. Includes multiple subclasses with different policies, such as:
  - Tit for Tate
  - Respond to previous
  - Reciprocator
  - FixedGoal
- **Policy superclass**: Contains state and step. Subclasses include:
  - `FixedActionPolicy`
  - `PuppetPolicy`
- **Tests and States**: Correspond to types of puppeteer subclasses.
- **Scenario subclass**: Includes subclasses:
  - `Substrate`
  - `Population`
  - `ScenarioObservables`
- **AI Labeling**: Images are labeled by adding the perspective of the data provider.
  - A human inspects the labeling and processes 2-layer labeling for compensation.
  - When the AI operates and generates revenue, the generated results and prompts are analyzed through vision AI.
  - The 2-layer labeling is finalized, and settlement is distributed to the dataset that provided the concept for that label.

### classes_mesa.png (https://github.com/projectmesa/mesa/)
- **Grid superclass**: Includes property grid subclass, with further subclasses:
  - `SingleGrid`
  - `MultiGrid`
  - `HexGrid`
- **BaseScheduler superclass**: Manages agents, model, time, step, and steps. Includes subclass `AgentSet`, which has a subclass `Model`.
- **Model subclass**: Inherits from `Simulator`, `Agent`, and `AgentSet`.
- **Trends**:
  - A scheduler or agent set superclass.
  - A resource or grid or action space superclass.
  - Sometimes a policy superclass that drives agents.

### classes_openhands.png (https://github.com/All-Hands-AI/OpenHands)
- **CodeActAgent**: This agent implements the `CodeAct` idea that consolidates LLM agents’ actions into a unified code action space for both simplicity and performance. The conceptual idea is as follows:
  - **Converse**: Communicate with humans in natural language to ask for clarification, confirmation, etc.
  - **CodeAct**: Choose to perform the task by executing code.
