# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a specialized Pine Script development environment for creating TradingView indicators and strategies. The system uses a multi-agent architecture with 7 specialized agents coordinated through Claude Code's Task tool and automated through hooks. The hook system provides deterministic routing - single-word commands and keywords automatically trigger appropriate agent workflows.

## Architecture

### Multi-Agent System

The codebase uses specialized subagents (`.claude/agents/`) that work together:

1. **pine-manager** - Orchestrates complex projects, coordinates other agents, manages scoping process
2. **pine-visualizer** - Breaks down trading ideas into implementable components
3. **pine-developer** - Writes production-quality Pine Script v6 code
4. **pine-debugger** - Troubleshoots issues and adds debugging tools
5. **pine-backtester** - Implements performance metrics and testing
6. **pine-optimizer** - Enhances performance and user experience
7. **pine-publisher** - Prepares scripts for TradingView publication

### Agent Selection Logic

- Simple indicators/strategies → pine-developer (direct implementation)
- Complex multi-step projects → pine-manager (orchestrates all agents)
- Debugging requests → pine-debugger
- Performance optimization → pine-optimizer
- YouTube video analysis → pine-visualizer (automatically runs `python tools/video-analyzer.py "<url>"`)

### Hook System

Active hooks (`.claude/hooks/`) provide deterministic, automated behavior:

- **startup.sh** - Checks onboarding state (`.claude/.onboarding_complete`) and greets user
- **user-prompt-submit.sh** - Automatic routing engine that detects keywords and triggers agents
  - Single-word commands: `start`, `help`, `status`, `examples`, `templates`, `lock`, `unlock`
  - Keyword detection: "debug" → pine-debugger, "optimize" → pine-optimizer, YouTube URLs → pine-visualizer
  - Complexity scoring: Multiple requirements (2+ "and"/"with"/"also") → pine-manager
- **before-write.sh** - Enforces file protection when locked, validates Pine Script files
- **after-edit.sh** - Checks for repainting issues and suggests improvements
- **before-delete.sh** - Prevents deletion of protected files when locked
- **after-rename.sh** - Validates file naming conventions

File protection system:
- **Locked** (`lock` command): Only `/projects/` and state files writable
- **Unlocked** (`unlock` command): All files modifiable (default for development)
- Protection state stored in `.claude/.lock_state`

## Project Structure

```
pinescript-agents/
├── .claude/
│   ├── agents/          # 7 specialized agent prompts (markdown files)
│   └── hooks/           # Bash hooks for deterministic behavior
├── projects/            # USER WORKSPACE - All Pine Scripts go here
│   ├── blank.pine       # Template for new projects (auto-renamed by pine-manager)
│   └── *.pine           # User-created indicators and strategies
├── docs/
│   ├── pinescript-v6/   # Complete Pine Script v6 reference documentation
│   ├── tradingview/     # TradingView platform documentation
│   ├── project-scoping-flow.md  # Standard project scoping process
│   ├── comprehensive-scoping-flow.md  # For unknown patterns
│   └── edge-case-handler.md  # Workarounds for non-standard requests
├── templates/           # Ready-to-use Pine Script templates
│   ├── indicators/      # RSI, MACD, Bollinger Bands, etc.
│   ├── strategies/      # Trend following, mean reversion patterns
│   └── utilities/       # Helper functions (debugging, risk management)
├── examples/            # Example scripts by complexity (simple/intermediate/advanced)
└── tools/               # Python utilities
    └── video-analyzer.py      # Extracts trading strategies from YouTube videos
```

**Key Files:**
- `start` - Interactive bash script for onboarding and menu system
- `analyze-video.sh` - Wrapper script for video analysis
- `run_analysis.py` - Python runner for analysis tasks
- `package.json` - Project metadata

## Key Workflows

### New Project Creation

1. pine-manager renames `projects/blank.pine` → `projects/[project-name].pine` (e.g., `rsi-divergence-indicator.pine`)
2. Creates fresh `blank.pine` for next project
3. Delegates to appropriate agents based on complexity
4. All development happens in `/projects/` directory

### YouTube Video Analysis

When user provides YouTube URL (detected by `user-prompt-submit.sh`):
1. pine-visualizer agent automatically invoked
2. Runs `python tools/video-analyzer.py "<url>"` to extract transcript
3. Identifies trading concepts, indicators, and strategy components
4. Generates Pine Script specification with feasibility assessment
5. Passes to pine-manager for implementation coordination

The `tools/video-analyzer.py` script handles video transcription and initial analysis.

### Project Scoping (pine-manager)

Before implementing, pine-manager follows scoping process:
1. Check if request matches known patterns (standard indicators/strategies)
2. If unknown → `/docs/comprehensive-scoping-flow.md` for deep discovery
3. If edge case (ML, options, exotic data) → `/docs/edge-case-handler.md` for workarounds
4. Ask 5-20 questions based on complexity
5. Generate clear spec with feasibility assessment

## Commands and Natural Language

### Single-Word Commands (auto-handled by hooks)
These commands are intercepted by `user-prompt-submit.sh` hook:
- `start` - Runs interactive `./start` bash script (shows menu and project count)
- `help` - Lists all available commands
- `examples` - Lists scripts from `examples/` directory
- `templates` - Shows quick template options
- `lock` - Enable file protection (only `/projects/` writable)
- `unlock` - Disable protection (default development mode)
- `status` - Shows lock state, protection mode, and project count

