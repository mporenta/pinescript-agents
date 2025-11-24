# Prompting best practices

---

This guide provides specific prompt engineering techniques for Claude 4.x models, with specific guidance for Sonnet 4.5 and Haiku 4.5. These models have been trained for more precise instruction following than previous generations of Claude models.

## General principles

### Be explicit with your instructions

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

### Add context to improve performance

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

### Be vigilant with examples & details

Claude 4.x models pay close attention to details and examples as part of their precise instruction following capabilities. Ensure that your examples align with the behaviors you want to encourage and minimize behaviors you want to avoid.

### Long-horizon reasoning and state tracking

Claude 4.5 models excel at long-horizon reasoning tasks with exceptional state tracking capabilities. It maintains orientation across extended sessions by focusing on incremental progress—making steady advances on a few things at a time rather than attempting everything at once. This capability especially emerges over multiple context windows or task iterations, where Claude can work on a complex task, save the state, and continue with a fresh context window.

#### Context awareness and multi-window workflows

Claude 4.5 models feature [context awareness](/docs/en/build-with-claude/context-windows#context-awareness-in-claude-sonnet-4-5), enabling the model to track its remaining context window (i.e. "token budget") throughout a conversation. This enables Claude to execute tasks and manage context more effectively by understanding how much space it has to work.

**Managing context limits:**

If you are using Claude in an agent harness that compacts context or allows saving context to external files (like in Claude Code), we suggest adding this information to your prompt so Claude can behave accordingly. Otherwise, Claude may sometimes naturally try to wrap up work as it approaches the context limit. Below is an example prompt:

```text Sample prompt
Your context window will be automatically compacted as it approaches its limit, allowing you to continue working indefinitely from where you left off. Therefore, do not stop tasks early due to token budget concerns. As you approach your token budget limit, save your current progress and state to memory before the context window refreshes. Always be as persistent and autonomous as possible and complete tasks fully, even if the end of your budget is approaching. Never artificially stop any task early regardless of the context remaining.
```

The [memory tool](/docs/en/agents-and-tools/tool-use/memory-tool) pairs naturally with context awareness for seamless context transitions.

#### Multi-context window workflows

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

#### State management best practices

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

### Communication style

Claude 4.5 models have a more concise and natural communication style compared to previous models:

- **More direct and grounded**: Provides fact-based progress reports rather than self-celebratory updates
- **More conversational**: Slightly more fluent and colloquial, less machine-like
- **Less verbose**: May skip detailed summaries for efficiency unless prompted otherwise

This communication style accurately reflects what has been accomplished without unnecessary elaboration.

## Guidance for specific situations

### Balance verbosity

Claude 4.5 models tend toward efficiency and may skip verbal summaries after tool calls, jumping directly to the next action. While this creates a streamlined workflow, you may prefer more visibility into its reasoning process.

If you want Claude to provide updates as it works:

```text Sample prompt
After completing a task that involves tool use, provide a quick summary of the work you've done.
```

### Tool usage patterns

Claude 4.5 models are trained for precise instruction following and benefits from explicit direction to use specific tools. If you say "can you suggest some changes," it will sometimes provide suggestions rather than implementing them—even if making changes might be what you intended.

For Claude to take action, be more explicit:

<section title="Example: Explicit instructions">

**Less effective (Claude will only suggest):**
```text
Can you suggest some changes to improve this function?
```

**More effective (Claude will make the changes):**
```text
Change this function to improve its performance.
```

Or:
```text
Make these edits to the authentication flow.
```

</section>

To make Claude more proactive about taking action by default, you can add this to your system prompt:

```text Sample prompt for proactive action
<default_to_action>
By default, implement changes rather than only suggesting them. If the user's intent is unclear, infer the most useful likely action and proceed, using tools to discover any missing details instead of guessing. Try to infer the user's intent about whether a tool call (e.g., file edit or read) is intended or not, and act accordingly.
</default_to_action>
```

On the other hand, if you want the model to be more hesitant by default, less prone to jumping straight into implementations, and only take action if requested, you can steer this behavior with a prompt like the below:

```text Sample prompt for conservative action
<do_not_act_before_instructions>
Do not jump into implementatation or changes files unless clearly instructed to make changes. When the user's intent is ambiguous, default to providing information, doing research, and providing recommendations rather than taking action. Only proceed with edits, modifications, or implementations when the user explicitly requests them.
</do_not_act_before_instructions>
```

### Control the format of responses

There are a few ways that we have found to be particularly effective in steering output formatting in Claude 4.x models:

1. **Tell Claude what to do instead of what not to do**

   - Instead of: "Do not use markdown in your response"
   - Try: "Your response should be composed of smoothly flowing prose paragraphs."

2. **Use XML format indicators**

   - Try: "Write the prose sections of your response in \<smoothly_flowing_prose_paragraphs\> tags."

3. **Match your prompt style to the desired output**

   The formatting style used in your prompt may influence Claude's response style. If you are still experiencing steerability issues with output formatting, we recommend as best as you can matching your prompt style to your desired output style. For example, removing markdown from your prompt can reduce the volume of markdown in the output.

4. **Use detailed prompts for specific formatting preferences**

   For more control over markdown and formatting usage, provide explicit guidance:

```text Sample prompt to minimize markdown
<avoid_excessive_markdown_and_bullet_points>
When writing reports, documents, technical explanations, analyses, or any long-form content, write in clear, flowing prose using complete paragraphs and sentences. Use standard paragraph breaks for organization and reserve markdown primarily for `inline code`, code blocks (```...```), and simple headings (###, and ###). Avoid using **bold** and *italics*.

DO NOT use ordered lists (1. ...) or unordered lists (*) unless : a) you're presenting truly discrete items where a list format is the best option, or b) the user explicitly requests a list or ranking

Instead of listing items with bullets or numbers, incorporate them naturally into sentences. This guidance applies especially to technical writing. Using prose instead of excessive formatting will improve user satisfaction. NEVER output a series of overly short bullet points.

Your goal is readable, flowing text that guides the reader naturally through ideas rather than fragmenting information into isolated points.
</avoid_excessive_markdown_and_bullet_points>
```

### Research and information gathering

Claude 4.5 models demonstrate exceptional agentic search capabilities and can find and synthesize information from multiple sources effectively. For optimal research results:

1. **Provide clear success criteria**: Define what constitutes a successful answer to your research question

2. **Encourage source verification**: Ask Claude to verify information across multiple sources

3. **For complex research tasks, use a structured approach**:

```text Sample prompt for complex research
Search for this information in a structured way. As you gather data, develop several competing hypotheses. Track your confidence levels in your progress notes to improve calibration. Regularly self-critique your approach and plan. Update a hypothesis tree or research notes file to persist information and provide transparency. Break down this complex research task systematically.
```

This structured approach allows Claude to find and synthesize virtually any piece of information and iteratively critique its findings, no matter the size of the corpus.

### Subagent orchestration

Claude 4.5 models demonstrate significantly improved native subagent orchestration capabilities. These models can recognize when tasks would benefit from delegating work to specialized subagents and do so proactively without requiring explicit instruction.

To take advantage of this behavior:

1. **Ensure well-defined subagent tools**: Have subagent tools available and described in tool definitions
2. **Let Claude orchestrate naturally**: Claude will delegate appropriately without explicit instruction
3. **Adjust conservativeness if needed**:

```text Sample prompt for conservative subagent usage
Only delegate to subagents when the task clearly benefits from a separate agent with a new context window.
```

### Model self-knowledge

If you would like Claude to identify itself correctly in your application or use specific API strings:

```text Sample prompt for model identity
The assistant is Claude, created by Anthropic. The current model is Claude Sonnet 4.5.
```

For LLM-powered apps that need to specify model strings:

```text Sample prompt for model string
When an LLM is needed, please default to Claude Sonnet 4.5 unless the user requests otherwise. The exact model string for Claude Sonnet 4.5 is claude-sonnet-4-5-20250929.
```

### Leverage thinking & interleaved thinking capabilities

Claude 4.x models offer thinking capabilities that can be especially helpful for tasks involving reflection after tool use or complex multi-step reasoning. You can guide its initial or interleaved thinking for better results.

```text Example prompt
After receiving tool results, carefully reflect on their quality and determine optimal next steps before proceeding. Use your thinking to plan and iterate based on this new information, and then take the best next action.
```

<Info>
  For more information on thinking capabilities, see `building_with_extended_thinking` below.
</Info>

### Document creation

Claude 4.5 models excel at creating presentations, animations, and visual documents. These models match or exceed Claude Opus 4.1 in this domain, with impressive creative flair and stronger instruction following. The models produce polished, usable output on the first try in most cases.

For best results with document creation:

```text Sample prompt
Create a professional presentation on [topic]. Include thoughtful design elements, visual hierarchy, and engaging animations where appropriate.
```

### Optimize parallel tool calling

Claude 4.x models excel at parallel tool execution, with Sonnet 4.5 being particularly aggressive in firing off multiple operations simultaneously. Claude 4.x models will:

- Run multiple speculative searches during research
- Read several files at once to build context faster
- Execute bash commands in parallel (which can even bottleneck system performance)

This behavior is easily steerable. While the model has a high success rate in parallel tool calling without prompting, you can boost this to ~100% or adjust the aggression level:

```text Sample prompt for maximum parallel efficiency
<use_parallel_tool_calls>
If you intend to call multiple tools and there are no dependencies between the tool calls, make all of the independent tool calls in parallel. Prioritize calling tools simultaneously whenever the actions can be done in parallel rather than sequentially. For example, when reading 3 files, run 3 tool calls in parallel to read all 3 files into context at the same time. Maximize use of parallel tool calls where possible to increase speed and efficiency. However, if some tool calls depend on previous calls to inform dependent values like the parameters, do NOT call these tools in parallel and instead call them sequentially. Never use placeholders or guess missing parameters in tool calls.
</use_parallel_tool_calls>
```

```text Sample prompt to reduce parallel execution
Execute operations sequentially with brief pauses between each step to ensure stability.
```

### Reduce file creation in agentic coding

Claude 4.x models may sometimes create new files for testing and iteration purposes, particularly when working with code. This approach allows Claude to use files, especially python scripts, as a 'temporary scratchpad' before saving its final output. Using temporary files can improve outcomes particularly for agentic coding use cases.

If you'd prefer to minimize net new file creation, you can instruct Claude to clean up after itself:

```text Sample prompt
If you create any temporary new files, scripts, or helper files for iteration, clean up these files by removing them at the end of the task.
```

### Enhance visual and frontend code generation

Claude 4.x models can generate high-quality, visually distinctive, functional user interfaces. However, without guidance, frontend code can default to generic patterns that lack visual interest. To elicit exceptional UI results:

1. **Provide explicit encouragement for creativity:**

```text Sample prompt
Don't hold back. Give it your all. Create an impressive demonstration showcasing web development capabilities.
```

2. **Specify aesthetic direction and design constraints:**

```text Sample prompt
Create a professional dashboard using a dark blue and cyan color palette, modern sans-serif typography (e.g., Inter for headings, system fonts for body), and card-based layouts with subtle shadows. Include thoughtful details like hover states, transitions, and micro-interactions. Apply design principles: hierarchy, contrast, balance, and movement.
```

3. **Encourage design diversity and fusion aesthetics:**

```text Sample prompt
Provide multiple design options. Create fusion aesthetics by combining elements from different sources—one color scheme, different typography, another layout principle. Avoid generic centered layouts, simplistic gradients, and uniform styling.
```

4. **Request specific features explicitly:**

- "Include as many relevant features and interactions as possible"
- "Add animations and interactive elements"
- "Create a fully-featured implementation beyond the basics"

### Avoid focusing on passing tests and hard-coding

Claude 4.x models can sometimes focus too heavily on making tests pass at the expense of more general solutions, or may use workarounds like helper scripts for complex refactoring instead of using standard tools directly. To prevent this behavior and ensure robust, generalizable solutions:

```text Sample prompt
Please write a high-quality, general-purpose solution using the standard tools available. Do not create helper scripts or workarounds to accomplish the task more efficiently. Implement a solution that works correctly for all valid inputs, not just the test cases. Do not hard-code values or create solutions that only work for specific test inputs. Instead, implement the actual logic that solves the problem generally.

Focus on understanding the problem requirements and implementing the correct algorithm. Tests are there to verify correctness, not to define the solution. Provide a principled implementation that follows best practices and software design principles.

If the task is unreasonable or infeasible, or if any of the tests are incorrect, please inform me rather than working around them. The solution should be robust, maintainable, and extendable.
```

### Minimizing hallucinations in agentic coding

Claude 4.x models are less prone to hallucinations and give more accurate, grounded, intelligent answers based on the code. To encourage this behavior even more and minimize hallucinations:

```text Sample prompt
<investigate_before_answering>
Never speculate about code you have not opened. If the user references a specific file, you MUST read the file before answering. Make sure to investigate and read relevant files BEFORE answering questions about the codebase. Never make any claims about code before investigating unless you are certain of the correct answer - give grounded and hallucination-free answers.
</investigate_before_answering>
```
---

<building_with_extended_thinking>
# Building with extended thinking



Extended thinking gives Claude enhanced reasoning capabilities for complex tasks, while providing varying levels of transparency into its step-by-step thought process before it delivers its final answer.

## Supported models

Extended thinking is supported in the following models:

- Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
- Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- Claude Sonnet 3.7 (`claude-3-7-sonnet-20250219`) ([deprecated](/docs/en/about-claude/model-deprecations))
- Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) 
- Claude Opus 4.1 (`claude-opus-4-1-20250805`)
- Claude Opus 4 (`claude-opus-4-20250514`)

