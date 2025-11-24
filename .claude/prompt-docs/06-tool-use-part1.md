# Extended Thinking with Tool Use - Part 1

Extended thinking can be used alongside [tool use](/docs/en/agents-and-tools/tool-use/overview), allowing Claude to reason through tool selection and results processing.

## Limitations

When using extended thinking with tool use, be aware of the following limitations:

1. **Tool choice limitation**: Tool use with thinking only supports `tool_choice: {"type": "auto"}` (the default) or `tool_choice: {"type": "none"}`. Using `tool_choice: {"type": "any"}` or `tool_choice: {"type": "tool", "name": "..."}` will result in an error because these options force tool use, which is incompatible with extended thinking.

2. **Preserving thinking blocks**: During tool use, you must pass `thinking` blocks back to the API for the last assistant message. Include the complete unmodified block back to the API to maintain reasoning continuity.

## Toggling thinking modes in conversations

You cannot toggle thinking in the middle of an assistant turn, including during tool use loops. The entire assistant turn must operate in a single thinking mode:

- **If thinking is enabled**, the final assistant turn must start with a thinking block.
- **If thinking is disabled**, the final assistant turn must not contain any thinking blocks

From the model's perspective, **tool use loops are part of the assistant turn**. An assistant turn doesn't complete until Claude finishes its full response, which may include multiple tool calls and results.

For example, this sequence is all part of a **single assistant turn**:
```
User: "What's the weather in Paris?"
Assistant: [thinking] + [tool_use: get_weather]
User: [tool_result: "20°C, sunny"]
Assistant: [text: "The weather in Paris is 20°C and sunny"]
```

Even though there are multiple API messages, the tool use loop is conceptually part of one continuous assistant response.

### Common error scenarios

You might encounter this error:
```
Expected `thinking` or `redacted_thinking`, but found `tool_use`.
When `thinking` is enabled, a final `assistant` message must start
with a thinking block (preceding the lastmost set of `tool_use` and
`tool_result` blocks).
```

This typically occurs when:
1. You had thinking **disabled** during a tool use sequence
2. You want to enable thinking again
3. Your last assistant message contains tool use blocks but no thinking block

### Practical guidance

**✗ Invalid: Toggling thinking immediately after tool use**
```
User: "What's the weather?"
Assistant: [tool_use] (thinking disabled)
User: [tool_result]
// Cannot enable thinking here - still in the same assistant turn
```

**✓ Valid: Complete the assistant turn first**
```
User: "What's the weather?"
Assistant: [tool_use] (thinking disabled)
User: [tool_result]
Assistant: [text: "It's sunny"]
User: "What about tomorrow?" (thinking disabled)
Assistant: [thinking] + [text: "..."] (thinking enabled - new turn)
```

**Best practice**: Plan your thinking strategy at the start of each turn rather than trying to toggle mid-turn.

<Note>
Toggling thinking modes also invalidates prompt caching for message history. For more details, see the Extended Thinking with Prompt Caching section.
</Note>

## Example: Passing thinking blocks with tool results

Here's a practical example showing how to preserve thinking blocks when providing tool results:

### Python Example

```python
weather_tool = {
    "name": "get_weather",
    "description": "Get current weather for a location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
}

# First request - Claude responds with thinking and tool request
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    tools=[weather_tool],
    messages=[
        {"role": "user", "content": "What's the weather in Paris?"}
    ]
)
```

### TypeScript Example

```typescript
const weatherTool = {
  name: "get_weather",
  description: "Get current weather for a location",
  input_schema: {
    type: "object",
    properties: {
      location: { type: "string" }
    },
    required: ["location"]
  }
};

// First request - Claude responds with thinking and tool request
const response = await client.messages.create({
  model: "claude-sonnet-4-5",
  max_tokens: 16000,
  thinking: {
    type: "enabled",
    budget_tokens: 10000
  },
  tools: [weatherTool],
  messages: [
    { role: "user", content: "What's the weather in Paris?" }
  ]
});
```

### API Response Example

The API response will include thinking, text, and tool_use blocks:

```json
{
    "content": [
        {
            "type": "thinking",
            "thinking": "The user wants to know the current weather in Paris. I have access to a function `get_weather`...",
            "signature": "BDaL4VrbR2Oj0hO4XpJxT28J5TILnCrrUXoKiiNBZW9P+nr8XSj1zuZzAl4egiCCpQNvfyUuFFJP5CncdYZEQPPmLxYsNrcs...."
        },
        {
            "type": "text",
            "text": "I can help you get the current weather information for Paris. Let me check that for you"
        },
        {
            "type": "tool_use",
            "id": "toolu_01CswdEQBMshySk6Y9DFKrfq",
            "name": "get_weather",
            "input": {
                "location": "Paris"
            }
        }
    ]
}
```
