# Prompt Writing Best Practices

This documentation provides comprehensive guidance on prompt engineering for Claude 4.x models, with specific emphasis on Sonnet 4.5 and Haiku 4.5. The content has been organized into digestible sections for easy reference.

## Table of Contents

### Part I: Core Prompting Principles

1. **[General Principles](01-general-principles.md)**
   - Be explicit with your instructions
   - Add context to improve performance
   - Be vigilant with examples & details
   - Long-horizon reasoning and state tracking
   - Communication style

2. **[Guidance for Specific Situations - Part 1](02-specific-situations-part1.md)**
   - Balance verbosity
   - Tool usage patterns
   - Control the format of responses
   - Research and information gathering
   - Subagent orchestration

3. **[Guidance for Specific Situations - Part 2](03-specific-situations-part2.md)**
   - Model self-knowledge
   - Leverage thinking & interleaved thinking capabilities
   - Document creation
   - Optimize parallel tool calling
   - Reduce file creation in agentic coding
   - Enhance visual and frontend code generation
   - Avoid focusing on passing tests and hard-coding
   - Minimizing hallucinations in agentic coding

### Part II: Extended Thinking

4. **[Extended Thinking Basics](04-extended-thinking-basics.md)**
   - Supported models
   - How extended thinking works
   - How to use extended thinking
   - Summarized thinking

5. **[Streaming Thinking](05-streaming-thinking.md)**
   - Streaming implementation
   - Code examples (Python, TypeScript, Shell)
   - Example streaming output
   - Performance considerations

6. **[Extended Thinking with Tool Use - Part 1](06-tool-use-part1.md)**
   - Limitations
   - Toggling thinking modes in conversations
   - Common error scenarios
   - Practical guidance
   - Example: Passing thinking blocks with tool results

7. **[Extended Thinking with Tool Use - Part 2](07-tool-use-part2.md)**
   - Continuing conversations with tool results
   - Code examples (Python, TypeScript)
   - Preserving thinking blocks
   - Why preserve thinking blocks

8. **[Interleaved Thinking](08-interleaved-thinking.md)**
   - Overview and capabilities
   - Important considerations
   - Tool use without interleaved thinking
   - Tool use with interleaved thinking

9. **[Extended Thinking with Prompt Caching](09-prompt-caching.md)**
   - Key considerations
   - Thinking block context removal
   - Cache invalidation patterns
   - Understanding thinking block caching behavior
   - System prompt caching

### Part III: Advanced Topics

10. **[Max Tokens, Context Window, and Thinking Encryption](10-context-encryption.md)**
    - Max tokens and context window size
    - The context window with extended thinking
    - The context window with tool use
    - Managing tokens with extended thinking
    - Thinking encryption
    - Thinking redaction

11. **[Model Differences, Pricing, and Best Practices](11-model-differences-pricing.md)**
    - Differences in thinking across model versions
    - Pricing information
    - Working with thinking budgets
    - Performance considerations
    - Feature compatibility
    - Usage guidelines

## Quick Start

If you're new to prompt engineering with Claude 4.x models, we recommend reading the documentation in the following order:

1. Start with **[General Principles](01-general-principles.md)** to understand the fundamentals
2. Review **[Guidance for Specific Situations](02-specific-situations-part1.md)** for practical use cases
3. Explore **[Extended Thinking Basics](04-extended-thinking-basics.md)** to leverage advanced reasoning capabilities
4. Dive into specific topics as needed for your use case

## About This Documentation

This guide is based on the official Anthropic documentation for Claude 4.x models. Each section has been designed to be under 1000 tokens for easy consumption while maintaining comprehensive coverage of the topics.

For the most up-to-date information, please refer to the official Anthropic documentation at [https://docs.anthropic.com](https://docs.anthropic.com).

## Additional Resources

- [Claude API Reference](https://docs.anthropic.com/en/api/messages)
- [Tool Use Documentation](https://docs.anthropic.com/en/agents-and-tools/tool-use/overview)
- [Prompt Caching Guide](https://docs.anthropic.com/en/build-with-claude/prompt-caching)
- [Context Windows Guide](https://docs.anthropic.com/en/build-with-claude/context-windows)