<Note>
API behavior differs across Claude Sonnet 3.7 and Claude 4 models, but the API shapes remain exactly the same.

For more information, see [Differences in thinking across model versions](#differences-in-thinking-across-model-versions).
</Note>

## How extended thinking works

When extended thinking is turned on, Claude creates `thinking` content blocks where it outputs its internal reasoning. Claude incorporates insights from this reasoning before crafting a final response.

The API response will include `thinking` content blocks, followed by `text` content blocks.

Here's an example of the default response format:

```json
{
  "content": [
    {
      "type": "thinking",
      "thinking": "Let me analyze this step by step...",
      "signature": "WaUjzkypQ2mUEVM36O2TxuC06KN8xyfbJwyem2dw3URve/op91XWHOEBLLqIOMfFG/UvLEczmEsUjavL...."
    },
    {
      "type": "text",
      "text": "Based on my analysis..."
    }
  ]
}
```

For more information about the response format of extended thinking, see the [Messages API Reference](/docs/en/api/messages).

## How to use extended thinking

Here is an example of using extended thinking in the Messages API:

<CodeGroup>
```bash Shell
curl https://api.anthropic.com/v1/messages \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "model": "claude-sonnet-4-5",
    "max_tokens": 16000,
    "thinking": {
        "type": "enabled",
        "budget_tokens": 10000
    },
    "messages": [
        {
            "role": "user",
            "content": "Are there an infinite number of prime numbers such that n mod 4 == 3?"
        }
    ]
}'
```

```python Python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    messages=[{
        "role": "user",
        "content": "Are there an infinite number of prime numbers such that n mod 4 == 3?"
    }]
)

# The response will contain summarized thinking blocks and text blocks
for block in response.content:
    if block.type == "thinking":
        print(f"\nThinking summary: {block.thinking}")
    elif block.type == "text":
        print(f"\nResponse: {block.text}")
```

```typescript TypeScript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

const response = await client.messages.create({
  model: "claude-sonnet-4-5",
  max_tokens: 16000,
  thinking: {
    type: "enabled",
    budget_tokens: 10000
  },
  messages: [{
    role: "user",
    content: "Are there an infinite number of prime numbers such that n mod 4 == 3?"
  }]
});

// The response will contain summarized thinking blocks and text blocks
for (const block of response.content) {
  if (block.type === "thinking") {
    console.log(`\nThinking summary: ${block.thinking}`);
  } else if (block.type === "text") {
    console.log(`\nResponse: ${block.text}`);
  }
}
```

```java Java
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.beta.messages.*;
import com.anthropic.models.beta.messages.MessageCreateParams;
import com.anthropic.models.messages.*;

public class SimpleThinkingExample {
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        BetaMessage response = client.beta().messages().create(
                MessageCreateParams.builder()
                        .model(Model.CLAUDE_OPUS_4_0)
                        .maxTokens(16000)
                        .thinking(BetaThinkingConfigEnabled.builder().budgetTokens(10000).build())
                        .addUserMessage("Are there an infinite number of prime numbers such that n mod 4 == 3?")
                        .build()
        );

        System.out.println(response);
    }
}
```

</CodeGroup>

To turn on extended thinking, add a `thinking` object, with the `type` parameter set to `enabled` and the `budget_tokens` to a specified token budget for extended thinking.

The `budget_tokens` parameter determines the maximum number of tokens Claude is allowed to use for its internal reasoning process. In Claude 4 models, this limit applies to full thinking tokens, and not to [the summarized output](#summarized-thinking). Larger budgets can improve response quality by enabling more thorough analysis for complex problems, although Claude may not use the entire budget allocated, especially at ranges above 32k.

`budget_tokens` must be set to a value less than `max_tokens`. However, when using [interleaved thinking with tools](#interleaved-thinking), you can exceed this limit as the token limit becomes your entire context window (200k tokens). 

### Summarized thinking

With extended thinking enabled, the Messages API for Claude 4 models returns a summary of Claude's full thinking process. Summarized thinking provides the full intelligence benefits of extended thinking, while preventing misuse.

Here are some important considerations for summarized thinking:

- You're charged for the full thinking tokens generated by the original request, not the summary tokens.
- The billed output token count will **not match** the count of tokens you see in the response.
- The first few lines of thinking output are more verbose, providing detailed reasoning that's particularly helpful for prompt engineering purposes. 
- As Anthropic seeks to improve the extended thinking feature, summarization behavior is subject to change.
- Summarization preserves the key ideas of Claude's thinking process with minimal added latency, enabling a streamable user experience and easy migration from Claude Sonnet 3.7 to Claude 4 models.
- Summarization is processed by a different model than the one you target in your requests. The thinking model does not see the summarized output.

<Note>
Claude Sonnet 3.7 continues to return full thinking output.

In rare cases where you need access to full thinking output for Claude 4 models, [contact our sales team](mailto:sales@anthropic.com).
</Note>

### Streaming thinking

You can stream extended thinking responses using [server-sent events (SSE)](https://developer.mozilla.org/en-US/Web/API/Server-sent%5Fevents/Using%5Fserver-sent%5Fevents).

When streaming is enabled for extended thinking, you receive thinking content via `thinking_delta` events.

For more documention on streaming via the Messages API, see [Streaming Messages](/docs/en/build-with-claude/streaming).

Here's how to handle streaming with thinking:

<CodeGroup>
```bash Shell
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

```python Python
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

```typescript TypeScript
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

```java Java
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.core.http.StreamResponse;
import com.anthropic.models.beta.messages.MessageCreateParams;
import com.anthropic.models.beta.messages.BetaRawMessageStreamEvent;
import com.anthropic.models.beta.messages.BetaThinkingConfigEnabled;
import com.anthropic.models.messages.Model;

public class SimpleThinkingStreamingExample {
    private static boolean thinkingStarted = false;
    private static boolean responseStarted = false;
    
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        MessageCreateParams createParams = MessageCreateParams.builder()
                .model(Model.CLAUDE_OPUS_4_0)
                .maxTokens(16000)
                .thinking(BetaThinkingConfigEnabled.builder().budgetTokens(10000).build())
                .addUserMessage("What is 27 * 453?")
                .build();

        try (StreamResponse<BetaRawMessageStreamEvent> streamResponse =
                     client.beta().messages().createStreaming(createParams)) {
            streamResponse.stream()
                    .forEach(event -> {
                        if (event.isContentBlockStart()) {
                            System.out.printf("\nStarting %s block...%n",
                                    event.asContentBlockStart()._type());
                            // Reset flags for each new block
                            thinkingStarted = false;
                            responseStarted = false;
                        } else if (event.isContentBlockDelta()) {
                            var delta = event.asContentBlockDelta().delta();
                            if (delta.isBetaThinking()) {
                                if (!thinkingStarted) {
                                    System.out.print("Thinking: ");
                                    thinkingStarted = true;
                                }
                                System.out.print(delta.asBetaThinking().thinking());
                                System.out.flush();
                            } else if (delta.isBetaText()) {
                                if (!responseStarted) {
                                    System.out.print("Response: ");
                                    responseStarted = true;
                                }
                                System.out.print(delta.asBetaText().text());
                                System.out.flush();
                            }
                        } else if (event.isContentBlockStop()) {
                            System.out.println("\nBlock complete.");
                        }
                    });
        }
    }
}
```

</CodeGroup>

<TryInConsoleButton userPrompt="What is 27 * 453?" thinkingBudgetTokens={16000}>
  Try in Console
</TryInConsoleButton>
  

Example streaming output:
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

## Extended thinking with tool use

Extended thinking can be used alongside [tool use](/docs/en/agents-and-tools/tool-use/overview), allowing Claude to reason through tool selection and results processing.

When using extended thinking with tool use, be aware of the following limitations:

1. **Tool choice limitation**: Tool use with thinking only supports `tool_choice: {"type": "auto"}` (the default) or `tool_choice: {"type": "none"}`. Using `tool_choice: {"type": "any"}` or `tool_choice: {"type": "tool", "name": "..."}` will result in an error because these options force tool use, which is incompatible with extended thinking.

2. **Preserving thinking blocks**: During tool use, you must pass `thinking` blocks back to the API for the last assistant message. Include the complete unmodified block back to the API to maintain reasoning continuity.

### Toggling thinking modes in conversations

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

#### Common error scenarios

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

#### Practical guidance

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
Toggling thinking modes also invalidates prompt caching for message history. For more details, see the [Extended thinking with prompt caching](#extended-thinking-with-prompt-caching) section.
</Note>

<section title="Example: Passing thinking blocks with tool results">

Here's a practical example showing how to preserve thinking blocks when providing tool results:

<CodeGroup>
```python Python
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

```typescript TypeScript
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

```java Java
import java.util.List;
import java.util.Map;

import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.core.JsonValue;
import com.anthropic.models.beta.messages.BetaMessage;
import com.anthropic.models.beta.messages.MessageCreateParams;
import com.anthropic.models.beta.messages.BetaThinkingConfigEnabled;
import com.anthropic.models.beta.messages.BetaTool;
import com.anthropic.models.beta.messages.BetaTool.InputSchema;
import com.anthropic.models.messages.Model;

public class ThinkingWithToolsExample {
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        InputSchema schema = InputSchema.builder()
                .properties(JsonValue.from(Map.of(
                        "location", Map.of("type", "string")
                )))
                .putAdditionalProperty("required", JsonValue.from(List.of("location")))
                .build();

        BetaTool weatherTool = BetaTool.builder()
                .name("get_weather")
                .description("Get current weather for a location")
                .inputSchema(schema)
                .build();

        BetaMessage response = client.beta().messages().create(
                MessageCreateParams.builder()
                        .model(Model.CLAUDE_OPUS_4_0)
                        .maxTokens(16000)
                        .thinking(BetaThinkingConfigEnabled.builder().budgetTokens(10000).build())
                        .addTool(weatherTool)
                        .addUserMessage("What's the weather in Paris?")
                        .build()
        );

        System.out.println(response);
    }
}
```
</CodeGroup>

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

Now let's continue the conversation and use the tool

<CodeGroup>
```python Python
# Extract thinking block and tool use block
thinking_block = next((block for block in response.content
                      if block.type == 'thinking'), None)
tool_use_block = next((block for block in response.content
                      if block.type == 'tool_use'), None)

# Call your actual weather API, here is where your actual API call would go
# let's pretend this is what we get back
weather_data = {"temperature": 88}

# Second request - Include thinking block and tool result
# No new thinking blocks will be generated in the response
continuation = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    tools=[weather_tool],
    messages=[
        {"role": "user", "content": "What's the weather in Paris?"},
        # notice that the thinking_block is passed in as well as the tool_use_block
        # if this is not passed in, an error is raised
        {"role": "assistant", "content": [thinking_block, tool_use_block]},
        {"role": "user", "content": [{
            "type": "tool_result",
            "tool_use_id": tool_use_block.id,
            "content": f"Current temperature: {weather_data['temperature']}°F"
        }]}
    ]
)
```

```typescript TypeScript
// Extract thinking block and tool use block
const thinkingBlock = response.content.find(block =>
  block.type === 'thinking');
const toolUseBlock = response.content.find(block =>
  block.type === 'tool_use');

// Call your actual weather API, here is where your actual API call would go
// let's pretend this is what we get back
const weatherData = { temperature: 88 };

// Second request - Include thinking block and tool result
// No new thinking blocks will be generated in the response
const continuation = await client.messages.create({
  model: "claude-sonnet-4-5",
  max_tokens: 16000,
  thinking: {
    type: "enabled",
    budget_tokens: 10000
  },
  tools: [weatherTool],
  messages: [
    { role: "user", content: "What's the weather in Paris?" },
    // notice that the thinkingBlock is passed in as well as the toolUseBlock
    // if this is not passed in, an error is raised
    { role: "assistant", content: [thinkingBlock, toolUseBlock] },
    { role: "user", content: [{
      type: "tool_result",
      tool_use_id: toolUseBlock.id,
      content: `Current temperature: ${weatherData.temperature}°F`
    }]}
  ]
});
```

```java Java
import java.util.List;
import java.util.Map;
import java.util.Optional;

import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.core.JsonValue;
import com.anthropic.models.beta.messages.*;
import com.anthropic.models.beta.messages.BetaTool.InputSchema;
import com.anthropic.models.messages.Model;

public class ThinkingToolsResultExample {
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        InputSchema schema = InputSchema.builder()
                .properties(JsonValue.from(Map.of(
                        "location", Map.of("type", "string")
                )))
                .putAdditionalProperty("required", JsonValue.from(List.of("location")))
                .build();

        BetaTool weatherTool = BetaTool.builder()
                .name("get_weather")
                .description("Get current weather for a location")
                .inputSchema(schema)
                .build();

        BetaMessage response = client.beta().messages().create(
                MessageCreateParams.builder()
                        .model(Model.CLAUDE_OPUS_4_0)
                        .maxTokens(16000)
                        .thinking(BetaThinkingConfigEnabled.builder().budgetTokens(10000).build())
                        .addTool(weatherTool)
                        .addUserMessage("What's the weather in Paris?")
                        .build()
        );

        // Extract thinking block and tool use block
        Optional<BetaThinkingBlock> thinkingBlockOpt = response.content().stream()
                .filter(BetaContentBlock::isThinking)
                .map(BetaContentBlock::asThinking)
                .findFirst();

        Optional<BetaToolUseBlock> toolUseBlockOpt = response.content().stream()
                .filter(BetaContentBlock::isToolUse)
                .map(BetaContentBlock::asToolUse)
                .findFirst();

        if (thinkingBlockOpt.isPresent() && toolUseBlockOpt.isPresent()) {
            BetaThinkingBlock thinkingBlock = thinkingBlockOpt.get();
            BetaToolUseBlock toolUseBlock = toolUseBlockOpt.get();

            // Call your actual weather API, here is where your actual API call would go
            // let's pretend this is what we get back
            Map<String, Object> weatherData = Map.of("temperature", 88);

            // Second request - Include thinking block and tool result
            // No new thinking blocks will be generated in the response
            BetaMessage continuation = client.beta().messages().create(
                    MessageCreateParams.builder()
                            .model(Model.CLAUDE_OPUS_4_0)
                            .maxTokens(16000)
                            .thinking(BetaThinkingConfigEnabled.builder().budgetTokens(10000).build())
                            .addTool(weatherTool)
                            .addUserMessage("What's the weather in Paris?")
                            .addAssistantMessageOfBetaContentBlockParams(
                                    // notice that the thinkingBlock is passed in as well as the toolUseBlock
                                    // if this is not passed in, an error is raised
                                    List.of(
                                            BetaContentBlockParam.ofThinking(thinkingBlock.toParam()),
                                            BetaContentBlockParam.ofToolUse(toolUseBlock.toParam())
                                    )
                            )
                            .addUserMessageOfBetaContentBlockParams(List.of(
                                    BetaContentBlockParam.ofToolResult(
                                            BetaToolResultBlockParam.builder()
                                                    .toolUseId(toolUseBlock.id())
                                                    .content(String.format("Current temperature: %d°F", (Integer)weatherData.get("temperature")))
                                                    .build()
                                    )
                            ))
                            .build()
            );

            System.out.println(continuation);
        }
    }
}
```
</CodeGroup>

The API response will now **only** include text

```json
{
    "content": [
        {
            "type": "text",
            "text": "Currently in Paris, the temperature is 88°F (31°C)"
        }
    ]
}
```

</section>

### Preserving thinking blocks

During tool use, you must pass `thinking` blocks back to the API, and you must include the complete unmodified block back to the API. This is critical for maintaining the model's reasoning flow and conversation integrity.

<Tip>
While you can omit `thinking` blocks from prior `assistant` role turns, we suggest always passing back all thinking blocks to the API for any multi-turn conversation. The API will:
- Automatically filter the provided thinking blocks
- Use the relevant thinking blocks necessary to preserve the model's reasoning
- Only bill for the input tokens for the blocks shown to Claude
</Tip>

<Note>
When toggling thinking modes during a conversation, remember that the entire assistant turn (including tool use loops) must operate in a single thinking mode. For more details, see [Toggling thinking modes in conversations](#toggling-thinking-modes-in-conversations).
</Note>

When Claude invokes tools, it is pausing its construction of a response to await external information. When tool results are returned, Claude will continue building that existing response. This necessitates preserving thinking blocks during tool use, for a couple of reasons:

1. **Reasoning continuity**: The thinking blocks capture Claude's step-by-step reasoning that led to tool requests. When you post tool results, including the original thinking ensures Claude can continue its reasoning from where it left off.

2. **Context maintenance**: While tool results appear as user messages in the API structure, they're part of a continuous reasoning flow. Preserving thinking blocks maintains this conceptual flow across multiple API calls. For more information on context management, see our [guide on context windows](/docs/en/build-with-claude/context-windows).

**Important**: When providing `thinking` blocks, the entire sequence of consecutive `thinking` blocks must match the outputs generated by the model during the original request; you cannot rearrange or modify the sequence of these blocks.

### Interleaved thinking

Extended thinking with tool use in Claude 4 models supports interleaved thinking, which enables Claude to think between tool calls and make more sophisticated reasoning after receiving tool results.

With interleaved thinking, Claude can:
- Reason about the results of a tool call before deciding what to do next
- Chain multiple tool calls with reasoning steps in between
- Make more nuanced decisions based on intermediate results

To enable interleaved thinking, add [the beta header](/docs/en/api/beta-headers) `interleaved-thinking-2025-05-14` to your API request.

Here are some important considerations for interleaved thinking:
- With interleaved thinking, the `budget_tokens` can exceed the `max_tokens` parameter, as it represents the total budget across all thinking blocks within one assistant turn.
- Interleaved thinking is only supported for [tools used via the Messages API](/docs/en/agents-and-tools/tool-use/overview).
- Interleaved thinking is supported for Claude 4 models only, with the beta header `interleaved-thinking-2025-05-14`.
- Direct calls to the Claude API allow you to pass `interleaved-thinking-2025-05-14` in requests to any model, with no effect.
- On 3rd-party platforms (e.g., [Amazon Bedrock](/docs/en/build-with-claude/claude-on-amazon-bedrock) and [Vertex AI](/docs/en/build-with-claude/claude-on-vertex-ai)), if you pass `interleaved-thinking-2025-05-14` to any model aside from Claude Opus 4.1, Opus 4, or Sonnet 4, your request will fail.

<section title="Tool use without interleaved thinking">

<CodeGroup>
```python Python
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

