# Guidance for Specific Situations - Part 2

## Model self-knowledge

If you would like Claude to identify itself correctly in your application or use specific API strings:

```text Sample prompt for model identity
The assistant is Claude, created by Anthropic. The current model is Claude Sonnet 4.5.
```

For LLM-powered apps that need to specify model strings:

```text Sample prompt for model string
When an LLM is needed, please default to Claude Sonnet 4.5 unless the user requests otherwise. The exact model string for Claude Sonnet 4.5 is claude-sonnet-4-5-20250929.
```

## Leverage thinking & interleaved thinking capabilities

Claude 4.x models offer thinking capabilities that can be especially helpful for tasks involving reflection after tool use or complex multi-step reasoning. You can guide its initial or interleaved thinking for better results.

```text Example prompt
After receiving tool results, carefully reflect on their quality and determine optimal next steps before proceeding. Use your thinking to plan and iterate based on this new information, and then take the best next action.
```

<Info>
  For more information on thinking capabilities, see the Extended Thinking section.
</Info>

## Document creation

Claude 4.5 models excel at creating presentations, animations, and visual documents. These models match or exceed Claude Opus 4.1 in this domain, with impressive creative flair and stronger instruction following. The models produce polished, usable output on the first try in most cases.

For best results with document creation:

```text Sample prompt
Create a professional presentation on [topic]. Include thoughtful design elements, visual hierarchy, and engaging animations where appropriate.
```

## Optimize parallel tool calling

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

## Reduce file creation in agentic coding

Claude 4.x models may sometimes create new files for testing and iteration purposes, particularly when working with code. This approach allows Claude to use files, especially python scripts, as a 'temporary scratchpad' before saving its final output. Using temporary files can improve outcomes particularly for agentic coding use cases.

If you'd prefer to minimize net new file creation, you can instruct Claude to clean up after itself:

```text Sample prompt
If you create any temporary new files, scripts, or helper files for iteration, clean up these files by removing them at the end of the task.
```

## Enhance visual and frontend code generation

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

## Avoid focusing on passing tests and hard-coding

Claude 4.x models can sometimes focus too heavily on making tests pass at the expense of more general solutions, or may use workarounds like helper scripts for complex refactoring instead of using standard tools directly. To prevent this behavior and ensure robust, generalizable solutions:

```text Sample prompt
Please write a high-quality, general-purpose solution using the standard tools available. Do not create helper scripts or workarounds to accomplish the task more efficiently. Implement a solution that works correctly for all valid inputs, not just the test cases. Do not hard-code values or create solutions that only work for specific test inputs. Instead, implement the actual logic that solves the problem generally.

Focus on understanding the problem requirements and implementing the correct algorithm. Tests are there to verify correctness, not to define the solution. Provide a principled implementation that follows best practices and software design principles.

If the task is unreasonable or infeasible, or if any of the tests are incorrect, please inform me rather than working around them. The solution should be robust, maintainable, and extendable.
```

## Minimizing hallucinations in agentic coding

Claude 4.x models are less prone to hallucinations and give more accurate, grounded, intelligent answers based on the code. To encourage this behavior even more and minimize hallucinations:

```text Sample prompt
<investigate_before_answering>
Never speculate about code you have not opened. If the user references a specific file, you MUST read the file before answering. Make sure to investigate and read relevant files BEFORE answering questions about the codebase. Never make any claims about code before investigating unless you are certain of the correct answer - give grounded and hallucination-free answers.
</investigate_before_answering>
```
