#!/usr/bin/env python3
"""
CSV Analysis Agent - Main entry point.

This script demonstrates how to use the CSV analysis agent with different
prompts and CSV files. Modify the configuration variables below to test
different scenarios.
"""

import asyncio
import os
import sys
from pathlib import Path

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


def validate_environment() -> bool:
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
        return 1

    if not validate_csv_path(CSV_FILE_PATH):
        return 1

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
            output_path=OUTPUT_PATH,
            verbose=True
        )

        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"\nResults saved to: {OUTPUT_PATH}")
        print("\n--- Analysis Report ---\n")
        print(result)
        return 0

    except Exception as e:
        print(f"\nERROR: Analysis failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main entry point."""
    # Allow command-line overrides
    global CSV_FILE_PATH, USER_PROMPT

    if len(sys.argv) >= 2:
        CSV_FILE_PATH = sys.argv[1]
    if len(sys.argv) >= 3:
        USER_PROMPT = sys.argv[2]

    exit_code = asyncio.run(main_async())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