```typescript TypeScript
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

```java Java
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.core.JsonValue;
import com.anthropic.models.beta.messages.*;
import com.anthropic.models.messages.Model;
import java.util.List;
import java.util.Map;

public class NonInterleavedThinkingExample {
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        // Define calculator tool
        BetaTool.InputSchema calculatorSchema = BetaTool.InputSchema.builder()
                .properties(JsonValue.from(Map.of(
                        "expression", Map.of(
                                "type", "string",
                                "description", "Mathematical expression to evaluate"
                        )
                )))
                .putAdditionalProperty("required", JsonValue.from(List.of("expression")))
                .build();

        BetaTool calculatorTool = BetaTool.builder()
                .name("calculator")
                .description("Perform mathematical calculations")
                .inputSchema(calculatorSchema)
                .build();

        // Define database tool
        BetaTool.InputSchema databaseSchema = BetaTool.InputSchema.builder()
                .properties(JsonValue.from(Map.of(
                        "query", Map.of(
                                "type", "string",
                                "description", "SQL query to execute"
                        )
                )))
                .putAdditionalProperty("required", JsonValue.from(List.of("query")))
                .build();

        BetaTool databaseTool = BetaTool.builder()
                .name("database_query")
                .description("Query product database")
                .inputSchema(databaseSchema)
                .build();

