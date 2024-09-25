# redis-scheme-client

This project was created using `bun init` in bun v1.1.8. [Bun](https://bun.sh) is a fast all-in-one JavaScript runtime.

To install dependencies:

```bash
bun install
```

To install redis:

https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/

To run client:

Syntax: `bun run runner.ts [role] [agent] [initial offer (buyer only)]`

```bash
bun run runner.ts seller ./example-agent.ts ""  redis://default:***@***.upstash.io:6379
```

```bash
bun run runner.ts buyer ./example-agent.ts '{"pubkey": "0x123","offerId": "offer_0","initial": true,"data": {"_tag": "offer","query": "hello","price": ["0x100", 200]}}' redis://default:***@***.upstash.io:6379
```

To run server:

```bash
redis-server
```
