#!/usr/bin/env python3
"""
Simple interactive test script
"""

import subprocess
import sys

def test_basic_commands():
    """Test basic game commands."""
    print("Testing basic game commands...")
    
    # Test with some basic commands
    commands = "\nhelp\nstatus\nsrs\nquit\ny\n"
    
    try:
        result = subprocess.run(
            [sys.executable, "run_game.py", "--ascii"],
            input=commands,
            text=True,
            capture_output=True,
            timeout=15,
            cwd="/home/carnegiej/amazon_q/agentic-trek"
        )
        
        print(f"Exit code: {result.returncode}")
        
        # Check for expected outputs
        if "HELP" in result.stdout and "STATUS" in result.stdout:
            print("✅ Basic commands test PASSED")
        else:
            print("❌ Basic commands test FAILED")
            print("STDOUT:")
            print(result.stdout[-1000:])  # Last 1000 chars
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_basic_commands()