        // First request - Claude thinks once before all tool calls
        BetaMessage response = client.beta().messages().create(
                MessageCreateParams.builder()
                        .model(Model.CLAUDE_OPUS_4_0)
                        .maxTokens(16000)
                        .thinking(BetaThinkingConfigEnabled.builder()
                                .budgetTokens(10000)
                                .build())
                        .addTool(calculatorTool)
                        .addTool(databaseTool)
                        .addUserMessage("What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?")
                        .build()
        );

        // Response includes thinking followed by tool uses
        // Note: Claude thinks once at the beginning, then makes all tool decisions
        System.out.println("First response:");
        for (BetaContentBlock block : response.content()) {
            if (block.isThinking()) {
                System.out.println("Thinking (summarized): " + block.asThinking().thinking());
            } else if (block.isToolUse()) {
                BetaToolUseBlock toolUse = block.asToolUse();
                System.out.println("Tool use: " + toolUse.name() + " with input " + toolUse.input());
            } else if (block.isText()) {
                System.out.println("Text: " + block.asText().text());
            }
        }

        // You would execute the tools and return results...
        // After getting both tool results back, Claude directly responds without additional thinking
    }
}
```
</CodeGroup>

In this example without interleaved thinking:
1. Claude thinks once at the beginning to understand the task
2. Makes all tool use decisions upfront
3. When tool results are returned, Claude immediately provides a response without additional thinking

</section>

<section title="Tool use with interleaved thinking">

<CodeGroup>
```python Python
import anthropic

client = anthropic.Anthropic()

# Same tool definitions as before
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

# First request with interleaved thinking enabled
response = client.beta.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    tools=[calculator_tool, database_tool],
    betas=["interleaved-thinking-2025-05-14"],
    messages=[{
        "role": "user",
        "content": "What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?"
    }]
)

print("Initial response:")
thinking_blocks = []
tool_use_blocks = []

for block in response.content:
    if block.type == "thinking":
        thinking_blocks.append(block)
        print(f"Thinking: {block.thinking}")
    elif block.type == "tool_use":
        tool_use_blocks.append(block)
        print(f"Tool use: {block.name} with input {block.input}")
    elif block.type == "text":
        print(f"Text: {block.text}")

# First tool result (calculator)
calculator_result = "7500"  # 150 * 50

# Continue with first tool result
response2 = client.beta.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    tools=[calculator_tool, database_tool],
    betas=["interleaved-thinking-2025-05-14"],
    messages=[
        {
            "role": "user",
            "content": "What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?"
        },
        {
            "role": "assistant",
            "content": [thinking_blocks[0], tool_use_blocks[0]]
        },
        {
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_blocks[0].id,
                "content": calculator_result
            }]
        }
    ]
)

print("\nAfter calculator result:")
# With interleaved thinking, Claude can think about the calculator result
# before deciding to query the database
for block in response2.content:
    if block.type == "thinking":
        thinking_blocks.append(block)
        print(f"Interleaved thinking: {block.thinking}")
    elif block.type == "tool_use":
        tool_use_blocks.append(block)
        print(f"Tool use: {block.name} with input {block.input}")

# Second tool result (database)
database_result = "5200"  # Example average monthly revenue

# Continue with second tool result
response3 = client.beta.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    tools=[calculator_tool, database_tool],
    betas=["interleaved-thinking-2025-05-14"],
    messages=[
        {
            "role": "user",
            "content": "What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?"
        },
        {
            "role": "assistant",
            "content": [thinking_blocks[0], tool_use_blocks[0]]
        },
        {
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_blocks[0].id,
                "content": calculator_result
            }]
        },
        {
            "role": "assistant",
            "content": thinking_blocks[1:] + tool_use_blocks[1:]
        },
        {
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_blocks[1].id,
                "content": database_result
            }]
        }
    ]
)

print("\nAfter database result:")
# With interleaved thinking, Claude can think about both results
# before formulating the final response
for block in response3.content:
    if block.type == "thinking":
        print(f"Final thinking: {block.thinking}")
    elif block.type == "text":
        print(f"Final response: {block.text}")
```

```typescript TypeScript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

// Same tool definitions as before
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

