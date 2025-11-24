# pinescript-mcp Skill

Comprehensive skill for developing PineScript v6 indicators and strategies using the mcp-server-pinescript MCP server.

## Purpose

This skill provides:
- MCP server management (checking status, starting server)
- Documentation lookup via `mcp__pinescript-docs__pinescript_reference`
- Code validation via `mcp__pinescript-docs__pinescript_review`
- PineScript v6 best practices and patterns
- Automated code review workflow
- Style guide compliance enforcement

## Structure

```
pinescript/
├── SKILL.md                              # Main skill definition
├── README.md                             # This file
└── references/
    └── validation-rules.md               # Complete validation rule catalog
```

## Usage

### Via Slash Command
```bash
/pinescript-mcp create an RSI indicator with overbought/oversold levels
/pinescript-mcp review this code: [paste code]
/pinescript-mcp look up ta.sma function
```

### Via Skill Invocation
```
Use the pinescript-mcp skill to create a moving average crossover strategy
```

## When This Skill Activates

The skill should be used when:
- User mentions `.pine` files
- User mentions PineScript, TradingView, indicators, or strategies
- User wants to create/edit/review trading indicators or strategies
- User needs PineScript documentation lookup
- User wants to validate PineScript code

## MCP Server Requirements

This skill requires the `mcp-server-pinescript` MCP server:
- **Location**: `/home/mcp-server-pinescript/`
- **Start command**: `cd /home/mcp-server-pinescript && npm start`
- **Tools provided**:
  - `mcp__pinescript-docs__pinescript_reference` - Documentation lookup
  - `mcp__pinescript-docs__pinescript_review` - Code validation
- **Performance**: <15ms response times with preloaded documentation

The skill will automatically check if the server is running and start it if needed.

## Key Features

### 1. MCP Server Management
- Checks server status before operations
- Provides commands to start server if not running
- Verifies server health and documentation preloading

### 2. Documentation Research
- Semantic search with synonym expansion
- Function syntax and parameters lookup
- Style guide and best practices reference
- Code examples and patterns

### 3. Code Validation
- 9+ validation rules for PineScript v6
- Line-by-line error detection
- Severity levels (error, warning, suggestion)
- Actionable fix suggestions
- Directory-wide project review

### 4. Workflow Automation
- Research → Write → Review → Fix → Iterate cycle
- Pre-validation checklists
- Common pattern templates
- Anti-pattern detection

## Validation Rules Covered

1. **version_declaration** - `//@version=6` required
2. **SHORT_TITLE_TOO_LONG** - shorttitle ≤10 chars
3. **INVALID_PRECISION** - precision ≤8
4. **naming_conventions** - CamelCase required
5. **operator_spacing** - Spaces around operators
6. **line_length** - Lines ≤120 chars
7. **runtime_na_object** - Safe na object handling
8. **parameter_naming** - Clear parameter names
9. **syntax_compatibility** - PineScript v6 syntax

See `references/validation-rules.md` for complete details.

## Common Workflows

### Creating New Indicator
1. Research functions via `pinescript_reference`
2. Review style guide conventions
3. Write indicator code following templates
4. Validate with `pinescript_review`
5. Fix issues iteratively
6. Test in TradingView

### Reviewing Existing Code
1. Ensure MCP server running
2. Use `pinescript_review` on file/directory
3. Review violations by severity
4. Apply suggested fixes
5. Re-validate until clean
6. Test in TradingView

### Learning PineScript
1. Look up functions via `pinescript_reference`
2. Study code examples in skill
3. Practice with templates
4. Validate practice code
5. Learn from validation feedback

## Progressive Disclosure

The skill uses progressive disclosure:
- **SKILL.md**: Core workflows, common patterns, quick reference
- **references/validation-rules.md**: Deep-dive into all validation rules with examples

This keeps context usage efficient while providing comprehensive guidance when needed.

## Performance Characteristics

- **Documentation lookup**: 5-15ms typical
- **Code review**: 3-10ms for single file
- **Directory review**: <50ms for 10 files
- **Server startup**: ~1 second (one-time cost)
- **Memory usage**: ~12MB for server

## Success Criteria

Code is production-ready when:
- ✅ Zero validation errors
- ✅ Zero validation warnings
- ✅ PineScript v6 syntax compliance
- ✅ Style guide adherence
- ✅ No runtime errors in TradingView
- ✅ Indicator/strategy behaves as expected

## Troubleshooting

### Server Won't Start
```bash
# Check if already running
ps aux | grep mcp-server-pinescript

# Kill existing process if needed
pkill -f mcp-server-pinescript

# Start fresh
cd /home/mcp-server-pinescript && npm start
```

### Documentation Not Available
1. Verify server shows "preloaded documentation" message
2. Check `/home/mcp-server-pinescript/docs/processed/` exists
3. Restart server if needed

### Validation False Positives
1. Check against PineScript v6 documentation
2. Test code in TradingView editor
3. Review specific rule in validation-rules.md
4. File bug report if legitimately wrong

## Related Skills

This skill complements:
- `technical-analysis` - For analyzing market data
- `create-agent-skills` - For extending the skill itself
- General trading and quantitative analysis skills

## Maintenance

To update this skill:
1. Use `/create-agent-skill` to modify
2. Update validation rules as mcp-server-pinescript evolves
3. Add new code examples and patterns
4. Keep templates current with TradingView best practices

## External Resources

- **MCP Server Repo**: https://github.com/iamrichardD/mcp-server-pinescript
- **Local Docs**: `/home/mcp-server-pinescript/README.md`
- **User Guide**: `/home/mcp-server-pinescript/USER-GUIDE.md`
- **Agent Config**: `/home/mcp-server-pinescript/AGENT.md`
