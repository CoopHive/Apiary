import { createClient } from "redis";
import type { ADT, Scheme, Message } from "./scheme";
import { AbstractSchemeClient } from "./scheme";

/**
 * A Redis-based implementation of AbstractSchemeClient.
 *
 * @template T - Type of Abstract Data Type (ADT).
 * @template R - Type of role.
 */
export class RedisSchemeClient<
  T extends ADT,
  R extends string
> extends AbstractSchemeClient<T, R> {
  /**
   * Constructs a RedisSchemeClient instance.
   *
   * @param scheme - The scheme to use.
   * @param role - The role of the client.
   * @param agent - The agent to handle messages.
   * @param redis - The Redis client for general operations (default is a new client).
   * @param redisPubSub - The Redis client for pub/sub operations (default is a new client).
   * @param defaultChannel - The default channel name (default is "initial_offers").
   */
  constructor(
    scheme: Scheme<T, R>,
    role: R,
    private agent: string,
    private redis = createClient(),
    private redisPubSub = createClient(),
    private defaultChannel = "initial_offers"
  ) {
    super(scheme, role);

    this.onMessage = this.onMessage.bind(this);
  }

  /**
   * Starts the RedisSchemeClient, connecting to Redis and initializing the scheme.
   *
   * @param init - Optional initialization message.
   * @returns True if the start was successful.
   * @throws Error if the start fails.
   */
  async start(init?: Message<T>) {

    await this.redisPubSub.connect();
    await this.redis.connect();
    if (!(await this.scheme.onStart(this, this.role, init))) {
      throw new Error("Failed to start");
    }
    return true;
  }

  /**
   * Subscribes to a specific offer or the default channel.
   *
   * @param offerId - Optional offer ID to subscribe to.
   * @returns True if subscription was successful.
   */
  async subscribe(offerId?: string) {
    if (!offerId) {
      await this.redisPubSub.subscribe(this.defaultChannel, this.onMessage);
      return true;
    }
    await this.redisPubSub.subscribe(offerId, this.onMessage);
    return true;
  }

  /**
   * Unsubscribes from a specific offer or the default channel.
   *
   * @param offerId - Optional offer ID to unsubscribe from.
   * @returns True if unsubscription was successful.
   */
  async unsubscribe(offerId?: string) {
    if (!offerId) {
      await this.redisPubSub.unsubscribe(this.defaultChannel);
      return true;
    }
    await this.redisPubSub.unsubscribe(offerId);
    return true;
  }

  /**
   * Sends a message to Redis.
   *
   * @param message - The message to send.
   * @returns True if the message was sent successfully.
   */
  async send(message: Message<T>) {
    await this.redis.publish(
      message.initial ? this.defaultChannel : message.offerId,
      JSON.stringify(message)
    );
    return true;
  }

  /**
   * Handles incoming messages, filters them, and processes with the agent.
   *
   * @param message - The message received.
   * @param topic - The topic from which the message was received.
   */
  private async onMessage(message: string, topic: string) {
    const message_: Message<T> = JSON.parse(message);

    // spam filter
    if (
      topic != message_.offerId &&
      !(topic == this.defaultChannel && message_.initial)
    )
      return;
    console.log("message to agent: ", message_);

    const response = await fetch(this.agent, {
      method: "POST",
      body: JSON.stringify(message_),
    });
    const response_: Message<T> | "noop" = await response.json();
    
    if (response_ === "noop") return;
    if (!(await this.scheme.onAgent(this, this.role, message_, response_))) {

      // Log variables for debugging
      console.log("Role:", this.role);
      console.log("Message:", message_);
      console.log("Response:", response_);

      console.error("Invalid agent response");
    }
  }
}