// First request with interleaved thinking enabled
const response = await client.beta.messages.create({
  // Enable interleaved thinking
  betas: ["interleaved-thinking-2025-05-14"],
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

console.log("Initial response:");
const thinkingBlocks = [];
const toolUseBlocks = [];

for (const block of response.content) {
  if (block.type === "thinking") {
    thinkingBlocks.push(block);
    console.log(`Thinking: ${block.thinking}`);
  } else if (block.type === "tool_use") {
    toolUseBlocks.push(block);
    console.log(`Tool use: ${block.name} with input ${JSON.stringify(block.input)}`);
  } else if (block.type === "text") {
    console.log(`Text: ${block.text}`);
  }
}

// First tool result (calculator)
const calculatorResult = "7500"; // 150 * 50

// Continue with first tool result
const response2 = await client.beta.messages.create({
  betas: ["interleaved-thinking-2025-05-14"],
  model: "claude-sonnet-4-5",
  max_tokens: 16000,
  thinking: {
    type: "enabled",
    budget_tokens: 10000
  },
  tools: [calculatorTool, databaseTool],
  messages: [
    {
      role: "user",
      content: "What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?"
    },
    {
      role: "assistant",
      content: [thinkingBlocks[0], toolUseBlocks[0]]
    },
    {
      role: "user",
      content: [{
        type: "tool_result",
        tool_use_id: toolUseBlocks[0].id,
        content: calculatorResult
      }]
    }
  ]
});

console.log("\nAfter calculator result:");
// With interleaved thinking, Claude can think about the calculator result
// before deciding to query the database
for (const block of response2.content) {
  if (block.type === "thinking") {
    thinkingBlocks.push(block);
    console.log(`Interleaved thinking: ${block.thinking}`);
  } else if (block.type === "tool_use") {
    toolUseBlocks.push(block);
    console.log(`Tool use: ${block.name} with input ${JSON.stringify(block.input)}`);
  }
}

// Second tool result (database)
const databaseResult = "5200"; // Example average monthly revenue

// Continue with second tool result
const response3 = await client.beta.messages.create({
  betas: ["interleaved-thinking-2025-05-14"],
  model: "claude-sonnet-4-5",
  max_tokens: 16000,
  thinking: {
    type: "enabled",
    budget_tokens: 10000
  },
  tools: [calculatorTool, databaseTool],
  messages: [
    {
      role: "user",
      content: "What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?"
    },
    {
      role: "assistant",
      content: [thinkingBlocks[0], toolUseBlocks[0]]
    },
    {
      role: "user",
      content: [{
        type: "tool_result",
        tool_use_id: toolUseBlocks[0].id,
        content: calculatorResult
      }]
    },
    {
      role: "assistant",
      content: thinkingBlocks.slice(1).concat(toolUseBlocks.slice(1))
    },
    {
      role: "user",
      content: [{
        type: "tool_result",
        tool_use_id: toolUseBlocks[1].id,
        content: databaseResult
      }]
    }
  ]
});

console.log("\nAfter database result:");
// With interleaved thinking, Claude can think about both results
// before formulating the final response
for (const block of response3.content) {
  if (block.type === "thinking") {
    console.log(`Final thinking: ${block.thinking}`);
  } else if (block.type === "text") {
    console.log(`Final response: ${block.text}`);
  }
}
```

```java Java
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.core.JsonValue;
import com.anthropic.models.beta.messages.*;
import com.anthropic.models.messages.Model;
import java.util.*;
import static java.util.stream.Collectors.toList;

public class InterleavedThinkingExample {
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        // Define calculator tool
        BetaTool.InputSchema calculatorSchema = BetaTool.InputSchema.builder()
                .properties(JsonValue.from(Map.of(
                        "expression", Map.of(
                                "type", "string",
                                "description", "Mathematical expression to evaluate"
                        )
                )))
                .putAdditionalProperty("required", JsonValue.from(List.of("expression")))
                .build();

        BetaTool calculatorTool = BetaTool.builder()
                .name("calculator")
                .description("Perform mathematical calculations")
                .inputSchema(calculatorSchema)
                .build();

        // Define database tool
        BetaTool.InputSchema databaseSchema = BetaTool.InputSchema.builder()
                .properties(JsonValue.from(Map.of(
                        "query", Map.of(
                                "type", "string",
                                "description", "SQL query to execute"
                        )
                )))
                .putAdditionalProperty("required", JsonValue.from(List.of("query")))
                .build();

        BetaTool databaseTool = BetaTool.builder()
                .name("database_query")
                .description("Query product database")
                .inputSchema(databaseSchema)
                .build();

        // First request with interleaved thinking enabled
        BetaMessage response = client.beta().messages().create(
                MessageCreateParams.builder()
                        .model(Model.CLAUDE_OPUS_4_0)
                        .maxTokens(16000)
                        .thinking(BetaThinkingConfigEnabled.builder()
                                .budgetTokens(10000)
                                .build())
                        .addTool(calculatorTool)
                        .addTool(databaseTool)
                        // Enable interleaved thinking with beta header
                        .putAdditionalHeader("anthropic-beta", "interleaved-thinking-2025-05-14")
                        .addUserMessage("What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?")
                        .build()
        );

        System.out.println("Initial response:");
        List<BetaThinkingBlock> thinkingBlocks = new ArrayList<>();
        List<BetaToolUseBlock> toolUseBlocks = new ArrayList<>();

        for (BetaContentBlock block : response.content()) {
            if (block.isThinking()) {
                BetaThinkingBlock thinking = block.asThinking();
                thinkingBlocks.add(thinking);
                System.out.println("Thinking: " + thinking.thinking());
            } else if (block.isToolUse()) {
                BetaToolUseBlock toolUse = block.asToolUse();
                toolUseBlocks.add(toolUse);
                System.out.println("Tool use: " + toolUse.name() + " with input " + toolUse.input());
            } else if (block.isText()) {
                System.out.println("Text: " + block.asText().text());
            }
        }

        // First tool result (calculator)
        String calculatorResult = "7500"; // 150 * 50

        // Continue with first tool result
        BetaMessage response2 = client.beta().messages().create(
                MessageCreateParams.builder()
                        .model(Model.CLAUDE_OPUS_4_0)
                        .maxTokens(16000)
                        .thinking(BetaThinkingConfigEnabled.builder()
                                .budgetTokens(10000)
                                .build())
                        .addTool(calculatorTool)
                        .addTool(databaseTool)
                        .putAdditionalHeader("anthropic-beta", "interleaved-thinking-2025-05-14")
                        .addUserMessage("What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?")
                        .addAssistantMessageOfBetaContentBlockParams(List.of(
                                BetaContentBlockParam.ofThinking(thinkingBlocks.get(0).toParam()),
                                BetaContentBlockParam.ofToolUse(toolUseBlocks.get(0).toParam())
                        ))
                        .addUserMessageOfBetaContentBlockParams(List.of(
                                BetaContentBlockParam.ofToolResult(
                                        BetaToolResultBlockParam.builder()
                                                .toolUseId(toolUseBlocks.get(0).id())
                                                .content(calculatorResult)
                                                .build()
                                )
                        ))
                        .build()
        );

        System.out.println("\nAfter calculator result:");
        // With interleaved thinking, Claude can think about the calculator result
        // before deciding to query the database
        for (BetaContentBlock block : response2.content()) {
            if (block.isThinking()) {
                BetaThinkingBlock thinking = block.asThinking();
                thinkingBlocks.add(thinking);
                System.out.println("Interleaved thinking: " + thinking.thinking());
            } else if (block.isToolUse()) {
                BetaToolUseBlock toolUse = block.asToolUse();
                toolUseBlocks.add(toolUse);
                System.out.println("Tool use: " + toolUse.name() + " with input " + toolUse.input());
            }
        }

        // Second tool result (database)
        String databaseResult = "5200"; // Example average monthly revenue

        // Prepare combined content for assistant message
        List<BetaContentBlockParam> combinedContent = new ArrayList<>();
        for (int i = 1; i < thinkingBlocks.size(); i++) {
            combinedContent.add(BetaContentBlockParam.ofThinking(thinkingBlocks.get(i).toParam()));
        }
        for (int i = 1; i < toolUseBlocks.size(); i++) {
            combinedContent.add(BetaContentBlockParam.ofToolUse(toolUseBlocks.get(i).toParam()));
        }

        // Continue with second tool result
        BetaMessage response3 = client.beta().messages().create(
                MessageCreateParams.builder()
                        .model(Model.CLAUDE_OPUS_4_0)
                        .maxTokens(16000)
                        .thinking(BetaThinkingConfigEnabled.builder()
                                .budgetTokens(10000)
                                .build())
                        .addTool(calculatorTool)
                        .addTool(databaseTool)
                        .putAdditionalHeader("anthropic-beta", "interleaved-thinking-2025-05-14")
                        .addUserMessage("What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?")
                        .addAssistantMessageOfBetaContentBlockParams(List.of(
                                BetaContentBlockParam.ofThinking(thinkingBlocks.get(0).toParam()),
                                BetaContentBlockParam.ofToolUse(toolUseBlocks.get(0).toParam())
                        ))
                        .addUserMessageOfBetaContentBlockParams(List.of(
                                BetaContentBlockParam.ofToolResult(
                                        BetaToolResultBlockParam.builder()
                                                .toolUseId(toolUseBlocks.get(0).id())
                                                .content(calculatorResult)
                                                .build()
                                )
                        ))
                        .addAssistantMessageOfBetaContentBlockParams(combinedContent)
                        .addUserMessageOfBetaContentBlockParams(List.of(
                                BetaContentBlockParam.ofToolResult(
                                        BetaToolResultBlockParam.builder()
                                                .toolUseId(toolUseBlocks.get(1).id())
                                                .content(databaseResult)
                                                .build()
                                )
                        ))
                        .build()
        );

        System.out.println("\nAfter database result:");
        // With interleaved thinking, Claude can think about both results
        // before formulating the final response
        for (BetaContentBlock block : response3.content()) {
            if (block.isThinking()) {
                System.out.println("Final thinking: " + block.asThinking().thinking());
            } else if (block.isText()) {
                System.out.println("Final response: " + block.asText().text());
            }
        }
    }
}
```
</CodeGroup>

In this example with interleaved thinking:
1. Claude thinks about the task initially
2. After receiving the calculator result, Claude can think again about what that result means
3. Claude then decides how to query the database based on the first result
4. After receiving the database result, Claude thinks once more about both results before formulating a final response
5. The thinking budget is distributed across all thinking blocks within the turn

This pattern allows for more sophisticated reasoning chains where each tool's output informs the next decision.

</section>

## Extended thinking with prompt caching

[Prompt caching](/docs/en/build-with-claude/prompt-caching) with thinking has several important considerations:

<Tip>
Extended thinking tasks often take longer than 5 minutes to complete. Consider using the [1-hour cache duration](/docs/en/build-with-claude/prompt-caching#1-hour-cache-duration) to maintain cache hits across longer thinking sessions and multi-step workflows.
</Tip>

**Thinking block context removal**
- Thinking blocks from previous turns are removed from context, which can affect cache breakpoints
- When continuing conversations with tool use, thinking blocks are cached and count as input tokens when read from cache
- This creates a tradeoff: while thinking blocks don't consume context window space visually, they still count toward your input token usage when cached
- If thinking becomes disabled, requests will fail if you pass thinking content in the current tool use turn. In other contexts, thinking content passed to the API is simply ignored

**Cache invalidation patterns**
- Changes to thinking parameters (enabled/disabled or budget allocation) invalidate message cache breakpoints
- [Interleaved thinking](#interleaved-thinking) amplifies cache invalidation, as thinking blocks can occur between multiple [tool calls](#extended-thinking-with-tool-use)
- System prompts and tools remain cached despite thinking parameter changes or block removal

<Note>
While thinking blocks are removed for caching and context calculations, they must be preserved when continuing conversations with [tool use](#extended-thinking-with-tool-use), especially with [interleaved thinking](#interleaved-thinking).
</Note>

### Understanding thinking block caching behavior

When using extended thinking with tool use, thinking blocks exhibit specific caching behavior that affects token counting:

**How it works:**

1. Caching only occurs when you make a subsequent request that includes tool results
2. When the subsequent request is made, the previous conversation history (including thinking blocks) can be cached
3. These cached thinking blocks count as input tokens in your usage metrics when read from the cache
4. When a non-tool-result user block is included, all previous thinking blocks are ignored and stripped from context

**Detailed example flow:**

**Request 1:**
```
User: "What's the weather in Paris?"
```
**Response 1:**
```
[thinking_block_1] + [tool_use block 1]
```

**Request 2:**
```
User: ["What's the weather in Paris?"], 
Assistant: [thinking_block_1] + [tool_use block 1], 
User: [tool_result_1, cache=True]
```
**Response 2:**
```
[thinking_block_2] + [text block 2]
```
Request 2 writes a cache of the request content (not the response). The cache includes the original user message, the first thinking block, tool use block, and the tool result.

**Request 3:**
```
User: ["What's the weather in Paris?"], 
Assistant: [thinking_block_1] + [tool_use block 1], 
User: [tool_result_1, cache=True], 
Assistant: [thinking_block_2] + [text block 2], 
User: [Text response, cache=True]
```
Because a non-tool-result user block was included, all previous thinking blocks are ignored. This request will be processed the same as:
```
User: ["What's the weather in Paris?"], 
Assistant: [tool_use block 1], 
User: [tool_result_1, cache=True], 
Assistant: [text block 2], 
User: [Text response, cache=True]
```

**Key points:**
- This caching behavior happens automatically, even without explicit `cache_control` markers
- This behavior is consistent whether using regular thinking or interleaved thinking

<section title="System prompt caching (preserved when thinking changes)">

<CodeGroup>
```python Python
from anthropic import Anthropic
import requests
from bs4 import BeautifulSoup

client = Anthropic()

def fetch_article_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get text
    text = soup.get_text()

    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text

# Fetch the content of the article
book_url = "https://www.gutenberg.org/cache/epub/1342/pg1342.txt"
book_content = fetch_article_content(book_url)
# Use just enough text for caching (first few chapters)
LARGE_TEXT = book_content[:5000]

SYSTEM_PROMPT=[
    {
        "type": "text",
        "text": "You are an AI assistant that is tasked with literary analysis. Analyze the following text carefully.",
    },
    {
        "type": "text",
        "text": LARGE_TEXT,
        "cache_control": {"type": "ephemeral"}
    }
]

MESSAGES = [
    {
        "role": "user",
        "content": "Analyze the tone of this passage."
    }
]

# First request - establish cache
print("First request - establishing cache")
response1 = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=20000,
    thinking={
        "type": "enabled",
        "budget_tokens": 4000
    },
    system=SYSTEM_PROMPT,
    messages=MESSAGES
)

