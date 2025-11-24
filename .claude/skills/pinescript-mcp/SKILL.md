---
name: pinescript-mcp
description: Create, edit, and review PineScript v6 code using the mcp-server-pinescript MCP server. Provides documentation lookup via pinescript_reference and code validation via pinescript_review. Use when working with .pine files, writing TradingView indicators/strategies, or when user mentions PineScript development.
---

<objective>
Develop PineScript v6 indicators and strategies with real-time documentation access and automated code review using the mcp-server-pinescript MCP server. Ensures code quality, style guide compliance, and correct syntax before deployment to TradingView.
</objective>

<quick_start>
<basic_workflow>
1. **Ensure MCP server is running**: Check if mcp-server-pinescript is active
2. **Look up functions**: Use `mcp__pinescript-docs__pinescript_reference` for documentation
3. **Write code**: Create .pine files with PineScript v6 syntax
4. **Review code**: Use `mcp__pinescript-docs__pinescript_review` for validation
5. **Fix issues**: Apply suggested fixes from review results
6. **Iterate**: Repeat review until all issues resolved
</basic_workflow>

<example>
```pine
//@version=6
indicator("RSI Momentum", shorttitle="RSI", overlay=false)

// Input parameters
rsiLength = input.int(14, "RSI Length", minval=1)
overbought = input.int(70, "Overbought Level", minval=50, maxval=100)
oversold = input.int(30, "Oversold Level", minval=0, maxval=50)

// Calculate RSI
rsiValue = ta.rsi(close, rsiLength)

// Plot indicator
plot(rsiValue, "RSI", color=color.blue)
hline(overbought, "Overbought", color=color.red)
hline(oversold, "Oversold", color=color.green)
```
</example>
</quick_start>

<mcp_server_management>
<checking_server_status>
The mcp-server-pinescript is installed at `/home/mcp-server-pinescript/`.

**To verify if running**:
```bash
ps aux | grep "mcp-server-pinescript"
```

If you see a node process with the path, server is running. Otherwise, start it.
</checking_server_status>

<starting_server>
If server is not running, start it:

```bash
cd /home/mcp-server-pinescript && npm start
```

Expected output:
```
PineScript MCP Server ready with preloaded documentation!
```

**Performance**: Server preloads 555KB documentation in ~1 second for <15ms response times.
</starting_server>

<server_requirements>
- Node.js 18+ required
- ~12MB RAM for server operation
- Server must be running before using MCP tools
- Documentation is preloaded in memory (no file I/O during requests)
</server_requirements>
</mcp_server_management>

<workflow>
<step_1>
**Check server availability**: Verify mcp-server-pinescript is running. If not, start it using the commands in the mcp_server_management section above.
</step_1>

<step_2>
**Research functions**: Before writing code, use `mcp__pinescript-docs__pinescript_reference` to look up:
- Function syntax and parameters
- Style guide conventions
- Code examples and patterns
- Best practices for your use case

Query examples:
- "ta.sma" - Look up simple moving average function
- "array functions" - Find array manipulation functions
- "strategy.entry" - Research strategy order placement
- "naming conventions" - Check style guide rules
</step_2>

<step_3>
**Write PineScript code**: Create .pine files following v6 standards:

Required elements:
- `//@version=6` declaration at top (mandatory)
- `indicator()` or `strategy()` declaration
- CamelCase naming for variables and functions
- Proper spacing around operators
- Comments for complex logic

Common patterns:
- Input parameters: `input.int()`, `input.float()`, `input.bool()`
- Technical indicators: `ta.sma()`, `ta.rsi()`, `ta.macd()`
- Plotting: `plot()`, `hline()`, `plotshape()`
- Conditional logic: `if/else`, `switch`, ternary operators
</step_3>

<step_4>
**Review code**: Use `mcp__pinescript-docs__pinescript_review` to validate:

**For inline code**:
```json
{
  "tool": "mcp__pinescript-docs__pinescript_review",
  "parameters": {
    "source_type": "code",
    "code": "your PineScript code here"
  }
}
```

**For single file**:
```json
{
  "tool": "mcp__pinescript-docs__pinescript_review",
  "parameters": {
    "source_type": "file",
    "file_path": "./indicators/my_indicator.pine"
  }
}
```