### Slash Commands
Available in `.claude/commands/`:
- `/pinescript-mcp` - Invoke pinescript MCP server for documentation lookup and code validation
- `/create-prompt` - Expert prompt engineer for creating optimized agent prompts

### Skills
Available in `.claude/skills/`:
- All 7 pine agents (pine-manager, pine-developer, pine-debugger, etc.) are available as skills
- `create-claude-agent-prompt` - Creates detailed prompts for Claude agents
- `pinescript-mcp` - PineScript MCP integration

### Natural Language Interface
Users can describe requests naturally - hooks automatically route to appropriate agents:
- "Create an RSI divergence indicator with alerts" → pine-manager
- "Debug my script - it's repainting" → pine-debugger
- "Optimize this for faster loading" → pine-optimizer
- "Analyze this video: https://youtube.com/watch?v=..." → pine-visualizer

## Pine Script Critical Constraints

### TradingView Limits
- 500 bars historical lookback max
- 500 plot/hline/fill outputs max
- 64 drawing objects (label/line/box/table)
- 40 `security()` calls max
- Tables limited to 100 cells

### Line Wrapping Rules (Common Error Source)
Pine Script requires continuation lines to be indented MORE than the first line:

```pinescript
// CORRECT
longCondition = ta.crossover(ema50, ema200) and
     rsi < 30 and
     volume > ta.sma(volume, 20)

// WRONG - will cause "end of line without line continuation" error
longCondition = ta.crossover(ema50, ema200) and
rsi < 30 and
volume > ta.sma(volume, 20)
```

Ternary operators MUST stay on one line - cannot be wrapped.

### Scope Restrictions
`plot()` cannot be used inside local scopes (if/for/functions). Use conditional plotting instead:
```pinescript
// WRONG - causes error
if condition
    plot(value)

// CORRECT
plot(condition ? value : na)
```

### Repainting Prevention
- Use `barstate.isconfirmed` for signals
- Set `lookahead=barmerge.lookahead_off` in `request.security()`
- Document any intentional repainting

## Documentation References

Primary docs in `/docs/pinescript-v6/`:
- `language-reference.md` - Core syntax and concepts
- `built-in-functions.md` - Complete function reference
- `core-concepts/execution-model.md` - How Pine Script executes
- `core-concepts/repainting.md` - Avoiding repainting issues
- `quick-reference/limitations.md` - Platform constraints
- `quick-reference/common-patterns.md` - Reusable code patterns

Load these as needed based on the task.

## Quality Standards

All delivered Pine Scripts must have:
- `//@version=6` declaration at top
- Proper error handling for `na` values
- Grouped inputs with tooltips
- No repainting (or clearly documented)
- Efficient calculations (optimized `security()` calls)
- Professional visual presentation
- Clear comments for complex logic

## Development Workflow

### For System Development
- System defaults to **unlocked** mode (all files modifiable)
- Hooks in `.claude/hooks/` are always protected (never writable)
- Agents in `.claude/agents/` are always protected
- Protected paths defined in `.claude/protected-paths.json`

### For User Script Creation
- Use `lock` command to prevent accidental system file modifications
- All Pine Scripts MUST go in `/projects/` directory
- pine-manager automatically renames `projects/blank.pine` → `projects/[project-name].pine`
- A fresh `blank.pine` is created after each project initialization
- Existing projects visible via `status` command

### State Management
- `.claude/.onboarding_complete` - Tracks first-time user status
- `.claude/.lock_state` - Stores protection mode (locked/unlocked)
- `.claude/.state.json` - Session state (if needed)
- `.claude/.last_session` - Last session tracking

### Key Principles
- **Hooks provide deterministic routing** - trust the automation, don't override
- **Projects directory is sacred** - all user Pine Scripts go in `/projects/`
- **blank.pine workflow** - pine-manager renames it for each new project and creates a fresh one
- **Interactive start** - `./start` bash script handles onboarding and provides menu
- **Automatic video analysis** - YouTube URLs trigger `tools/video-analyzer.py` via pine-visualizer

## Working with This Codebase

### When User Asks to Create Something
1. Check if it's a simple request (single indicator/strategy) → use pine-developer directly
2. If complex (multiple requirements, "and"/"with" keywords) → use pine-manager to orchestrate
3. If YouTube URL provided → pine-visualizer extracts requirements first
4. Always start by understanding if similar templates exist in `templates/` or `examples/`

### When User Reports Issues
- "Repainting" / "not updating" → pine-debugger
- "Slow" / "loading forever" → pine-optimizer
- "Errors" / "not working" → pine-debugger
- "Prepare for publishing" → pine-publisher

### File Operations
- Reading templates: `templates/indicators/`, `templates/strategies/`, `templates/utilities/`
- Reading examples: `examples/simple/`, `examples/intermediate/`, `examples/advanced/`
- Reading docs: Start with `docs/pinescript-v6/language-reference.md` and `docs/pinescript-v6/built-in-functions.md`
- Writing scripts: Always to `projects/[descriptive-name].pine`

### Hook Interception
User messages are processed by `user-prompt-submit.sh` BEFORE reaching Claude. Single-word commands (`start`, `help`, etc.) exit immediately with output. For all other prompts, the hook provides routing suggestions but doesn't block - Claude still receives the full prompt.