print(f"First response usage: {response1.usage}")

MESSAGES.append({
    "role": "assistant",
    "content": response1.content
})
MESSAGES.append({
    "role": "user",
    "content": "Analyze the characters in this passage."
})
# Second request - same thinking parameters (cache hit expected)
print("\nSecond request - same thinking parameters (cache hit expected)")
response2 = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=20000,
    thinking={
        "type": "enabled",
        "budget_tokens": 4000
    },
    system=SYSTEM_PROMPT,
    messages=MESSAGES
)

print(f"Second response usage: {response2.usage}")

# Third request - different thinking parameters (cache miss for messages)
print("\nThird request - different thinking parameters (cache miss for messages)")
response3 = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=20000,
    thinking={
        "type": "enabled",
        "budget_tokens": 8000  # Changed thinking budget
    },
    system=SYSTEM_PROMPT,  # System prompt remains cached
    messages=MESSAGES  # Messages cache is invalidated
)

print(f"Third response usage: {response3.usage}")
```

```typescript TypeScript
import Anthropic from '@anthropic-ai/sdk';
import axios from 'axios';
import * as cheerio from 'cheerio';

const client = new Anthropic();

async function fetchArticleContent(url: string): Promise<string> {
  const response = await axios.get(url);
  const $ = cheerio.load(response.data);
  
  // Remove script and style elements
  $('script, style').remove();
  
  // Get text
  let text = $.text();
  
  // Break into lines and remove leading and trailing space on each
  const lines = text.split('\n').map(line => line.trim());
  // Drop blank lines
  text = lines.filter(line => line.length > 0).join('\n');
  
  return text;
}

// Fetch the content of the article
const bookUrl = "https://www.gutenberg.org/cache/epub/1342/pg1342.txt";
const bookContent = await fetchArticleContent(bookUrl);
// Use just enough text for caching (first few chapters)
const LARGE_TEXT = bookContent.slice(0, 5000);

const SYSTEM_PROMPT = [
  {
    type: "text",
    text: "You are an AI assistant that is tasked with literary analysis. Analyze the following text carefully.",
  },
  {
    type: "text",
    text: LARGE_TEXT,
    cache_control: { type: "ephemeral" }
  }
];

const MESSAGES = [
  {
    role: "user",
    content: "Analyze the tone of this passage."
  }
];

// First request - establish cache
console.log("First request - establishing cache");
const response1 = await client.messages.create({
  model: "claude-sonnet-4-5",
  max_tokens: 20000,
  thinking: {
    type: "enabled",
    budget_tokens: 4000
  },
  system: SYSTEM_PROMPT,
  messages: MESSAGES
});

console.log(`First response usage: ${response1.usage}`);

MESSAGES.push({
  role: "assistant",
  content: response1.content
});
MESSAGES.push({
  role: "user",
  content: "Analyze the characters in this passage."
});

// Second request - same thinking parameters (cache hit expected)
console.log("\nSecond request - same thinking parameters (cache hit expected)");
const response2 = await client.messages.create({
  model: "claude-sonnet-4-5",
  max_tokens: 20000,
  thinking: {
    type: "enabled",
    budget_tokens: 4000
  },
  system: SYSTEM_PROMPT,
  messages: MESSAGES
});

console.log(`Second response usage: ${response2.usage}`);

// Third request - different thinking parameters (cache miss for messages)
console.log("\nThird request - different thinking parameters (cache miss for messages)");
const response3 = await client.messages.create({
  model: "claude-sonnet-4-5",
  max_tokens: 20000,
  thinking: {
    type: "enabled",
    budget_tokens: 8000  // Changed thinking budget
  },
  system: SYSTEM_PROMPT,  // System prompt remains cached
  messages: MESSAGES  // Messages cache is invalidated
});

console.log(`Third response usage: ${response3.usage}`);
```
</CodeGroup>

</section>
<section title="Messages caching (invalidated when thinking changes)">

<CodeGroup>
```python Python
from anthropic import Anthropic
import requests
from bs4 import BeautifulSoup

client = Anthropic()

def fetch_article_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get text
    text = soup.get_text()

    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text

# Fetch the content of the article
book_url = "https://www.gutenberg.org/cache/epub/1342/pg1342.txt"
book_content = fetch_article_content(book_url)
# Use just enough text for caching (first few chapters)
LARGE_TEXT = book_content[:5000]

# No system prompt - caching in messages instead
MESSAGES = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": LARGE_TEXT,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": "Analyze the tone of this passage."
            }
        ]
    }
]

# First request - establish cache
print("First request - establishing cache")
response1 = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=20000,
    thinking={
        "type": "enabled",
        "budget_tokens": 4000
    },
    messages=MESSAGES
)

print(f"First response usage: {response1.usage}")

MESSAGES.append({
    "role": "assistant",
    "content": response1.content
})
MESSAGES.append({
    "role": "user",
    "content": "Analyze the characters in this passage."
})
# Second request - same thinking parameters (cache hit expected)
print("\nSecond request - same thinking parameters (cache hit expected)")
response2 = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=20000,
    thinking={
        "type": "enabled",
        "budget_tokens": 4000  # Same thinking budget
    },
    messages=MESSAGES
)

print(f"Second response usage: {response2.usage}")

MESSAGES.append({
    "role": "assistant",
    "content": response2.content
})
MESSAGES.append({
    "role": "user",
    "content": "Analyze the setting in this passage."
})

# Third request - different thinking budget (cache miss expected)
print("\nThird request - different thinking budget (cache miss expected)")
response3 = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=20000,
    thinking={
        "type": "enabled",
        "budget_tokens": 8000  # Different thinking budget breaks cache
    },
    messages=MESSAGES
)

print(f"Third response usage: {response3.usage}")
```

```typescript TypeScript
import Anthropic from '@anthropic-ai/sdk';
import axios from 'axios';
import * as cheerio from 'cheerio';

const client = new Anthropic();

async function fetchArticleContent(url: string): Promise<string> {
  const response = await axios.get(url);
  const $ = cheerio.load(response.data);

  // Remove script and style elements
  $('script, style').remove();

  // Get text
  let text = $.text();

  // Clean up text (break into lines, remove whitespace)
  const lines = text.split('\n').map(line => line.trim());
  const chunks = lines.flatMap(line => line.split('  ').map(phrase => phrase.trim()));
  text = chunks.filter(chunk => chunk).join('\n');

  return text;
}

