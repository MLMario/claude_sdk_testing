# CSV Analysis Agent - Implementation Guide

This document provides step-by-step instructions for implementing the CSV Analysis Agent using the Claude Agent SDK.

---

## Prerequisites Checklist

Before starting implementation, ensure:

- [ ] Python 3.12+ installed
- [ ] Virtual environment activated
- [ ] `ANTHROPIC_API_KEY` environment variable set
- [ ] Project dependencies installed

---

## Step 1: Install Dependencies

### 1.1 Add claude-agent-sdk to pyproject.toml

Update the dependencies in `pyproject.toml`:

```toml
[project]
name = "claude-sdk-testing"
version = "0.1.0"
description = "CSV Analysis Agent using Claude SDK"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "anthropic>=0.75.0",
    "claude-agent-sdk",
    "httpx>=0.28.1",
    "pandas>=2.3.3",
    "pydantic>=2.12.5",
    "numpy",
    "matplotlib",
]
```

### 1.2 Install Dependencies

```bash
# Using uv (recommended, already in use)
uv sync

# Or using pip
pip install -e .
```

---

## Step 2: Create Project Structure

### 2.1 Create Required Directories

```bash
mkdir -p data output
```

### 2.2 Create Sample CSV for Testing

Create `data/sample_sales.csv`:

```csv
date,product,category,quantity,price,revenue
2024-01-01,Widget A,Electronics,50,29.99,1499.50
2024-01-01,Widget B,Electronics,30,49.99,1499.70
2024-01-02,Gadget X,Home,25,19.99,499.75
2024-01-02,Widget A,Electronics,45,29.99,1349.55
2024-01-03,Gadget Y,Home,60,24.99,1499.40
2024-01-03,Widget B,Electronics,35,49.99,1749.65
2024-01-04,Widget A,Electronics,55,29.99,1649.45
2024-01-04,Gadget X,Home,40,19.99,799.60
2024-01-05,Gadget Y,Home,70,24.99,1749.30
2024-01-05,Widget B,Electronics,25,49.99,1249.75
```

---

## Step 3: Implement the Agent Module

### 3.1 Create `csv_analysis_agent.py`

This is the core agent implementation:

```python
#!/usr/bin/env python3
"""
CSV Analysis Agent - Core agent implementation using Claude SDK.

This module provides an agent that can iteratively analyze CSV files,
execute Python code, and produce comprehensive analysis reports.
"""

import asyncio
from pathlib import Path
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions


# System prompt that guides the agent's analytical behavior
DATA_ANALYSIS_SYSTEM_PROMPT = """You are an expert data analyst specializing in CSV data analysis.

When analyzing data, follow this iterative process:

## PHASE 1: DATA EXPLORATION
1. Read the CSV file to understand its structure
2. Check the shape (rows, columns)
3. Examine column names and data types
4. Identify any missing or null values
5. Look at sample rows to understand the data

## PHASE 2: ANALYSIS
Based on the user's specific question:
1. Write Python code using pandas to analyze the data
2. Execute the code and observe the results
3. If the results are incomplete or raise new questions, run additional analysis
4. Continue iterating until you have comprehensive insights

## PHASE 3: SYNTHESIS
1. Compile your findings into clear, actionable insights
2. Answer the user's question directly with supporting data
3. Include relevant statistics and patterns discovered
4. Write your final analysis to the output file

## GUIDELINES
- Always use Python with pandas for data manipulation
- Show your work by printing intermediate results
- If you encounter errors, debug and retry
- Be thorough but focused on the user's question
- Support all conclusions with actual data from the CSV
- Save your final analysis report as plain text
"""


async def analyze_csv(
    csv_path: str,
    user_prompt: str,
    output_path: str = "output/analysis_report.txt"
) -> str:
    """
    Analyze a CSV file based on user's prompt and save results.

    Args:
        csv_path: Path to the CSV file to analyze
        user_prompt: User's question or analysis request
        output_path: Path where the analysis report will be saved

    Returns:
        The analysis result as a string
    """
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Configure agent options
    options = ClaudeAgentOptions(
        system_prompt=DATA_ANALYSIS_SYSTEM_PROMPT,
        allowed_tools=["Bash", "Read", "Write", "Glob"],
        permission_mode="acceptEdits"
    )

    # Construct the full prompt for the agent
    full_prompt = f"""
Analyze the CSV file located at: {csv_path}

User's Question/Request:
{user_prompt}

Instructions:
1. Start by reading and exploring the CSV file structure
2. Use Python with pandas to perform the requested analysis
3. Iterate as needed to fully answer the question
4. Save your final analysis and conclusions to: {output_path}

Begin your analysis now.
"""

    result_text = []

    # Run the agent
    async with ClaudeSDKClient(options=options) as client:
        await client.query(full_prompt)

        async for message in client.receive_response():
            # Collect agent's output
            if hasattr(message, 'content'):
                result_text.append(str(message.content))
            elif hasattr(message, 'text'):
                result_text.append(str(message.text))

    # Read the generated report if it exists
    output_file = Path(output_path)
    if output_file.exists():
        return output_file.read_text()

    return "\n".join(result_text)


async def analyze_csv_streaming(
    csv_path: str,
    user_prompt: str,
    output_path: str = "output/analysis_report.txt",
    callback=None
) -> str:
    """
    Analyze a CSV file with streaming output for real-time progress.

    Args:
        csv_path: Path to the CSV file to analyze
        user_prompt: User's question or analysis request
        output_path: Path where the analysis report will be saved
        callback: Optional callback function for streaming updates

    Returns:
        The analysis result as a string
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    options = ClaudeAgentOptions(
        system_prompt=DATA_ANALYSIS_SYSTEM_PROMPT,
        allowed_tools=["Bash", "Read", "Write", "Glob"],
        permission_mode="acceptEdits"
    )

    full_prompt = f"""
Analyze the CSV file located at: {csv_path}

User's Question/Request:
{user_prompt}

Save your final analysis to: {output_path}
"""

    async with ClaudeSDKClient(options=options) as client:
        await client.query(full_prompt)

        async for message in client.receive_response():
            if callback and hasattr(message, 'content'):
                callback(message.content)

    output_file = Path(output_path)
    if output_file.exists():
        return output_file.read_text()

    return "Analysis complete. Check the output file."


# Convenience function for synchronous usage
def run_analysis(
    csv_path: str,
    user_prompt: str,
    output_path: str = "output/analysis_report.txt"
) -> str:
    """
    Synchronous wrapper for analyze_csv.

    Args:
        csv_path: Path to the CSV file to analyze
        user_prompt: User's question or analysis request
        output_path: Path where the analysis report will be saved

    Returns:
        The analysis result as a string
    """
    return asyncio.run(analyze_csv(csv_path, user_prompt, output_path))
```

---

## Step 4: Implement the Main Entry Point

### 4.1 Update `main.py`

This file serves as the entry point and testing interface:

```python
#!/usr/bin/env python3
"""
CSV Analysis Agent - Main entry point.

This script demonstrates how to use the CSV analysis agent with different
prompts and CSV files. Modify the configuration variables below to test
different scenarios.
"""

import asyncio
import os
from pathlib import Path

# Import the agent module
from csv_analysis_agent import analyze_csv, run_analysis


# ============================================================================
# CONFIGURATION - Modify these values to test different scenarios
# ============================================================================

# Path to the CSV file to analyze (relative to project root)
CSV_FILE_PATH = "data/sample_sales.csv"

# User's analysis prompt - what do you want to know about the data?
USER_PROMPT = """
Analyze this sales data and provide:
1. Summary statistics for all numeric columns
2. Top 3 products by total revenue
3. Daily revenue trends
4. Any interesting patterns or insights you discover
"""

# Output file path for the analysis report
OUTPUT_PATH = "output/analysis_report.txt"

# ============================================================================


def validate_environment():
    """Check that required environment variables are set."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        print("Please set it with: export ANTHROPIC_API_KEY='your-api-key'")
        return False
    return True


def validate_csv_path(csv_path: str) -> bool:
    """Check that the CSV file exists."""
    path = Path(csv_path)
    if not path.exists():
        print(f"ERROR: CSV file not found at: {csv_path}")
        print("Please ensure the file exists or update CSV_FILE_PATH.")
        return False
    return True


async def main_async():
    """Async main function for running the analysis."""
    print("=" * 60)
    print("CSV Analysis Agent")
    print("=" * 60)

    # Validate environment
    if not validate_environment():
        return

    if not validate_csv_path(CSV_FILE_PATH):
        return

    print(f"\nCSV File: {CSV_FILE_PATH}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"\nUser Prompt:\n{USER_PROMPT}")
    print("\n" + "=" * 60)
    print("Starting analysis... (this may take a few minutes)")
    print("=" * 60 + "\n")

    try:
        # Run the analysis
        result = await analyze_csv(
            csv_path=CSV_FILE_PATH,
            user_prompt=USER_PROMPT,
            output_path=OUTPUT_PATH
        )

        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"\nResults saved to: {OUTPUT_PATH}")
        print("\n--- Analysis Report ---\n")
        print(result)

    except Exception as e:
        print(f"\nERROR: Analysis failed with error: {e}")
        raise


def main():
    """Main entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
```

