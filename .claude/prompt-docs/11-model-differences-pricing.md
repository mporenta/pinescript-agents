# Model Differences, Pricing, and Best Practices

## Differences in thinking across model versions

The Messages API handles thinking differently across Claude Sonnet 3.7 and Claude 4 models, primarily in redaction and summarization behavior.

See the table below for a condensed comparison:

| Feature | Claude Sonnet 3.7 | Claude 4 Models |
|---------|------------------|----------------|
| **Thinking Output** | Returns full thinking output | Returns summarized thinking |
| **Interleaved Thinking** | Not supported | Supported with `interleaved-thinking-2025-05-14` beta header |

## Pricing

Extended thinking uses the standard token pricing scheme:

| Model             | Base Input Tokens | Cache Writes  | Cache Hits    | Output Tokens |
|-------------------|-------------------|---------------|---------------|---------------|
| Claude Opus 4.1     | $15 / MTok        | $18.75 / MTok | $1.50 / MTok  | $75 / MTok    |
| Claude Opus 4     | $15 / MTok        | $18.75 / MTok | $1.50 / MTok  | $75 / MTok    |
| Claude Sonnet 4.5   | $3 / MTok         | $3.75 / MTok  | $0.30 / MTok  | $15 / MTok    |
| Claude Sonnet 4   | $3 / MTok         | $3.75 / MTok  | $0.30 / MTok  | $15 / MTok    |
| Claude Sonnet 3.7 | $3 / MTok         | $3.75 / MTok  | $0.30 / MTok  | $15 / MTok    |

The thinking process incurs charges for:
- Tokens used during thinking (output tokens)
- Thinking blocks from the last assistant turn included in subsequent requests (input tokens)
- Standard text output tokens

<Note>
When extended thinking is enabled, a specialized system prompt is automatically included to support this feature.
</Note>

When using summarized thinking:
- **Input tokens**: Tokens in your original request (excludes thinking tokens from previous turns)
- **Output tokens (billed)**: The original thinking tokens that Claude generated internally
- **Output tokens (visible)**: The summarized thinking tokens you see in the response
- **No charge**: Tokens used to generate the summary

<Warning>
The billed output token count will **not** match the visible token count in the response. You are billed for the full thinking process, not the summary you see.
</Warning>

## Best practices and considerations for extended thinking

### Working with thinking budgets

- **Budget optimization:** The minimum budget is 1,024 tokens. We suggest starting at the minimum and increasing the thinking budget incrementally to find the optimal range for your use case. Higher token counts enable more comprehensive reasoning but with diminishing returns depending on the task. Increasing the budget can improve response quality at the tradeoff of increased latency. For critical tasks, test different settings to find the optimal balance. Note that the thinking budget is a target rather than a strict limit—actual token usage may vary based on the task.
- **Starting points:** Start with larger thinking budgets (16k+ tokens) for complex tasks and adjust based on your needs.
- **Large budgets:** For thinking budgets above 32k, we recommend using [batch processing](/docs/en/build-with-claude/batch-processing) to avoid networking issues. Requests pushing the model to think above 32k tokens causes long running requests that might run up against system timeouts and open connection limits.
- **Token usage tracking:** Monitor thinking token usage to optimize costs and performance.

### Performance considerations

- **Response times:** Be prepared for potentially longer response times due to the additional processing required for the reasoning process. Factor in that generating thinking blocks may increase overall response time.
- **Streaming requirements:** Streaming is required when `max_tokens` is greater than 21,333. When streaming, be prepared to handle both thinking and text content blocks as they arrive.

### Feature compatibility

- Thinking isn't compatible with `temperature` or `top_k` modifications as well as [forced tool use](/docs/en/agents-and-tools/tool-use/implement-tool-use#forcing-tool-use).
- When thinking is enabled, you can set `top_p` to values between 1 and 0.95.
- You cannot pre-fill responses when thinking is enabled.
- Changes to the thinking budget invalidate cached prompt prefixes that include messages. However, cached system prompts and tool definitions will continue to work when thinking parameters change.

### Usage guidelines

- **Task selection:** Use extended thinking for particularly complex tasks that benefit from step-by-step reasoning like math, coding, and analysis.
- **Context handling:** You do not need to remove previous thinking blocks yourself. The Claude API automatically ignores thinking blocks from previous turns and they are not included when calculating context usage.
- **Prompt engineering:** Review our [extended thinking prompting tips](/docs/en/build-with-claude/prompt-engineering/extended-thinking-tips) if you want to maximize Claude's thinking capabilities.
