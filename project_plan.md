# CSV Analysis Agent - Project Plan

## Overview

This project implements a CSV data analysis agent using the Claude Agent SDK. The agent can iteratively analyze CSV files, execute Python code, observe results, and refine its analysis until it produces comprehensive insights.

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                               │
│  (Entry point: user prompt + CSV file path configuration)   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   csv_analysis_agent.py                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              ClaudeSDKClient                         │    │
│  │  • System prompt for data analysis                   │    │
│  │  • Allowed tools: Bash, Read, Write, Glob            │    │
│  │  • Permission mode: acceptEdits                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                              │                               │
│                     Agentic Loop                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  1. Read CSV file                                    │    │
│  │  2. Execute Python code (via Bash)                   │    │
│  │  3. Observe output                                   │    │
│  │  4. Decide: more analysis or complete?               │    │
│  │  5. Repeat until satisfied                           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      output/                                 │
│  • analysis_report.txt (final conclusions)                  │
│  • Any generated visualizations (optional)                  │
└─────────────────────────────────────────────────────────────┘
```

### Component Breakdown

| Component | File | Responsibility |
|-----------|------|----------------|
| **Entry Point** | `main.py` | Configures CSV path, user prompt, and invokes the agent |
| **Agent Module** | `csv_analysis_agent.py` | Core agent logic using Claude SDK |
| **Output** | `output/` directory | Stores analysis results and conclusions |

### Agentic Loop Flow

The agent operates in an iterative loop powered by the Claude Agent SDK:

```
┌──────────────┐
│ User Prompt  │
│ + CSV Path   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│           AGENTIC LOOP                        │
│  ┌─────────────────────────────────────────┐ │
│  │ 1. UNDERSTAND                            │ │
│  │    • Read CSV structure                  │ │
│  │    • Identify columns, types, shape      │ │
│  └───────────────┬─────────────────────────┘ │
│                  ▼                            │
│  ┌─────────────────────────────────────────┐ │
│  │ 2. ANALYZE                               │ │
│  │    • Execute Python code (pandas, etc.)  │ │
│  │    • Generate statistics, visualizations │ │
│  └───────────────┬─────────────────────────┘ │
│                  ▼                            │
│  ┌─────────────────────────────────────────┐ │
│  │ 3. OBSERVE                               │ │
│  │    • Check code output                   │ │
│  │    • Identify errors or gaps             │ │
│  └───────────────┬─────────────────────────┘ │
│                  ▼                            │
│  ┌─────────────────────────────────────────┐ │
│  │ 4. DECIDE                                │ │
│  │    • Need more analysis? → Loop back     │ │
│  │    • Analysis complete? → Write report   │ │
│  └───────────────┬─────────────────────────┘ │
└──────────────────┼───────────────────────────┘
                   ▼
         ┌─────────────────┐
         │ Write Output    │
         │ analysis.txt    │
         └─────────────────┘
```

---

## Requirements

### Python Version
- Python 3.12+ (as specified in pyproject.toml)

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `claude-agent-sdk` | latest | Core SDK for building the agent |
| `anthropic` | >=0.75.0 | Anthropic API client (already in project) |
| `pandas` | >=2.3.3 | CSV parsing and data manipulation (already in project) |
| `numpy` | latest | Numerical operations |
| `matplotlib` | latest | Data visualization (optional but useful) |
| `seaborn` | latest | Statistical visualizations (optional) |

### API Requirements
- **ANTHROPIC_API_KEY**: Environment variable with valid Anthropic API key

### Directory Structure

```
claude_sdk_testing/
├── main.py                     # Entry point with user prompt and CSV path
├── csv_analysis_agent.py       # Agent implementation
├── project_plan.md             # This document
├── implementation.md           # Step-by-step implementation guide
├── pyproject.toml              # Python dependencies
├── data/                       # Input CSV files directory
│   └── sample.csv              # Example input file
├── output/                     # Analysis results
│   └── analysis_report.txt     # Generated analysis report
└── README.md                   # Project documentation
```

---

## Implementation Strategy

### Strategy 1: Simple Query API (Recommended for MVP)

**Approach**: Use the `query()` function with built-in tools.

**Pros**:
- Minimal code required
- Quick to implement
- Uses proven built-in tools (Bash, Read, Write)

**Cons**:
- Less customization
- Limited control over the agentic loop

**Implementation**:
```python
from claude_agent_sdk import query, ClaudeAgentOptions

