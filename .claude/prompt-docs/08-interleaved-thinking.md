# Interleaved Thinking

Extended thinking with tool use in Claude 4 models supports interleaved thinking, which enables Claude to think between tool calls and make more sophisticated reasoning after receiving tool results.

With interleaved thinking, Claude can:
- Reason about the results of a tool call before deciding what to do next
- Chain multiple tool calls with reasoning steps in between
- Make more nuanced decisions based on intermediate results

To enable interleaved thinking, add [the beta header](/docs/en/api/beta-headers) `interleaved-thinking-2025-05-14` to your API request.

## Important Considerations

- With interleaved thinking, the `budget_tokens` can exceed the `max_tokens` parameter, as it represents the total budget across all thinking blocks within one assistant turn.
- Interleaved thinking is only supported for [tools used via the Messages API](/docs/en/agents-and-tools/tool-use/overview).
- Interleaved thinking is supported for Claude 4 models only, with the beta header `interleaved-thinking-2025-05-14`.
- Direct calls to the Claude API allow you to pass `interleaved-thinking-2025-05-14` in requests to any model, with no effect.
- On 3rd-party platforms (e.g., [Amazon Bedrock](/docs/en/build-with-claude/claude-on-amazon-bedrock) and [Vertex AI](/docs/en/build-with-claude/claude-on-vertex-ai)), if you pass `interleaved-thinking-2025-05-14` to any model aside from Claude Opus 4.1, Opus 4, or Sonnet 4, your request will fail.

## Tool Use Without Interleaved Thinking

### Python Example

```python
import anthropic

client = anthropic.Anthropic()

# Define tools
calculator_tool = {
    "name": "calculator",
    "description": "Perform mathematical calculations",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate"
            }
        },
        "required": ["expression"]
    }
}

database_tool = {
    "name": "database_query",
    "description": "Query product database",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query to execute"
            }
        },
        "required": ["query"]
    }
}

# First request - Claude thinks once before all tool calls
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    tools=[calculator_tool, database_tool],
    messages=[{
        "role": "user",
        "content": "What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?"
    }]
)

# Response includes thinking followed by tool uses
# Note: Claude thinks once at the beginning, then makes all tool decisions
print("First response:")
for block in response.content:
    if block.type == "thinking":
        print(f"Thinking (summarized): {block.thinking}")
    elif block.type == "tool_use":
        print(f"Tool use: {block.name} with input {block.input}")
    elif block.type == "text":
        print(f"Text: {block.text}")

# You would execute the tools and return results...
# After getting both tool results back, Claude directly responds without additional thinking
```

### TypeScript Example

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

// Define tools
const calculatorTool = {
  name: "calculator",
  description: "Perform mathematical calculations",
  input_schema: {
    type: "object",
    properties: {
      expression: {
        type: "string",
        description: "Mathematical expression to evaluate"
      }
    },
    required: ["expression"]
  }
};

const databaseTool = {
  name: "database_query",
  description: "Query product database",
  input_schema: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "SQL query to execute"
      }
    },
    required: ["query"]
  }
};

// First request - Claude thinks once before all tool calls
const response = await client.messages.create({
  model: "claude-sonnet-4-5",
  max_tokens: 16000,
  thinking: {
    type: "enabled",
    budget_tokens: 10000
  },
  tools: [calculatorTool, databaseTool],
  messages: [{
    role: "user",
    content: "What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?"
  }]
});

// Response includes thinking followed by tool uses
// Note: Claude thinks once at the beginning, then makes all tool decisions
console.log("First response:");
for (const block of response.content) {
  if (block.type === "thinking") {
    console.log(`Thinking (summarized): ${block.thinking}`);
  } else if (block.type === "tool_use") {
    console.log(`Tool use: ${block.name} with input ${JSON.stringify(block.input)}`);
  } else if (block.type === "text") {
    console.log(`Text: ${block.text}`);
  }
}

// You would execute the tools and return results...
// After getting both tool results back, Claude directly responds without additional thinking
```

## Tool Use With Interleaved Thinking

With the `interleaved-thinking-2025-05-14` beta header, Claude can think after receiving tool results, allowing for more sophisticated multi-step reasoning. This enables Claude to:

- Reflect on tool results before deciding on the next action
- Chain multiple tool calls with reasoning between each step
- Make more nuanced decisions based on intermediate results
- Adapt its strategy based on what it learns from previous tool calls

This pattern is especially useful for complex tasks that require iterative exploration or decision-making based on intermediate results.
