# PineScript Validation Rules Reference

## Complete Rule Catalog

### Critical Errors (Must Fix)

#### 1. version_declaration
**Rule**: Every PineScript file must start with `//@version=6`

**Severity**: Error

**Detection**: Missing version declaration at file start

**Fix**:
```pine
//@version=6
indicator("My Indicator")
```

**Why it matters**: TradingView requires version declaration to parse code correctly.

---

#### 2. SHORT_TITLE_TOO_LONG
**Rule**: `shorttitle` parameter must be ≤10 characters

**Severity**: Error

**Detection**: Character count exceeds limit

**Example violation**:
```pine
❌ indicator("Test", shorttitle="VERY_LONG_TITLE")  // 15 chars
```

**Fix**:
```pine
✅ indicator("Test", shorttitle="ShortName")  // 9 chars
```

**Why it matters**: TradingView UI has limited space for short titles.

---

#### 3. INVALID_PRECISION
**Rule**: `precision` parameter must be ≤8

**Severity**: Error

**Detection**: Precision value exceeds maximum

**Example violation**:
```pine
❌ indicator("Test", precision=15)
```

**Fix**:
```pine
✅ indicator("Test", precision=8)
```

**Why it matters**: PineScript engine limits decimal precision to 8 places.

---

#### 4. runtime_na_object
**Rule**: Cannot access fields on `na` objects (User-Defined Types)

**Severity**: Error

**Detection**: Pattern `var UDT obj = na; result = obj.field` without na check

**Example violation**:
```pine
❌ type TestType
    float field

var TestType obj = na
result = obj.field  // Runtime error!
```

**Fix**:
```pine
✅ type TestType
    float field

var TestType obj = na
result = na(obj) ? na : obj.field
```

**Why it matters**: Accessing fields on na objects causes runtime errors in TradingView.

---

### Warnings (Should Fix)

#### 5. naming_conventions
**Rule**: Use CamelCase for variables and functions

**Severity**: Warning

**Detection**: snake_case or other naming patterns

**Example violation**:
```pine
❌ my_variable = close
❌ My_Function() =>
```

**Fix**:
```pine
✅ myVariable = close
✅ myFunction() =>
```

**Why it matters**: Official PineScript style guide mandates CamelCase.

---

#### 6. operator_spacing
**Rule**: Spaces required around operators (=, +, -, *, /, etc.)

**Severity**: Warning

**Detection**: Missing spaces around operators

**Example violation**:
```pine
❌ value=close+open
❌ result=price*volume
```

**Fix**:
```pine
✅ value = close + open
✅ result = price * volume
```

**Why it matters**: Improves code readability and maintainability.

---

#### 7. line_length
**Rule**: Lines should not exceed 120 characters

**Severity**: Warning

**Detection**: Line character count exceeds limit

**Example violation**:
```pine
❌ veryLongVariableName = ta.sma(close, 50) + ta.ema(close, 20) + ta.rsi(close, 14) + ta.stoch(close, high, low, 14) + ta.macd(close, 12, 26, 9)
```

**Fix**:
```pine
✅ veryLongVariableName = ta.sma(close, 50) + ta.ema(close, 20) +
     ta.rsi(close, 14) + ta.stoch(close, high, low, 14) +
     ta.macd(close, 12, 26, 9)
```

**Why it matters**: Long lines are difficult to read and maintain.

---

### Suggestions (Consider Fixing)

#### 8. parameter_naming
**Rule**: Function parameters should follow naming conventions

**Severity**: Suggestion

**Detection**: Parameter names that don't follow CamelCase or are unclear

**Example violation**:
```pine
❌ myFunction(input_val, output_res) =>
```

**Fix**:
```pine
✅ myFunction(inputValue, outputResult) =>
```

**Why it matters**: Clear parameter names improve code clarity.

---

#### 9. syntax_compatibility
**Rule**: Code must use PineScript v6 compatible syntax

**Severity**: Error/Warning (depends on severity)

**Detection**: Deprecated functions, old syntax patterns

**Example violation**:
```pine
❌ study("Old syntax")  // v4 function
```

**Fix**:
```pine
✅ indicator("New syntax")  // v6 function
```

**Why it matters**: Deprecated syntax may break in future versions.

---

## Validation Workflow

### 1. Pre-validation Checklist
Before running review, ensure:
- [ ] File has `//@version=6` at top
- [ ] Variables use CamelCase
- [ ] Operators have spacing
- [ ] Lines are ≤120 chars

### 2. Running Validation
```json
{
  "tool": "mcp__pinescript-docs__pinescript_review",
  "parameters": {
    "source_type": "code",
    "code": "your code here"
  }
}
```