async def analyze_csv(csv_path: str, user_prompt: str) -> str:
    options = ClaudeAgentOptions(
        allowed_tools=["Bash", "Read", "Write", "Glob"],
        permission_mode="acceptEdits"
    )

    full_prompt = f"""
    Analyze the CSV file at: {csv_path}

    User request: {user_prompt}

    Instructions:
    1. Read and understand the CSV structure
    2. Use Python with pandas to analyze the data
    3. Answer the user's question with data-driven insights
    4. Save your conclusions to output/analysis_report.txt
    """

    async for message in query(prompt=full_prompt, options=options):
        # Process streaming messages
        pass
```

### Strategy 2: Full Client API (Recommended for Production)

**Approach**: Use `ClaudeSDKClient` for full control over the agent.

**Pros**:
- Full control over agent behavior
- Custom system prompts
- Better error handling
- Hooks for validation and logging

**Cons**:
- More code to write
- Slightly more complex

**Implementation**:
```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def analyze_csv(csv_path: str, user_prompt: str) -> str:
    options = ClaudeAgentOptions(
        system_prompt=DATA_ANALYSIS_SYSTEM_PROMPT,
        allowed_tools=["Bash", "Read", "Write", "Glob"],
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(f"Analyze {csv_path}: {user_prompt}")
        async for msg in client.receive_response():
            # Handle messages
            pass
```

### Strategy 3: Custom Tools API (Advanced)

**Approach**: Define custom tools using `@tool` decorator for specialized operations.

**Pros**:
- Domain-specific operations
- More efficient for repeated tasks
- Better encapsulation

**Cons**:
- More development overhead
- Requires MCP server setup

**Selected Strategy**: **Strategy 2 (Full Client API)** with option to add custom tools later.

---

## Key Design Decisions

### 1. Code Execution via Bash Tool

The agent will execute Python code through the Bash tool:
```python
# Agent internally runs:
Bash("python -c 'import pandas as pd; df = pd.read_csv(\"data.csv\"); print(df.describe())'")
```

This allows the agent to:
- Run any Python code dynamically
- Install additional packages if needed
- Handle complex multi-line scripts

### 2. System Prompt Design

The system prompt guides the agent's analytical behavior:

```python
SYSTEM_PROMPT = """You are an expert data analyst. When analyzing CSV files:

1. EXPLORATION: First load and inspect the data structure
   - Check shape, columns, data types
   - Identify missing values

2. ANALYSIS: Based on the user's question, perform appropriate analysis
   - Use pandas for data manipulation
   - Calculate relevant statistics
   - Look for patterns and trends

3. ITERATION: If initial analysis is insufficient:
   - Run additional queries
   - Create visualizations if helpful
   - Dig deeper into interesting findings

4. CONCLUSION: Provide clear, actionable insights
   - Answer the user's specific question
   - Support conclusions with data
   - Save final report to output/analysis_report.txt

Always use Python with pandas for data operations."""
```

### 3. Permission Mode

Using `permission_mode="acceptEdits"` to:
- Auto-approve file read/write operations
- Allow Bash command execution
- Minimize user intervention during analysis

### 4. Output Format

The analysis report will be a plain text file containing:
- Summary of data analyzed
- Key findings
- Direct answer to user's question
- Supporting statistics

---

## Error Handling

| Error Type | Handling Strategy |
|------------|-------------------|
| CSV not found | Agent will report file not found and suggest checking the path |
| Invalid CSV format | Agent will attempt to parse and report issues |
| Python errors | Agent will see error output and retry with corrected code |
| Missing packages | Agent can install packages via `pip install` |
| API errors | Propagate to main.py with appropriate error messages |

---

## Testing Strategy

### Test Cases

1. **Basic Analysis**: Simple CSV with descriptive statistics request
2. **Complex Query**: Multi-column aggregation with filtering
3. **Missing Data**: CSV with null values
4. **Large File**: Performance with larger datasets
5. **Edge Cases**: Empty CSV, single row, malformed data

### Sample Test in main.py

```python
# Test configuration
CSV_PATH = "data/sample_sales.csv"
USER_PROMPT = "What are the top 5 products by revenue? Show monthly trends."
```

---

## Future Enhancements

1. **Custom Tools**: Add specialized tools for common operations
2. **Visualization**: Automatic chart generation
3. **Multiple File Support**: Analyze related CSVs together
4. **Caching**: Store intermediate results for faster re-analysis
5. **Streaming Output**: Real-time progress updates
