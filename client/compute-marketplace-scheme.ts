import { type Scheme } from "./scheme";
import { match, P } from "ts-pattern";

type Roles = "buyer" | "seller";
type Messages =
  | ({ _tag: "offer" } & Offer)
  | { _tag: "cancel"; error?: string }
  | ({ _tag: "buyAttest"; attestation: Hex } & Offer)
  | { _tag: "sellAttest"; attestation: Hex; result: string };

type Offer = { query: string; price: [Hex, number] };
type Hex = `0x${string}`;


export const dcnScheme: Scheme<Messages, Roles> = {
  onAgent: async (client, role, input, output) =>
    // output is responding to input
    input.offerId == output.offerId &&
    match({ role, input, output })
      // anyone can cancel a negotiation at any time
      .with(
        { output: { data: { _tag: "cancel" } } },
        async ({ output }) => await client.unsubscribeSend(output)
      )
      // seller can respond to buyer's attestation (payment)
      // with their own attestation (result)
      .with(
        {
          role: "seller",
          input: { data: { _tag: "buyAttest" } },
          output: { data: { _tag: "sellAttest" } },
        },
        async ({ output }) => await client.unsubscribeSend(output)
      )
      // seller can respond to initial offers with a counteroffer
      .with(
        {
          role: "seller",
          input: { initial: true, data: { _tag: "offer" } },
          output: { data: { _tag: "offer" } },
        },
        async ({ output }) => await client.subscribeSend(output)
      )
      // anyone can respond to a non-initial offer with a counteroffer
      .with(
        {
          input: { data: { _tag: "offer" } },
          output: { data: { _tag: "offer" } },
        },
        async ({ output }) => await client.send(output)
      )
      // buyer can respond to counteroffers with payment
      .with(
        {
          role: "buyer",
          input: { data: { _tag: "offer" } },
          output: { data: { _tag: "buyAttest" } },
        },
        async ({ output }) => await client.send(output)
      )
      // the above rules are exhaustive
      .otherwise(() => false),
  onStart: async (client, role, init) =>
    match({ role, init })
      // buyers must join with an initial offer
      .with(
        { role: "buyer", init: { data: { _tag: "offer" } } },
        async ({ init }) =>
          // default to 0 if no price is given; token must still be given
          await client.subscribeSend({
            ...init,
            initial: true,
            data: {
              ...init.data,
              price: [init.data.price[0], init.data.price[1] || 0],
            },
          })
      )
      // sellers must join without an initial offer
      .with(
        { role: "seller", init: undefined },
        async () => await client.subscribe()
      )
      .otherwise(() => false),
};