async function main() {
  // Fetch the content of the article
  const bookUrl = "https://www.gutenberg.org/cache/epub/1342/pg1342.txt";
  const bookContent = await fetchArticleContent(bookUrl);
  // Use just enough text for caching (first few chapters)
  const LARGE_TEXT = bookContent.substring(0, 5000);

  // No system prompt - caching in messages instead
  let MESSAGES = [
    {
      role: "user",
      content: [
        {
          type: "text",
          text: LARGE_TEXT,
          cache_control: {type: "ephemeral"},
        },
        {
          type: "text",
          text: "Analyze the tone of this passage."
        }
      ]
    }
  ];

  // First request - establish cache
  console.log("First request - establishing cache");
  const response1 = await client.messages.create({
    model: "claude-sonnet-4-5",
    max_tokens: 20000,
    thinking: {
      type: "enabled",
      budget_tokens: 4000
    },
    messages: MESSAGES
  });

  console.log(`First response usage: `, response1.usage);

  MESSAGES = [
    ...MESSAGES,
    {
      role: "assistant",
      content: response1.content
    },
    {
      role: "user",
      content: "Analyze the characters in this passage."
    }
  ];

  // Second request - same thinking parameters (cache hit expected)
  console.log("\nSecond request - same thinking parameters (cache hit expected)");
  const response2 = await client.messages.create({
    model: "claude-sonnet-4-5",
    max_tokens: 20000,
    thinking: {
      type: "enabled",
      budget_tokens: 4000  // Same thinking budget
    },
    messages: MESSAGES
  });

  console.log(`Second response usage: `, response2.usage);

  MESSAGES = [
    ...MESSAGES,
    {
      role: "assistant",
      content: response2.content
    },
    {
      role: "user",
      content: "Analyze the setting in this passage."
    }
  ];

  // Third request - different thinking budget (cache miss expected)
  console.log("\nThird request - different thinking budget (cache miss expected)");
  const response3 = await client.messages.create({
    model: "claude-sonnet-4-5",
    max_tokens: 20000,
    thinking: {
      type: "enabled",
      budget_tokens: 8000  // Different thinking budget breaks cache
    },
    messages: MESSAGES
  });

  console.log(`Third response usage: `, response3.usage);
}

main().catch(console.error);
```

```java Java
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;
import java.util.Arrays;
import java.util.regex.Pattern;

import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.beta.messages.*;
import com.anthropic.models.beta.messages.MessageCreateParams;
import com.anthropic.models.messages.Model;

import static java.util.stream.Collectors.joining;
import static java.util.stream.Collectors.toList;

public class ThinkingCacheExample {
    public static void main(String[] args) throws IOException {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        // Fetch the content of the article
        String bookUrl = "https://www.gutenberg.org/cache/epub/1342/pg1342.txt";
        String bookContent = fetchArticleContent(bookUrl);
        // Use just enough text for caching (first few chapters)
        String largeText = bookContent.substring(0, 5000);

        List<BetaTextBlockParam> systemPrompt = List.of(
                BetaTextBlockParam.builder()
                        .text("You are an AI assistant that is tasked with literary analysis. Analyze the following text carefully.")
                        .build(),
                BetaTextBlockParam.builder()
                        .text(largeText)
                        .cacheControl(BetaCacheControlEphemeral.builder().build())
                        .build()
        );

        List<BetaMessageParam> messages = new ArrayList<>();
        messages.add(BetaMessageParam.builder()
                .role(BetaMessageParam.Role.USER)
                .content("Analyze the tone of this passage.")
                .build());

        // First request - establish cache
        System.out.println("First request - establishing cache");
        BetaMessage response1 = client.beta().messages().create(
                MessageCreateParams.builder()
                        .model(Model.CLAUDE_OPUS_4_0)
                        .maxTokens(20000)
                        .thinking(BetaThinkingConfigEnabled.builder().budgetTokens(4000).build())
                        .systemOfBetaTextBlockParams(systemPrompt)
                        .messages(messages)
                        .build()
        );

        System.out.println("First response usage: " + response1.usage());

        // Second request - same thinking parameters (cache hit expected)
        System.out.println("\nSecond request - same thinking parameters (cache hit expected)");
        BetaMessage response2 = client.beta().messages().create(
                MessageCreateParams.builder()
                        .model(Model.CLAUDE_OPUS_4_0)
                        .maxTokens(20000)
                        .thinking(BetaThinkingConfigEnabled.builder().budgetTokens(4000).build())
                        .systemOfBetaTextBlockParams(systemPrompt)
                        .addMessage(response1)
                        .addUserMessage("Analyze the characters in this passage.")
                        .messages(messages)
                        .build()
        );

        System.out.println("Second response usage: " + response2.usage());

        // Third request - different thinking budget (cache hit expected because system prompt caching)
        System.out.println("\nThird request - different thinking budget (cache hit expected)");
        BetaMessage response3 = client.beta().messages().create(
                MessageCreateParams.builder()
                        .model(Model.CLAUDE_OPUS_4_0)
                        .maxTokens(20000)
                        .thinking(BetaThinkingConfigEnabled.builder().budgetTokens(8000).build())
                        .systemOfBetaTextBlockParams(systemPrompt)
                        .addMessage(response1)
                        .addUserMessage("Analyze the characters in this passage.")
                        .addMessage(response2)
                        .addUserMessage("Analyze the setting in this passage.")
                        .build()
        );

        System.out.println("Third response usage: " + response3.usage());
    }

    private static String fetchArticleContent(String url) throws IOException {
        // Fetch HTML content
        String htmlContent = fetchHtml(url);

        // Remove script and style elements
        String noScriptStyle = removeElements(htmlContent, "script", "style");

        // Extract text (simple approach - remove HTML tags)
        String text = removeHtmlTags(noScriptStyle);

        // Clean up text (break into lines, remove whitespace)
        List<String> lines = Arrays.asList(text.split("\n"));
        List<String> trimmedLines = lines.stream()
                .map(String::trim)
                .collect(toList());

        // Split on double spaces and flatten
        List<String> chunks = trimmedLines.stream()
                .flatMap(line -> Arrays.stream(line.split("  "))
                        .map(String::trim))
                .collect(toList());

        // Filter empty chunks and join with newlines
        return chunks.stream()
                .filter(chunk -> !chunk.isEmpty())
                .collect(joining("\n"));
    }

    /**
     * Fetches HTML content from a URL
     */
    private static String fetchHtml(String urlString) throws IOException {
        try (InputStream inputStream = new URL(urlString).openStream()) {
            StringBuilder content = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(inputStream))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    content.append(line).append("\n");
                }
            }
            return content.toString();
        }
    }

    /**
     * Removes specified HTML elements and their content
     */
    private static String removeElements(String html, String... elementNames) {
        String result = html;
        for (String element : elementNames) {
            // Pattern to match <element>...</element> and self-closing tags
            String pattern = "<" + element + "\\s*[^>]*>.*?</" + element + ">|<" + element + "\\s*[^>]*/?>";
            result = Pattern.compile(pattern, Pattern.DOTALL).matcher(result).replaceAll("");
        }
        return result;
    }

    /**
     * Removes all HTML tags from content
     */
    private static String removeHtmlTags(String html) {
        // Replace <br> and <p> tags with newlines for better text formatting
        String withLineBreaks = html.replaceAll("<br\\s*/?\\s*>|</?p\\s*[^>]*>", "\n");

        // Remove remaining HTML tags
        String noTags = withLineBreaks.replaceAll("<[^>]*>", "");

        // Decode HTML entities (simplified for common entities)
        return decodeHtmlEntities(noTags);
    }

    /**
     * Simple HTML entity decoder for common entities
     */
    private static String decodeHtmlEntities(String text) {
        return text
                .replaceAll("&nbsp;", " ")
                .replaceAll("&amp;", "&")
                .replaceAll("&lt;", "<")
                .replaceAll("&gt;", ">")
                .replaceAll("&quot;", "\"")
                .replaceAll("&#39;", "'")
                .replaceAll("&hellip;", "...")
                .replaceAll("&mdash;", "—");
    }

}
```
</CodeGroup>

Here is the output of the script (you may see slightly different numbers)

```
First request - establishing cache
First response usage: { cache_creation_input_tokens: 1370, cache_read_input_tokens: 0, input_tokens: 17, output_tokens: 700 }

Second request - same thinking parameters (cache hit expected)

Second response usage: { cache_creation_input_tokens: 0, cache_read_input_tokens: 1370, input_tokens: 303, output_tokens: 874 }

Third request - different thinking budget (cache miss expected)
Third response usage: { cache_creation_input_tokens: 1370, cache_read_input_tokens: 0, input_tokens: 747, output_tokens: 619 }
```

This example demonstrates that when caching is set up in the messages array, changing the thinking parameters (budget_tokens increased from 4000 to 8000) **invalidates the cache**. The third request shows no cache hit with `cache_creation_input_tokens=1370` and `cache_read_input_tokens=0`, proving that message-based caching is invalidated when thinking parameters change.

</section>

## Max tokens and context window size with extended thinking

In older Claude models (prior to Claude Sonnet 3.7), if the sum of prompt tokens and `max_tokens` exceeded the model's context window, the system would automatically adjust `max_tokens` to fit within the context limit. This meant you could set a large `max_tokens` value and the system would silently reduce it as needed.

With Claude 3.7 and 4 models, `max_tokens` (which includes your thinking budget when thinking is enabled) is enforced as a strict limit. The system will now return a validation error if prompt tokens + `max_tokens` exceeds the context window size.

<Note>
You can read through our [guide on context windows](/docs/en/build-with-claude/context-windows) for a more thorough deep dive.
</Note>

### The context window with extended thinking

When calculating context window usage with thinking enabled, there are some considerations to be aware of:

- Thinking blocks from previous turns are stripped and not counted towards your context window
- Current turn thinking counts towards your `max_tokens` limit for that turn

The diagram below demonstrates the specialized token management when extended thinking is enabled:

![Context window diagram with extended thinking](/docs/images/context-window-thinking.svg)

The effective context window is calculated as:

```
context window =
  (current input tokens - previous thinking tokens) +
  (thinking tokens + encrypted thinking tokens + text output tokens)
