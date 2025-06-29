#!/usr/bin/env python3
"""
Simple test script to verify EOF handling in the game
"""

import subprocess
import sys

def test_eof_handling():
    """Test that the game handles EOF gracefully."""
    print("Testing EOF handling...")
    
    # Test with empty input (immediate EOF)
    try:
        result = subprocess.run(
            [sys.executable, "run_game.py", "--ascii"],
            input="",  # Empty input causes immediate EOF
            text=True,
            capture_output=True,
            timeout=10,
            cwd="/home/carnegiej/amazon_q/agentic-trek"
        )
        
        print(f"Exit code: {result.returncode}")
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        # Check if it handled EOF gracefully
        if "EOF detected" in result.stdout and result.returncode == 0:
            print("✅ EOF handling test PASSED")
        else:
            print("❌ EOF handling test FAILED")
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out - game may be hanging")
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")

if __name__ == "__main__":
    test_eof_handling()
