#!/usr/bin/env python3
"""
Test script for WinampGera to verify imports and basic functionality
"""
import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import tkinter: {e}")
        return False
    
    try:
        import vlc
        print("✓ vlc imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import vlc: {e}")
        return False
    
    try:
        from winampgera import WinampGera
        print("✓ WinampGera class imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import WinampGera: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'winampgera.py',
        'requirements.txt',
        'README.md',
        'assets/icon.svg'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} is missing")
            all_exist = False
    
    return all_exist

def test_class_structure():
    """Test that WinampGera class has required methods"""
    print("\nTesting class structure...")
    
    try:
        from winampgera import WinampGera
        
        required_methods = [
            'setup_ui',
            'open_file',
            'load_file',
            'play_pause',
            'stop',
            'change_volume'
        ]
        
        all_methods_exist = True
        for method in required_methods:
            if hasattr(WinampGera, method):
                print(f"✓ Method '{method}' exists")
            else:
                print(f"✗ Method '{method}' is missing")
                all_methods_exist = False
        
        return all_methods_exist
    
    except Exception as e:
        print(f"✗ Error checking class structure: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("WinampGera Test Suite")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("File Structure", test_file_structure),
        ("Class Structure", test_class_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("=" * 50)
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