**For entire directory**:
```json
{
  "tool": "mcp__pinescript-docs__pinescript_review",
  "parameters": {
    "source_type": "directory",
    "directory_path": "./strategies"
  }
}
```
</step_4>

<step_5>
**Fix validation issues**: Apply suggested fixes from review results.

Common validation rules:
- `version_declaration` - Must have `//@version=6`
- `SHORT_TITLE_TOO_LONG` - shorttitle must be ≤10 chars
- `INVALID_PRECISION` - precision must be ≤8
- `naming_conventions` - Use CamelCase for variables
- `operator_spacing` - Spaces around operators (=, +, -, etc.)
- `line_length` - Lines must be ≤120 chars

Review output includes:
- Severity level (error, warning, suggestion)
- Line number and rule violated
- Specific fix suggestion
- Code examples where applicable
</step_5>

<step_6>
**Iterate until clean**: Repeat review → fix → review cycle until zero issues remain.

Target: Zero errors, zero warnings for production-ready code.
</step_6>
</workflow>

<advanced_features>
<directory_review>
**Review entire projects**: Check all .pine files in a directory tree.

```json
{
  "tool": "mcp__pinescript-docs__pinescript_review",
  "parameters": {
    "source_type": "directory",
    "directory_path": "./trading-bots",
    "severity_filter": "error",
    "format": "markdown"
  }
}
```

**Parameters**:
- `severity_filter`: "error", "warning", or "suggestion" to focus on specific issues
- `format`: "json" (default), "markdown" (human-readable), or "stream" (large projects)

**Use streaming for large projects** (>10 files):
```json
{
  "format": "stream"
}
```

Benefits:
- Real-time feedback as files are processed
- No token limits for large codebases
- Progressive results delivery
</directory_review>

<semantic_search>
**Enhanced documentation search**: The reference tool supports:

- Synonym expansion (e.g., "moving average" finds "ta.sma", "ta.ema")
- Partial matching (e.g., "array" finds all array functions)
- Technical term recognition
- Streaming for large result sets

Search strategies:
- Start broad, narrow down: "arrays" → "array.push"
- Use function prefixes: "ta." for technical analysis, "strategy." for strategies
- Include examples: Request code examples in query
</semantic_search>

<output_formats>
**JSON format** (default):
```json
{
  "summary": {
    "total_issues": 2,
    "errors": 1,
    "warnings": 0,
    "suggestions": 1
  },
  "violations": [
    {
      "line": 1,
      "rule": "version_declaration",
      "severity": "error",
      "message": "Missing PineScript version declaration"
    }
  ]
}
```

**Markdown format** (human-readable):
- Error count with severity indicators
- Line-by-line issue descriptions
- Suggested fixes for each violation
- Example: "Line 1: Missing PineScript version declaration - Add //@version=6 at the top"

**Streaming format** (large files/directories):
Progressive JSON chunks delivered as processing occurs.
</output_formats>

<validation_rules>
The review tool checks 9+ validation rules:

1. **version_declaration** - `//@version=6` required at top
2. **SHORT_TITLE_TOO_LONG** - `shorttitle` parameter ≤10 chars
3. **INVALID_PRECISION** - `precision` parameter ≤8
4. **naming_conventions** - CamelCase for variables/functions
5. **operator_spacing** - Spaces around operators
6. **line_length** - Maximum 120 characters per line
7. **runtime_na_object** - Detects runtime-breaking `na` object access
8. **parameter_naming** - Validates function parameter names
9. **syntax_compatibility** - PineScript v6 syntax validation

All rules have:
- Severity level (error/warning/suggestion)
- Specific line/column information
- Actionable fix suggestions
- Code examples where helpful
</validation_rules>
</advanced_features>

<common_patterns>
<indicator_template>
```pine
//@version=6
indicator("Indicator Name", shorttitle="Short", overlay=false)

// Inputs
length = input.int(20, "Length", minval=1, maxval=500)
source = input.source(close, "Source")

// Calculations
value = ta.sma(source, length)

// Plotting
plot(value, "Value", color=color.blue, linewidth=2)
```
</indicator_template>

