// Imports
import { createClient } from "redis";
import { RedisSchemeClient } from "./client";
import { dcnScheme } from "./compute-marketplace-scheme";

// Command Line Arguments
// return the command-line arguments excluding the first two elements
const [role, agent, init, redis_url] = process.argv.slice(2);

// Create new instance of RedisSchemeClient
const client = new RedisSchemeClient(
  dcnScheme,
  role,
  agent,
  createClient({ url: redis_url }),
  createClient({ url: redis_url })
);

// Start the client with optional arguments
await client.start(init ? JSON.parse(init) : undefined);
