"""
Interactive Tool Testing - See Actual Output
No assertions - just shows you the real results so you can verify yourself.
"""

import sys
import os
import asyncio
import tempfile
import time
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tools
from config import Config

load_dotenv()


def pause():
    """Pause for user to verify output."""
    input("\n[Press ENTER to continue...]")


def section(title):
    """Print section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


# ==================== FILE OPERATIONS ====================

def test_file_operations():
    """Test file operations interactively."""
    section("FILE OPERATIONS - INTERACTIVE TEST")

    temp_dir = tempfile.mkdtemp(prefix="jarvis_interactive_")
    print(f"\n📁 Created temp directory: {temp_dir}")

    # Test 1: Create folder
    print("\n1️⃣  TEST: create_folder")
    test_folder = os.path.join(temp_dir, "my_test_folder")
    print(f"   Creating folder: {test_folder}")
    result = tools.create_folder(test_folder)
    print(f"   Result: {result}")
    print(f"   Folder exists? {os.path.exists(test_folder)}")
    pause()

    # Test 2: Create file
    print("\n2️⃣  TEST: create_file")
    test_file = os.path.join(test_folder, "hello.txt")
    content = "Hello from Jarvis! This is a test file."
    print(f"   Creating file: {test_file}")
    print(f"   Content: '{content}'")
    result = tools.create_file(test_file, content)
    print(f"   Result: {result}")
    print(f"   File exists? {os.path.exists(test_file)}")
    pause()

    # Test 3: Read file
    print("\n3️⃣  TEST: read_file")
    print(f"   Reading file: {test_file}")
    result = tools.read_file(test_file)
    print(f"   Status: {result['status']}")
    print(f"   Content retrieved: '{result.get('content', 'ERROR')}'")
    pause()

    # Test 4: Edit file
    print("\n4️⃣  TEST: edit_file")
    new_content = "UPDATED CONTENT - Jarvis was here!"
    print(f"   Editing file: {test_file}")
    print(f"   New content: '{new_content}'")
    result = tools.edit_file(test_file, new_content)
    print(f"   Result: {result}")

    # Verify the edit
    print("\n   Verifying edit by reading file again...")
    verify_result = tools.read_file(test_file)
    print(f"   Content after edit: '{verify_result.get('content', 'ERROR')}'")
    print(f"   ✓ Edit successful!" if verify_result.get('content') == new_content else "   ✗ Edit failed!")
    pause()

    # Test 5: List files
    print("\n5️⃣  TEST: list_files")
    print(f"   Listing files in: {test_folder}")
    result = tools.list_files(test_folder)
    print(f"   Status: {result['status']}")
    print(f"   Files found: {result.get('files', [])}")
    pause()

    # Cleanup
    print("\n🧹 Cleanup: Removing temp directory...")
    import shutil
    shutil.rmtree(temp_dir)
    print(f"   Removed: {temp_dir}")


# ==================== TIME & UTILITIES ====================

def test_time_utilities():
    """Test time utilities."""
    section("TIME UTILITIES - INTERACTIVE TEST")

    print("\n1️⃣  TEST: get_current_time")
    result = tools.get_current_time()
    print(f"   Status: {result['status']}")
    print(f"   Current Time: {result.get('current_time')}")
    print(f"   Hour: {result.get('hour')}")
    print(f"   Minute: {result.get('minute')}")
    print(f"   Unix Timestamp: {result.get('unix_timestamp')}")
    pause()


# ==================== SCREENSHOTS ====================

async def test_screenshots():
    """Test screenshot functions."""
    section("SCREENSHOT TOOLS - INTERACTIVE TEST")

    print("\n1️⃣  TEST: take_screenshot")
    print("   Taking full screenshot...")
    screen_capture = tools.ScreenCapture()
    result = await screen_capture.capture_screen()

    if result:
        img, data = result
        print(f"   ✓ Screenshot captured!")
        print(f"   Image size: {img.size[0]}x{img.size[1]}")
        print(f"   Data type: {type(data)}")
        print(f"   Has mime_type: {'mime_type' in data}")

        # Save to temp file so user can view it
        temp_file = tempfile.mktemp(suffix=".jpg")
        img.save(temp_file)
        print(f"\n   📸 Screenshot saved to: {temp_file}")
        print(f"   Open this file to verify the screenshot!")
    else:
        print("   ✗ Screenshot failed")
    pause()

    print("\n2️⃣  TEST: capture_screen_region")
    print("   Capturing top-left corner (200x200)...")
    result = await tools.capture_screen_region(0, 0, 200, 200)

    if result:
        img, data = result
        print(f"   ✓ Region captured!")
        print(f"   Image size: {img.size[0]}x{img.size[1]}")

        # Save to temp file
        temp_file = tempfile.mktemp(suffix=".jpg")
        img.save(temp_file)
        print(f"\n   📸 Region screenshot saved to: {temp_file}")
        print(f"   Open this file to verify it shows top-left corner!")
    else:
        print("   ✗ Region capture failed")
    pause()


# ==================== MAIN ====================

async def main():
    """Run all interactive tests."""
    print("="*70)
    print("  JARVIS INTERACTIVE TOOL TESTING SUITE")
    print("  See actual output - No assertions, just real results!")
    print("="*70)
    print("\nThis test suite will:")
    print("  • Show you the actual output of each tool")
    print("  • Save screenshots you can view")
    print("  • Create files you can inspect")
    print("  • Let you verify everything yourself")
    print("\nPress ENTER after each test to continue...")
    pause()

    # Run tests
    test_file_operations()
    test_time_utilities()
    await test_screenshots()

    section("✅ ALL INTERACTIVE TESTS COMPLETE")
    print("\nYou've seen the actual output of each tool!")
    print("Check the temp files created to verify screenshots.")


if __name__ == "__main__":
    asyncio.run(main())