<strategy_template>
```pine
//@version=6
strategy("Strategy Name", shorttitle="Strat", overlay=true)

// Inputs
fastLength = input.int(12, "Fast Length", minval=1)
slowLength = input.int(26, "Slow Length", minval=1)

// Indicators
fastMA = ta.sma(close, fastLength)
slowMA = ta.sma(close, slowLength)

// Entry conditions
longCondition = ta.crossover(fastMA, slowMA)
shortCondition = ta.crossunder(fastMA, slowMA)

// Execute trades
if longCondition
    strategy.entry("Long", strategy.long)
if shortCondition
    strategy.entry("Short", strategy.short)

// Plotting
plot(fastMA, "Fast MA", color=color.green)
plot(slowMA, "Slow MA", color=color.red)
```
</strategy_template>

<array_usage>
```pine
//@version=6
indicator("Array Example")

// Create array
var myArray = array.new_float(0)

// Add elements
array.push(myArray, close)

// Access elements
if array.size(myArray) > 0
    lastValue = array.get(myArray, array.size(myArray) - 1)
    plot(lastValue)
```
</array_usage>

<conditional_structures>
```pine
//@version=6
indicator("Conditionals")

// If-else
rsiValue = ta.rsi(close, 14)
signalColor = if rsiValue > 70
    color.red
else if rsiValue < 30
    color.green
else
    color.gray

// Ternary operator
isOverbought = rsiValue > 70 ? true : false

// Switch statement
timeframe = switch
    timeframe.period == "1" => "1 Minute"
    timeframe.period == "5" => "5 Minutes"
    timeframe.period == "60" => "1 Hour"
    => "Other"

plot(rsiValue, color=signalColor)
```
</conditional_structures>

<json_string_building>
**Best practices for alert messages and JSON construction**:

```pine
//@version=6
strategy("JSON Alert Example")

// ❌ AVOID: Long inline concatenation with complex expressions
buildAlertBad(action, price, stopLoss) =>
    '{"symbol":"' + syminfo.ticker + '","action":"' + action +
     '","price":' + str.tostring(price) +
     '","stop":' + str.tostring(price > close ? price - 10 : price + 10) +
     '","target":' + str.tostring(price > close ? price + 20 : price - 20) + '}'

// ✅ GOOD: Pre-compute complex values, use compact JSON format
buildAlertGood(action, price, stopLoss) =>
    // Pre-compute complex expressions
    stopPrice = price > close ? price - 10 : price + 10
    targetPrice = price > close ? price + 20 : price - 20

    // Build JSON with no spaces after colons (valid JSON, more compact)
    json = '{"symbol":"' + syminfo.ticker + '","action":"' + action +
     ',"price":' + str.tostring(price) +
     ',"stop":' + str.tostring(stopPrice) +
     ',"target":' + str.tostring(targetPrice) + '}'
    json

// ✅ BETTER: For very large JSON, split into logical sections
buildAlertComplex(action, price, stopLoss, qty, notes) =>
    // Pre-compute all values
    stopPrice = price > close ? price - 10 : price + 10
    targetPrice = price > close ? price + 20 : price - 20
    timestamp = time

    // Build in sections
    basicInfo = '{"symbol":"' + syminfo.ticker + '","action":"' + action + '"'
    priceInfo = ',"price":' + str.tostring(price) + ',"stop":' + str.tostring(stopPrice)
    extraInfo = ',"target":' + str.tostring(targetPrice) +
     ',"qty":' + str.tostring(qty) +
     ',"time":' + str.tostring(timestamp) +
     ',"notes":"' + notes + '"}'

    // Combine sections
    basicInfo + priceInfo + extraInfo

// Usage in strategy
if ta.crossover(ta.sma(close, 10), ta.sma(close, 20))
    alertMsg = buildAlertGood("BUY", close, close * 0.98)
    strategy.entry("Long", strategy.long, alert_message=alertMsg)
```

**Key principles**:
1. Pre-compute ternary expressions before string building
2. Remove spaces after colons in JSON (still valid, saves characters)
3. Use shorter variable names in string builders
4. Split very long strings into logical sections
5. Keep total concatenated length under ~600 characters per assignment
</json_string_building>
</common_patterns>

<anti_patterns>
<avoid_these>
1. **Missing version declaration**: Always start with `//@version=6`

   ```pine
   ❌ indicator("Test")
   ✅ //@version=6
      indicator("Test")
   ```

