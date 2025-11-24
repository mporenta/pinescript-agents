# Streaming Thinking

You can stream extended thinking responses using [server-sent events (SSE)](https://developer.mozilla.org/en-US/Web/API/Server-sent%5Fevents/Using%5Fserver-sent%5Fevents).

When streaming is enabled for extended thinking, you receive thinking content via `thinking_delta` events.

For more documention on streaming via the Messages API, see [Streaming Messages](/docs/en/build-with-claude/streaming).

## How to handle streaming with thinking

### Shell Example

```bash
curl https://api.anthropic.com/v1/messages \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "model": "claude-sonnet-4-5",
    "max_tokens": 16000,
    "stream": true,
    "thinking": {
        "type": "enabled",
        "budget_tokens": 10000
    },
    "messages": [
        {
            "role": "user",
            "content": "What is 27 * 453?"
        }
    ]
}'
```

### Python Example

```python
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "What is 27 * 453?"}],
) as stream:
    thinking_started = False
    response_started = False

    for event in stream:
        if event.type == "content_block_start":
            print(f"\nStarting {event.content_block.type} block...")
            # Reset flags for each new block
            thinking_started = False
            response_started = False
        elif event.type == "content_block_delta":
            if event.delta.type == "thinking_delta":
                if not thinking_started:
                    print("Thinking: ", end="", flush=True)
                    thinking_started = True
                print(event.delta.thinking, end="", flush=True)
            elif event.delta.type == "text_delta":
                if not response_started:
                    print("Response: ", end="", flush=True)
                    response_started = True
                print(event.delta.text, end="", flush=True)
        elif event.type == "content_block_stop":
            print("\nBlock complete.")
```

### TypeScript Example

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

const stream = await client.messages.stream({
  model: "claude-sonnet-4-5",
  max_tokens: 16000,
  thinking: {
    type: "enabled",
    budget_tokens: 10000
  },
  messages: [{
    role: "user",
    content: "What is 27 * 453?"
  }]
});

let thinkingStarted = false;
let responseStarted = false;

for await (const event of stream) {
  if (event.type === 'content_block_start') {
    console.log(`\nStarting ${event.content_block.type} block...`);
    // Reset flags for each new block
    thinkingStarted = false;
    responseStarted = false;
  } else if (event.type === 'content_block_delta') {
    if (event.delta.type === 'thinking_delta') {
      if (!thinkingStarted) {
        process.stdout.write('Thinking: ');
        thinkingStarted = true;
      }
      process.stdout.write(event.delta.thinking);
    } else if (event.delta.type === 'text_delta') {
      if (!responseStarted) {
        process.stdout.write('Response: ');
        responseStarted = true;
      }
      process.stdout.write(event.delta.text);
    }
  } else if (event.type === 'content_block_stop') {
    console.log('\nBlock complete.');
  }
}
```

## Example Streaming Output

```json
event: message_start
data: {"type": "message_start", "message": {"id": "msg_01...", "type": "message", "role": "assistant", "content": [], "model": "claude-sonnet-4-5", "stop_reason": null, "stop_sequence": null}}

event: content_block_start
data: {"type": "content_block_start", "index": 0, "content_block": {"type": "thinking", "thinking": ""}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "Let me solve this step by step:\n\n1. First break down 27 * 453"}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "\n2. 453 = 400 + 50 + 3"}}

// Additional thinking deltas...

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "signature_delta", "signature": "EqQBCgIYAhIM1gbcDa9GJwZA2b3hGgxBdjrkzLoky3dl1pkiMOYds..."}}

event: content_block_stop
data: {"type": "content_block_stop", "index": 0}

event: content_block_start
data: {"type": "content_block_start", "index": 1, "content_block": {"type": "text", "text": ""}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": "27 * 453 = 12,231"}}

// Additional text deltas...

event: content_block_stop
data: {"type": "content_block_stop", "index": 1}

event: message_delta
data: {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": null}}

event: message_stop
data: {"type": "message_stop"}
```

<Note>
When using streaming with thinking enabled, you might notice that text sometimes arrives in larger chunks alternating with smaller, token-by-token delivery. This is expected behavior, especially for thinking content.

The streaming system needs to process content in batches for optimal performance, which can result in this "chunky" delivery pattern, with possible delays between streaming events. We're continuously working to improve this experience, with future updates focused on making thinking content stream more smoothly.
</Note>
