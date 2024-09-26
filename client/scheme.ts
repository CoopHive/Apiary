/**
 * Represents an Algebraic Data Type (ADT) with a tag.
 */
export interface ADT {
  _tag: string;
}

/**
 * Represents a negotiation protocol.
 * @template T - A discriminated union representing all possible messages.
 * @template R - A string literal union of roles.
 */
export type Scheme<T extends ADT, R extends string> = {
  /**
   * Defines rules for valid responses to messages.
   * @param client - Provides methods for managing communication.
   * @param role - The agent's role in the scheme.
   * @param input - Message responded to.
   * @param output - Agent response to input.
   * @returns A promise that resolves to true if the response is valid, false otherwise.
   *
   * Implementation notes:
   * - Return true if the response is valid in context, false otherwise.
   * - Use client.subscribe() to start listening about an offerId.
   * - Use client.unsubscribe() to stop listening about an offerId.
   * - Use client.send() to broadcast messages.
   */
  onAgent(
    client: SchemeClient<T>,
    role: R,
    input: Message<T>,
    output: Message<T>
  ): Promise<boolean>;

  /**
   * Defines rules for valid parameters when initializing an agent
   * @param client - Provides methods for managing communication.
   * @param role - User input for the agent's role in the scheme.
   * @param init - Optional initial message to be sent when joining.
   * @returns A promise that resolves to true if the role and initial message are valid, false otherwise.
   *
   * Implementation notes:
   * - Return true if the role and initial message are valid, false otherwise.
   *    - `role` is a user input at this point. Do not assume it is a member of R.
   * - Use client.subscribe() to set up initial message listeners.
   * - Use client.send() to broadcast messages.
   */
  onStart(
    client: SchemeClient<T>,
    role: string,
    init?: Message<T>
  ): Promise<boolean>;
};

/**
 * Represents an infrastructure client for a negotiation scheme.
 * @template T - A discriminated union representing all possible messages.
 */
export type SchemeClient<T extends ADT> = {
  /**
   * Connects to communication infrastructure and calls `scheme.onStart(init?)`.
   * @param init - Optional initial message to send upon connection.
   * @returns A promise that resolves to true if connection and initial message (if any) are successful.
   */
  start: (init?: Message<T>) => Promise<boolean>;

  /**
   * Starts listening for messages related to a specific offer or the default channel.
   * @param offerId - Optional offer ID to listen for. If not provided, listens on the default channel.
   * @returns A promise that resolves to true if subscription is successful.
   */
  subscribe: (offerId?: string) => Promise<boolean>;

  /**
   * Stops listening for messages related to a specific offer or the default channel.
   * @param offerId - Optional offer ID to unsubscribe from. If not provided, unsubscribes from the default channel.
   * @returns A promise that resolves to true if unsubscription is successful.
   */
  unsubscribe: (offerId?: string) => Promise<boolean>;

  /**
   * Sends a message to all subscribers of a specific offer or the default channel.
   * `message.initial` should be true for default channel messages.
   * @param message - The message to send.
   * @returns A promise that resolves to true if the message is sent successfully.
   */
  send: (message: Message<T>) => Promise<boolean>;

  /**
   * Send a message and subscribe to messages related to the same offer.
   * @param message - The message to send after subscribing.
   * @returns A promise that resolves to true if both subscribe and send operations are successful.
   */
  subscribeSend: (message: Message<T>) => Promise<boolean>;

  /**
   * Send a message and unsubscribe from messages related to the same offer.
   * @param message - The message to send after unsubscribing.
   * @returns A promise that resolves to true if both unsubscribe and send operations are successful.
   */
  unsubscribeSend: (message: Message<T>) => Promise<boolean>;
};

/**
 * Represents a message in the scheme.
 * @template T - A discriminated union representing all possible messages.
 */
export type Message<T extends ADT> = {
  pubkey: `0x${string}`;
  offerId: string;
  initial?: boolean;
  data: T;
};

/**
 * Abstract base class for implementing a SchemeClient.
 * Provides a foundation for concrete implementations of the SchemeClient interface.
 * @template T - A discriminated union representing all possible messages.
 * @template R - A string literal union of roles.
 */
export abstract class AbstractSchemeClient<T extends ADT, R extends string>
  implements SchemeClient<T>
{
  /**
   * @param scheme - The scheme being implemented.
   * @param role - The role of a client instance in the scheme.
   */
  constructor(protected readonly scheme: Scheme<T, R>, protected role: R) {}

  abstract start(init?: Message<T>): Promise<boolean>;
  abstract subscribe(offerId?: string): Promise<boolean>;
  abstract unsubscribe(offerId?: string): Promise<boolean>;
  abstract send(message: Message<T>): Promise<boolean>;

  subscribeSend = async (message: Message<T>): Promise<boolean> =>
    (await this.subscribe(message.offerId)) && (await this.send(message));
  unsubscribeSend = async (message: Message<T>): Promise<boolean> =>
    (await this.unsubscribe(message.offerId)) && (await this.send(message));
}