2. **Long shorttitles**: Keep ≤10 characters

   ```pine
   ❌ indicator("Test", shorttitle="VERY_LONG_TITLE")
   ✅ indicator("Test", shorttitle="Test")
   ```

3. **Invalid precision**: Maximum 8

   ```pine
   ❌ indicator("Test", precision=15)
   ✅ indicator("Test", precision=8)
   ```

4. **snake_case naming**: Use CamelCase

   ```pine
   ❌ my_variable = close
   ✅ myVariable = close
   ```

5. **No operator spacing**: Add spaces

   ```pine
   ❌ value=close+open
   ✅ value = close + open
   ```

6. **Runtime NA object access**: Check for na before accessing UDT fields

   ```pine
   ❌ var TestType obj = na
      result = obj.field  // Runtime error!

   ✅ var TestType obj = na
      result = na(obj) ? na : obj.field
   ```

7. **Hex colors without wrapper**: Must use `color.new()` for hex colors in function parameters

   ```pine
   ❌ plotshape(signal, "Signal", color=#ff0000)
   ✅ plotshape(signal, "Signal", color=color.new(#ff0000, 0))

   // Note: 8-digit hex with alpha channel works directly in bgcolor()
   ✅ bgcolor(condition ? #ff000020 : na)
   ```

8. **Invalid time() function call**: Use `time` built-in variable, not `time("")`

   ```pine
   ❌ timestamp = time("")        // Invalid empty string
   ❌ timestamp = time()          // Empty call may cause issues
   ✅ timestamp = time            // Built-in variable (no parentheses)
   ✅ timestamp = time("America/New_York")  // Valid timezone string
   ```

9. **Overly long string concatenations**: Break up complex JSON/string builders

   ```pine
   ❌ // Very long multi-line concatenation (>700 chars can cause issues)
   json = '{"key1":"' + val1 + '","key2":"' + val2 + '","key3":"' + val3 +
          '","key4":"' + val4 + '","key5":"' + val5 + ... // 20+ more fields

   ✅ // Pre-compute complex expressions, use compact JSON (no spaces after colons)
   complexValue = condition ? longCalculation1 : longCalculation2
   json = '{"key1":"' + val1 + '","key2":"' + val2 +
    ',"key3":"' + val3 + ',"key4":' + str.tostring(complexValue) + '}'

   ✅ // Or split into multiple smaller string builds
   part1 = '{"key1":"' + val1 + '","key2":"' + val2 + '"'
   part2 = ',"key3":"' + val3 + '","key4":"' + val4 + '"}'
   json = part1 + part2
   ```

10. **Variable name shadowing**: Avoid names that conflict with built-in constants

    ```pine
    ❌ var int long = na       // Shadows strategy.long constant
    ❌ var int short = na      // Shadows strategy.short constant

    ✅ var int longPos = na    // Clear, no conflicts
    ✅ var int shortPos = na   // Clear, no conflicts
    ```
</avoid_these>
</anti_patterns>

<troubleshooting>
<server_issues>
**Problem**: "Documentation not yet available" error

**Solution**:
1. Check if server is running: `ps aux | grep mcp-server-pinescript`
2. If not running, start server: `cd /home/mcp-server-pinescript && npm start`
3. Verify startup message shows "preloaded documentation"
4. If files missing, check `/home/mcp-server-pinescript/docs/processed/` directory
</server_issues>

<compilation_errors>
**Problem**: "Mismatched input 'end of line without line continuation' expecting ')'"

**Common causes and solutions**:

1. **Hex colors without color.new() wrapper**:
   - **Error location**: Usually points to line with `color=#RRGGBB` in function parameters
   - **How to find**: Search for `color=#` in plotshape(), plot(), or similar functions
   - **Fix**: Wrap in `color.new(#RRGGBB, transparency)`
   ```pine
   ❌ plotshape(signal, "Label", color=#ff0000)
   ✅ plotshape(signal, "Label", color=color.new(#ff0000, 0))
   ```