---

## Step 5: Environment Configuration

### 5.1 Set API Key

Set the Anthropic API key as an environment variable:

```bash
# Linux/macOS
export ANTHROPIC_API_KEY="your-api-key-here"

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your-api-key-here"

# Windows (CMD)
set ANTHROPIC_API_KEY=your-api-key-here
```

### 5.2 Optional: Create .env File

For development convenience, create a `.env` file (add to `.gitignore`):

```
ANTHROPIC_API_KEY=your-api-key-here
```

Then load it in `main.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Step 6: Run the Agent

### 6.1 Basic Usage

```bash
# Using uv
uv run python main.py

# Or directly with python
python main.py
```

### 6.2 Expected Output

```
============================================================
CSV Analysis Agent
============================================================

CSV File: data/sample_sales.csv
Output: output/analysis_report.txt

User Prompt:
Analyze this sales data and provide:
1. Summary statistics for all numeric columns
...

============================================================
Starting analysis... (this may take a few minutes)
============================================================

[Agent performs iterative analysis...]

============================================================
ANALYSIS COMPLETE
============================================================

Results saved to: output/analysis_report.txt

--- Analysis Report ---

[Analysis results appear here]
```

---

## Step 7: Testing Different Scenarios

### 7.1 Test Case 1: Basic Statistics

```python
# In main.py
CSV_FILE_PATH = "data/sample_sales.csv"
USER_PROMPT = "What are the basic statistics for this dataset?"
```

### 7.2 Test Case 2: Complex Query

```python
# In main.py
CSV_FILE_PATH = "data/sample_sales.csv"
USER_PROMPT = """
Find the correlation between quantity and revenue.
Which category has the highest average transaction value?
"""
```

### 7.3 Test Case 3: Trend Analysis

```python
# In main.py
CSV_FILE_PATH = "data/sample_sales.csv"
USER_PROMPT = "Analyze daily trends and predict the next day's revenue."
```

---

## Step 8: Project File Summary

After implementation, your project should have:

```
claude_sdk_testing/
├── main.py                     # Entry point (updated)
├── csv_analysis_agent.py       # Agent implementation (new)
├── project_plan.md             # Architecture documentation
├── implementation.md           # This file
├── pyproject.toml              # Dependencies (updated)
├── data/
│   └── sample_sales.csv        # Test data (new)
├── output/
│   └── analysis_report.txt     # Generated reports
└── README.md                   # Project readme
```

---

## Troubleshooting

### Issue: "claude-agent-sdk not found"

```bash
# Ensure you're using the correct package name
pip install claude-agent-sdk

# Or with uv
uv add claude-agent-sdk
```

### Issue: "ANTHROPIC_API_KEY not set"

```bash
# Set the environment variable
export ANTHROPIC_API_KEY="sk-ant-..."

# Verify it's set
echo $ANTHROPIC_API_KEY
```

### Issue: "Permission denied" during file write

The agent uses `permission_mode="acceptEdits"` which should handle this.
If issues persist, check directory permissions:

```bash
chmod 755 output/
```

### Issue: Agent runs indefinitely

Add a max_turns limit to options:

```python
options = ClaudeAgentOptions(
    # ... other options
    max_turns=20  # Limit iterations
)
```

---

## Next Steps

After basic implementation works:

1. **Add visualization support**: Include matplotlib charts in analysis
2. **Multiple file support**: Analyze multiple related CSVs
3. **Custom tools**: Add domain-specific analysis tools
4. **Logging**: Add detailed logging for debugging
5. **Error recovery**: Implement retry logic for transient failures

---

## Quick Start Checklist

- [ ] Install dependencies: `uv sync` or `pip install -e .`
- [ ] Set API key: `export ANTHROPIC_API_KEY="..."`
- [ ] Create test data: `data/sample_sales.csv`
- [ ] Create output dir: `mkdir -p output`
- [ ] Run: `python main.py`
- [ ] Check results: `cat output/analysis_report.txt`
