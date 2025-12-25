#!/usr/bin/env python3
"""
CSV Analysis Agent - Core agent implementation using Claude Code SDK.

This module provides an agent that can iteratively analyze CSV files,
execute Python code, and produce comprehensive analysis reports.
"""

import asyncio
from pathlib import Path
from claude_code_sdk import query, ClaudeCodeOptions, Message


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
    output_path: str = "output/analysis_report.txt",
    verbose: bool = True
) -> str:
    """
    Analyze a CSV file based on user's prompt and save results.

    Args:
        csv_path: Path to the CSV file to analyze
        user_prompt: User's question or analysis request
        output_path: Path where the analysis report will be saved
        verbose: Whether to print progress messages

    Returns:
        The analysis result as a string
    """
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Resolve absolute paths
    csv_abs_path = str(Path(csv_path).resolve())
    output_abs_path = str(Path(output_path).resolve())

    # Construct the full prompt for the agent
    full_prompt = f"""
Analyze the CSV file located at: {csv_abs_path}

User's Question/Request:
{user_prompt}

Instructions:
1. Start by reading and exploring the CSV file structure using Python with pandas
2. Use the Bash tool to run Python code for analysis
3. Iterate as needed to fully answer the question
4. Save your final analysis and conclusions to: {output_abs_path}

Important: Use Python code execution via Bash to perform all data analysis.
Example: python3 -c "import pandas as pd; df = pd.read_csv('{csv_abs_path}'); print(df.head())"

Begin your analysis now.
"""

    if verbose:
        print(f"[Agent] Starting analysis of: {csv_path}")
        print(f"[Agent] User prompt: {user_prompt[:100]}...")

    # Configure agent options
    options = ClaudeCodeOptions(
        system_prompt=DATA_ANALYSIS_SYSTEM_PROMPT,
        allowed_tools=["Bash", "Read", "Write", "Glob", "Grep"],
        permission_mode="acceptEdits",
        max_turns=30
    )

    result_messages = []

    # Run the agent using the query function
    async for message in query(prompt=full_prompt, options=options):
        if isinstance(message, Message):
            if verbose and hasattr(message, 'content'):
                # Print assistant messages for visibility
                content = message.content
                if isinstance(content, list):
                    for block in content:
                        if hasattr(block, 'text'):
                            print(f"[Agent] {block.text[:200]}...")
                elif isinstance(content, str):
                    print(f"[Agent] {content[:200]}...")
            result_messages.append(message)

    if verbose:
        print(f"[Agent] Analysis complete. Checking output file...")

    # Read the generated report if it exists
    output_file = Path(output_path)
    if output_file.exists():
        report_content = output_file.read_text()
        if verbose:
            print(f"[Agent] Report saved to: {output_path}")
        return report_content

    # If no file was created, return collected messages
    return "Analysis completed but no report file was generated. Check agent output above."


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

    csv_abs_path = str(Path(csv_path).resolve())
    output_abs_path = str(Path(output_path).resolve())

    full_prompt = f"""
Analyze the CSV file located at: {csv_abs_path}

User's Question/Request:
{user_prompt}

Save your final analysis to: {output_abs_path}

Use Python with pandas for all data analysis operations.
"""

    options = ClaudeCodeOptions(
        system_prompt=DATA_ANALYSIS_SYSTEM_PROMPT,
        allowed_tools=["Bash", "Read", "Write", "Glob", "Grep"],
        permission_mode="acceptEdits",
        max_turns=30
    )

    async for message in query(prompt=full_prompt, options=options):
        if callback and isinstance(message, Message):
            if hasattr(message, 'content'):
                callback(message.content)

    output_file = Path(output_path)
    if output_file.exists():
        return output_file.read_text()

    return "Analysis complete. Check the output file."


def run_analysis(
    csv_path: str,
    user_prompt: str,
    output_path: str = "output/analysis_report.txt",
    verbose: bool = True
) -> str:
    """
    Synchronous wrapper for analyze_csv.

    Args:
        csv_path: Path to the CSV file to analyze
        user_prompt: User's question or analysis request
        output_path: Path where the analysis report will be saved
        verbose: Whether to print progress messages

    Returns:
        The analysis result as a string
    """
    return asyncio.run(analyze_csv(csv_path, user_prompt, output_path, verbose))


if __name__ == "__main__":
    # Quick test
    import sys

    if len(sys.argv) < 3:
        print("Usage: python csv_analysis_agent.py <csv_path> <prompt>")
        print("Example: python csv_analysis_agent.py data/sales.csv 'What are the top products?'")
        sys.exit(1)

    csv_file = sys.argv[1]
    prompt = sys.argv[2]

    result = run_analysis(csv_file, prompt)
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(result)