2. **String concatenation too long**:
   - **Error location**: Points to a line in multi-line string concatenation, often with high column number (>500)
   - **How to diagnose**: Error shows column number representing cumulative string length
   - **Fix**: Pre-compute complex expressions, remove JSON whitespace, or split into parts
   ```pine
   ❌ // Multi-line string with 700+ characters
   json = '{"symbol": "' + symbol + '", "action": "' + action + ... // many more fields

   ✅ // Pre-compute ternary, compact JSON (no spaces after colons)
   tpPrice = condition ? value1 : value2
   json = '{"symbol":"' + symbol + '","action":"' + action +
    ',"price":' + str.tostring(tpPrice) + '}'
   ```

3. **Invalid time() function call**:
   - **Error location**: Line with `time("")` or similar
   - **How to find**: Search for `time(` in code
   - **Fix**: Use `time` built-in variable (no parentheses) or valid timezone string
   ```pine
   ❌ timestamp = time("")
   ✅ timestamp = time
   ✅ timestamp = time("America/New_York")
   ```

**Debugging strategy**:
1. Note the exact line and column number from error
2. If column >500, likely a string concatenation issue
3. Check that line for hex colors, time() calls, or long strings
4. Search entire file for patterns: `color=#`, `time("")`, long concatenations
5. Fix all instances, not just the first one
</compilation_errors>

<search_no_results>
**Problem**: Documentation search returns no results

**Solutions**:
- Try broader terms: "array" instead of "array.push"
- Check spelling and syntax
- Use function names without parameters: "ta.sma" not "ta.sma(close, 14)"
- Try related terms: "moving average" finds "ta.sma", "ta.ema"
</search_no_results>

<validation_false_positives>
**Problem**: Review shows false positive errors

**Solutions**:
1. Verify you're using PineScript v6 syntax
2. Check if code matches official style guide
3. Review specific rule documentation
4. If legitimate false positive, file bug report in mcp-server-pinescript repo
</validation_false_positives>

<runtime_errors>
**Problem**: Code compiles but fails at runtime

**Common causes**:

1. **Variable shadowing**:
   - Variables named `long` or `short` conflict with strategy constants
   - **Fix**: Use `longPos`, `shortPos`, or similar descriptive names

2. **NA object access**:
   - Accessing fields of UDT (User-Defined Type) that is `na`
   - **Fix**: Check `na(obj)` before accessing `obj.field`

3. **Array index out of bounds**:
   - Accessing array elements beyond size
   - **Fix**: Check `array.size()` before accessing indices

4. **Division by zero**:
   - Mathematical operations with zero denominators
   - **Fix**: Add conditional checks before division
</runtime_errors>

<slow_performance>
**Problem**: Responses taking >50ms

**Solutions**:
1. Verify "preloaded documentation" in server startup logs
2. Use `format=stream` for large files (>1000 lines)
3. Check system resources (server needs ~12MB RAM)
4. Restart server if performance degrades over time
</slow_performance>
</troubleshooting>

<reference_guides>
**Server documentation**:
- Installation and setup: `/home/mcp-server-pinescript/README.md`
- User integration guide: `/home/mcp-server-pinescript/USER-GUIDE.md`
- Agent configuration: `/home/mcp-server-pinescript/AGENT.md`

**PineScript resources**:
- Use `mcp__pinescript-docs__pinescript_reference` for official docs
- Style guide: Query "style guide" via reference tool
- Function reference: Query specific function names
- Code examples: Request examples in reference queries

**Performance documentation**:
- 4,277x faster data access via memory preloading
- <15ms response times for typical queries
- Sub-2ms test execution for validation rules
- Streaming support for large codebases
</reference_guides>

<success_criteria>
**Code quality achieved when**:
- ✅ Zero errors from `pinescript_review`
- ✅ Zero warnings from `pinescript_review`
- ✅ All suggestions addressed or consciously deferred
- ✅ Code follows PineScript v6 syntax standards
- ✅ Style guide compliance (CamelCase, spacing, line length)
- ✅ Version declaration present (`//@version=6`)
- ✅ Code tested in TradingView editor (no runtime errors)

**Documentation research complete when**:
- ✅ Function syntax and parameters understood
- ✅ Code examples reviewed
- ✅ Edge cases and limitations documented
- ✅ Best practices identified for use case

**MCP server operational when**:
- ✅ Server running with "preloaded documentation" message
- ✅ Response times <15ms for typical queries
- ✅ Both tools accessible: `pinescript_reference` and `pinescript_review`
- ✅ No connection errors or timeout issues
</success_criteria>
