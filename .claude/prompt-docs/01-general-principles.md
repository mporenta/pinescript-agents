# Prompting Best Practices: General Principles

This guide provides specific prompt engineering techniques for Claude 4.x models, with specific guidance for Sonnet 4.5 and Haiku 4.5. These models have been trained for more precise instruction following than previous generations of Claude models.

## Be explicit with your instructions

Claude 4.x models respond well to clear, explicit instructions. Being specific about your desired output can help enhance results. Customers who desire the "above and beyond" behavior from previous Claude models might need to more explicitly request these behaviors with newer models.

<section title="Example: Creating an analytics dashboard">

**Less effective:**
```text
Create an analytics dashboard
```

**More effective:**
```text
Create an analytics dashboard. Include as many relevant features and interactions as possible. Go beyond the basics to create a fully-featured implementation.
```

</section>

## Add context to improve performance

Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude 4.x models better understand your goals and deliver more targeted responses.

<section title="Example: Formatting preferences">

**Less effective:**
```text
NEVER use ellipses
```

**More effective:**
```text
Your response will be read aloud by a text-to-speech engine, so never use ellipses since the text-to-speech engine will not know how to pronounce them.
```

</section>

Claude is smart enough to generalize from the explanation.

## Be vigilant with examples & details

Claude 4.x models pay close attention to details and examples as part of their precise instruction following capabilities. Ensure that your examples align with the behaviors you want to encourage and minimize behaviors you want to avoid.

## Long-horizon reasoning and state tracking

Claude 4.5 models excel at long-horizon reasoning tasks with exceptional state tracking capabilities. It maintains orientation across extended sessions by focusing on incremental progress—making steady advances on a few things at a time rather than attempting everything at once. This capability especially emerges over multiple context windows or task iterations, where Claude can work on a complex task, save the state, and continue with a fresh context window.

### Context awareness and multi-window workflows

Claude 4.5 models feature [context awareness](/docs/en/build-with-claude/context-windows#context-awareness-in-claude-sonnet-4-5), enabling the model to track its remaining context window (i.e. "token budget") throughout a conversation. This enables Claude to execute tasks and manage context more effectively by understanding how much space it has to work.

**Managing context limits:**

If you are using Claude in an agent harness that compacts context or allows saving context to external files (like in Claude Code), we suggest adding this information to your prompt so Claude can behave accordingly. Otherwise, Claude may sometimes naturally try to wrap up work as it approaches the context limit. Below is an example prompt:

```text Sample prompt
Your context window will be automatically compacted as it approaches its limit, allowing you to continue working indefinitely from where you left off. Therefore, do not stop tasks early due to token budget concerns. As you approach your token budget limit, save your current progress and state to memory before the context window refreshes. Always be as persistent and autonomous as possible and complete tasks fully, even if the end of your budget is approaching. Never artificially stop any task early regardless of the context remaining.
```

The [memory tool](/docs/en/agents-and-tools/tool-use/memory-tool) pairs naturally with context awareness for seamless context transitions.

### Multi-context window workflows

For tasks spanning multiple context windows:

1. **Use a different prompt for the very first context window**: Use the first context window to set up a framework (write tests, create setup scripts), then use future context windows to iterate on a todo-list.

2. **Have the model write tests in a structured format**: Ask Claude to create tests before starting work and keep track of them in a structured format (e.g., `tests.json`). This leads to better long-term ability to iterate. Remind Claude of the importance of tests: "It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality."

3. **Set up quality of life tools**: Encourage Claude to create setup scripts (e.g., `init.sh`) to gracefully start servers, run test suites, and linters. This prevents repeated work when continuing from a fresh context window.

4. **Starting fresh vs compacting**: When a context window is cleared, consider starting with a brand new context window rather than using compaction. Claude 4.5 models are extremely effective at discovering state from the local filesystem. In some cases, you may want to take advantage of this over compaction. Be prescriptive about how it should start:
   - "Call pwd; you can only read and write files in this directory."
   - "Review progress.txt, tests.json, and the git logs."
   - "Manually run through a fundamental integration test before moving on to implementing new features."

5. **Provide verification tools**: As the length of autonomous tasks grows, Claude needs to verify correctness without continuous human feedback. Tools like Playwright MCP server or computer use capabilities for testing UIs are helpful.

6. **Encourage complete usage of context**: Prompt Claude to efficiently complete components before moving on:

```text Sample prompt
This is a very long task, so it may be beneficial to plan out your work clearly. It's encouraged to spend your entire output context working on the task - just make sure you don't run out of context with significant uncommitted work. Continue working systematically until you have completed this task.
```

### State management best practices

- **Use structured formats for state data**: When tracking structured information (like test results or task status), use JSON or other structured formats to help Claude understand schema requirements
- **Use unstructured text for progress notes**: Freeform progress notes work well for tracking general progress and context
- **Use git for state tracking**: Git provides a log of what's been done and checkpoints that can be restored. Claude 4.5 models perform especially well in using git to track state across multiple sessions.
- **Emphasize incremental progress**: Explicitly ask Claude to keep track of its progress and focus on incremental work

<section title="Example: State tracking">

```json
// Structured state file (tests.json)
{
  "tests": [
    {"id": 1, "name": "authentication_flow", "status": "passing"},
    {"id": 2, "name": "user_management", "status": "failing"},
    {"id": 3, "name": "api_endpoints", "status": "not_started"}
  ],
  "total": 200,
  "passing": 150,
  "failing": 25,
  "not_started": 25
}
```

```text
// Progress notes (progress.txt)
Session 3 progress:
- Fixed authentication token validation
- Updated user model to handle edge cases
- Next: investigate user_management test failures (test #2)
- Note: Do not remove tests as this could lead to missing functionality
```

</section>

## Communication style

Claude 4.5 models have a more concise and natural communication style compared to previous models:

- **More direct and grounded**: Provides fact-based progress reports rather than self-celebratory updates
- **More conversational**: Slightly more fluent and colloquial, less machine-like
- **Less verbose**: May skip detailed summaries for efficiency unless prompted otherwise

This communication style accurately reflects what has been accomplished without unnecessary elaboration.