### 3. Interpreting Results
Review output structure:
```json
{
  "summary": {
    "total_issues": 5,
    "errors": 2,
    "warnings": 2,
    "suggestions": 1
  },
  "violations": [
    {
      "line": 1,
      "rule": "version_declaration",
      "severity": "error",
      "message": "Missing PineScript version declaration",
      "fix": "Add //@version=6 at the top"
    }
  ]
}
```

**Priority order**:
1. Fix all errors first (code won't run with errors)
2. Address warnings (style guide compliance)
3. Consider suggestions (optional improvements)

### 4. Iterative Fixing
1. Apply fixes for all errors
2. Re-run validation
3. Apply fixes for warnings
4. Re-run validation
5. Review suggestions and decide
6. Final validation should show zero issues

---

## Common Validation Patterns

### Pattern 1: Missing Version
**Issue**: "Missing PineScript version declaration"

**Quick fix**: Add as first line
```pine
//@version=6
```

---

### Pattern 2: Title Issues
**Issue**: "SHORT_TITLE_TOO_LONG" or "INVALID_PRECISION"

**Quick fix**: Adjust parameters
```pine
// Before
indicator("My Indicator", shorttitle="MY_LONG_INDICATOR_NAME", precision=15)

// After
indicator("My Indicator", shorttitle="MyInd", precision=8)
```

---

### Pattern 3: Naming Convention Violations
**Issue**: "naming_conventions" warning for snake_case

**Quick fix**: Convert to CamelCase
```pine
// Before
my_variable = close
my_function() =>
    result = 42

// After
myVariable = close
myFunction() =>
    result = 42
```

---

### Pattern 4: Spacing Issues
**Issue**: "operator_spacing" warning

**Quick fix**: Add spaces around operators
```pine
// Before
value=close+open
result=price*volume

// After
value = close + open
result = price * volume
```

---

### Pattern 5: Runtime NA Object Access
**Issue**: "runtime_na_object" error for UDT field access

**Quick fix**: Add na check before access
```pine
// Before
type MyType
    float value

var MyType obj = na
result = obj.value  // Error!

// After
type MyType
    float value

var MyType obj = na
result = na(obj) ? na : obj.value  // Safe
```

---

## Performance Considerations

### Validation Speed
- **Single file**: <10ms typical
- **Directory (10 files)**: <50ms typical
- **Large codebase (50+ files)**: Use `format=stream`

### Optimization Tips
1. Use severity filtering to focus on errors first:
   ```json
   {
     "severity_filter": "error"
   }
   ```

2. Use streaming for large projects:
   ```json
   {
     "format": "stream"
   }
   ```

3. Validate incrementally during development (not just at end)

---

## Edge Cases and Gotchas

### Edge Case 1: Comments in Version Declaration
```pine
// This works
//@version=6
indicator("Test")

// This does NOT work (comment on same line)
//@version=6 // indicator version
indicator("Test")
```

### Edge Case 2: Multiple na Checks
```pine
// Nested UDTs require nested checks
type Inner
    float value

type Outer
    Inner inner

var Outer obj = na

// Wrong - doesn't check inner
result = na(obj) ? na : obj.inner.value

// Right - checks both levels
result = na(obj) or na(obj.inner) ? na : obj.inner.value
```

### Edge Case 3: Valid Parameter Names
```pine
// These are all valid (no false positives)
myFunction(inputValue, outputResult, dataSource) =>
    result = inputValue + outputResult
```

---

## Troubleshooting Validation

### False Positives
If you believe a rule violation is incorrect:

1. Check PineScript v6 documentation via `pinescript_reference`
2. Verify code runs in TradingView without errors
3. Review specific rule details in this reference
4. If legitimately wrong, file bug report in mcp-server-pinescript repo

### False Negatives
If validation misses an actual error:

1. Verify you're using latest mcp-server-pinescript version
2. Check if error is syntax error (caught by TradingView, not validator)
3. Consider if error is logic error (validator checks style, not logic)
4. Report missing validation rules to mcp-server-pinescript repo

### Performance Issues
If validation is slow:

1. Check server startup logs for "preloaded documentation"
2. Use streaming format for large files
3. Validate smaller chunks during development
4. Restart server if performance degrades

---

## Testing Your Code

### Pre-deployment Checklist
- [ ] All validation errors fixed
- [ ] All validation warnings addressed
- [ ] Code tested in TradingView Pine Editor
- [ ] No runtime errors in TradingView
- [ ] Indicator/strategy behaves as expected
- [ ] Performance acceptable on various timeframes
- [ ] Documentation/comments added for complex logic

### TradingView Testing
1. Copy code to TradingView Pine Editor
2. Check for compilation errors (red underlines)
3. Add to chart and verify visual output
4. Test with different timeframes
5. Test with different symbols
6. Check for runtime errors in console

### Regression Testing
After making changes:
1. Re-run validation: `pinescript_review`
2. Verify no new issues introduced
3. Test in TradingView again
4. Compare output with previous version
