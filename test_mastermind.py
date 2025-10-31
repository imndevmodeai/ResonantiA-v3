#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.mastermind import Mastermind

async def test_mastermind():
    try:
        print("Creating Mastermind instance...")
        mastermind = Mastermind()
        print("✅ Mastermind created successfully")
        
        print("Testing interact method...")
        response = await mastermind.interact("Hello ArchE!")
        print(f"✅ Response: {response}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_mastermind())
    if result:
        print("🎉 Mastermind test successful!")
    else:
        print("💥 Mastermind test failed!") 