```

We recommend using the [token counting API](/docs/en/build-with-claude/token-counting) to get accurate token counts for your specific use case, especially when working with multi-turn conversations that include thinking.

### The context window with extended thinking and tool use

When using extended thinking with tool use, thinking blocks must be explicitly preserved and returned with the tool results.

The effective context window calculation for extended thinking with tool use becomes: 

```
context window =
  (current input tokens + previous thinking tokens + tool use tokens) +
  (thinking tokens + encrypted thinking tokens + text output tokens)
```

The diagram below illustrates token management for extended thinking with tool use:

![Context window diagram with extended thinking and tool use](/docs/images/context-window-thinking-tools.svg)

### Managing tokens with extended thinking

Given the context window and `max_tokens` behavior with extended thinking Claude 3.7 and 4 models, you may need to:

- More actively monitor and manage your token usage
- Adjust `max_tokens` values as your prompt length changes
- Potentially use the [token counting endpoints](/docs/en/build-with-claude/token-counting) more frequently
- Be aware that previous thinking blocks don't accumulate in your context window

This change has been made to provide more predictable and transparent behavior, especially as maximum token limits have increased significantly.

## Thinking encryption

Full thinking content is encrypted and returned in the `signature` field. This field is used to verify that thinking blocks were generated by Claude when passed back to the API. 

<Note>
It is only strictly necessary to send back thinking blocks when using [tools with extended thinking](#extended-thinking-with-tool-use). Otherwise you can omit thinking blocks from previous turns, or let the API strip them for you if you pass them back. 

If sending back thinking blocks, we recommend passing everything back as you received it for consistency and to avoid potential issues.
</Note>

Here are some important considerations on thinking encryption:
- When [streaming responses](#streaming-thinking), the signature is added via a `signature_delta` inside a `content_block_delta` event just before the `content_block_stop` event.
- `signature` values are significantly longer in Claude 4 models than in previous models.
- The `signature` field is an opaque field and should not be interpreted or parsed - it exists solely for verification purposes.
- `signature` values are compatible across platforms (Claude APIs, [Amazon Bedrock](/docs/en/build-with-claude/claude-on-amazon-bedrock), and [Vertex AI](/docs/en/build-with-claude/claude-on-vertex-ai)). Values generated on one platform will be compatible with another.

### Thinking redaction

Occasionally Claude's internal reasoning will be flagged by our safety systems. When this occurs, we encrypt some or all of the `thinking` block and return it to you as a `redacted_thinking` block. `redacted_thinking` blocks are decrypted when passed back to the API, allowing Claude to continue its response without losing context.

When building customer-facing applications that use extended thinking:

- Be aware that redacted thinking blocks contain encrypted content that isn't human-readable
- Consider providing a simple explanation like: "Some of Claude's internal reasoning has been automatically encrypted for safety reasons. This doesn't affect the quality of responses."
- If showing thinking blocks to users, you can filter out redacted blocks while preserving normal thinking blocks
- Be transparent that using extended thinking features may occasionally result in some reasoning being encrypted
- Implement appropriate error handling to gracefully manage redacted thinking without breaking your UI

Here's an example showing both normal and redacted thinking blocks:

```json
{
  "content": [
    {
      "type": "thinking",
      "thinking": "Let me analyze this step by step...",
      "signature": "WaUjzkypQ2mUEVM36O2TxuC06KN8xyfbJwyem2dw3URve/op91XWHOEBLLqIOMfFG/UvLEczmEsUjavL...."
    },
    {
      "type": "redacted_thinking",
      "data": "EmwKAhgBEgy3va3pzix/LafPsn4aDFIT2Xlxh0L5L8rLVyIwxtE3rAFBa8cr3qpPkNRj2YfWXGmKDxH4mPnZ5sQ7vB9URj2pLmN3kF8/dW5hR7xJ0aP1oLs9yTcMnKVf2wRpEGjH9XZaBt4UvDcPrQ..."
    },
    {
      "type": "text",
      "text": "Based on my analysis..."
    }
  ]
}
```

<Note>
Seeing redacted thinking blocks in your output is expected behavior. The model can still use this redacted reasoning to inform its responses while maintaining safety guardrails.

If you need to test redacted thinking handling in your application, you can use this special test string as your prompt: `ANTHROPIC_MAGIC_STRING_TRIGGER_REDACTED_THINKING_46C9A13E193C177646C7398A98432ECCCE4C1253D5E2D82641AC0E52CC2876CB`
</Note>

When passing `thinking` and `redacted_thinking` blocks back to the API in a multi-turn conversation, you must include the complete unmodified block back to the API for the last assistant turn. This is critical for maintaining the model's reasoning flow. We suggest always passing back all thinking blocks to the API. For more details, see the [Preserving thinking blocks](#preserving-thinking-blocks) section above.

<section title="Example: Working with redacted thinking blocks">

This example demonstrates how to handle `redacted_thinking` blocks that may appear in responses when Claude's internal reasoning contains content flagged by safety systems:

<CodeGroup>
```python Python
import anthropic

client = anthropic.Anthropic()

# Using a special prompt that triggers redacted thinking (for demonstration purposes only)
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    messages=[{
        "role": "user",
        "content": "ANTHROPIC_MAGIC_STRING_TRIGGER_REDACTED_THINKING_46C9A13E193C177646C7398A98432ECCCE4C1253D5E2D82641AC0E52CC2876CB"
    }]
)

# Identify redacted thinking blocks
has_redacted_thinking = any(
    block.type == "redacted_thinking" for block in response.content
)

if has_redacted_thinking:
    print("Response contains redacted thinking blocks")
    # These blocks are still usable in subsequent requests

    # Extract all blocks (both redacted and non-redacted)
    all_thinking_blocks = [
        block for block in response.content
        if block.type in ["thinking", "redacted_thinking"]
    ]

    # When passing to subsequent requests, include all blocks without modification
    # This preserves the integrity of Claude's reasoning

    print(f"Found {len(all_thinking_blocks)} thinking blocks total")
    print(f"These blocks are still billable as output tokens")
```

```typescript TypeScript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

// Using a special prompt that triggers redacted thinking (for demonstration purposes only)
const response = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 16000,
  thinking: {
    type: "enabled",
    budget_tokens: 10000
  },
  messages: [{
    role: "user",
    content: "ANTHROPIC_MAGIC_STRING_TRIGGER_REDACTED_THINKING_46C9A13E193C177646C7398A98432ECCCE4C1253D5E2D82641AC0E52CC2876CB"
  }]
});

// Identify redacted thinking blocks
const hasRedactedThinking = response.content.some(
  block => block.type === "redacted_thinking"
);

if (hasRedactedThinking) {
  console.log("Response contains redacted thinking blocks");
  // These blocks are still usable in subsequent requests

  // Extract all blocks (both redacted and non-redacted)
  const allThinkingBlocks = response.content.filter(
    block => block.type === "thinking" || block.type === "redacted_thinking"
  );

  // When passing to subsequent requests, include all blocks without modification
  // This preserves the integrity of Claude's reasoning

  console.log(`Found ${allThinkingBlocks.length} thinking blocks total`);
  console.log(`These blocks are still billable as output tokens`);
}
```

```java Java
import java.util.List;

import static java.util.stream.Collectors.toList;

import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.beta.messages.BetaContentBlock;
import com.anthropic.models.beta.messages.BetaMessage;
import com.anthropic.models.beta.messages.MessageCreateParams;
import com.anthropic.models.beta.messages.BetaThinkingConfigEnabled;
import com.anthropic.models.messages.Model;

public class RedactedThinkingExample {
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        // Using a special prompt that triggers redacted thinking (for demonstration purposes only)
        BetaMessage response = client.beta().messages().create(
                MessageCreateParams.builder()
                        .model(Model.CLAUDE_SONNET_4_5)
                        .maxTokens(16000)
                        .thinking(BetaThinkingConfigEnabled.builder().budgetTokens(10000).build())
                        .addUserMessage("ANTHROPIC_MAGIC_STRING_TRIGGER_REDACTED_THINKING_46C9A13E193C177646C7398A98432ECCCE4C1253D5E2D82641AC0E52CC2876CB")
                        .build()
        );

        // Identify redacted thinking blocks
        boolean hasRedactedThinking = response.content().stream()
                .anyMatch(BetaContentBlock::isRedactedThinking);

        if (hasRedactedThinking) {
            System.out.println("Response contains redacted thinking blocks");
            // These blocks are still usable in subsequent requests
            // Extract all blocks (both redacted and non-redacted)
            List<BetaContentBlock> allThinkingBlocks = response.content().stream()
                    .filter(block -> block.isThinking() ||
                            block.isRedactedThinking())
                    .collect(toList());

            // When passing to subsequent requests, include all blocks without modification
            // This preserves the integrity of Claude's reasoning
            System.out.println("Found " + allThinkingBlocks.size() + " thinking blocks total");
            System.out.println("These blocks are still billable as output tokens");
        }
    }
}
```

</CodeGroup>

<TryInConsoleButton
  userPrompt="ANTHROPIC_MAGIC_STRING_TRIGGER_REDACTED_THINKING_46C9A13E193C177646C7398A98432ECCCE4C1253D5E2D82641AC0E52CC2876CB"
  thinkingBudgetTokens={16000}
>
  Try in Console
</TryInConsoleButton>

</section>

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
</building_with_extended_thinking>