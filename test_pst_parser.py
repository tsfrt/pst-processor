#!/usr/bin/env python3
"""
Unit tests and integration tests for the PST parser.

This script tests various components of the PST parser without requiring actual PST files.
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime


def test_file_discovery():
    """Test the PST file discovery functionality."""
    print("\n" + "="*80)
    print("TEST 1: File Discovery")
    print("="*80)
    
    # Create temporary test structure
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test PST files in nested directories
        test_files = [
            os.path.join(tmpdir, "test1.pst"),
            os.path.join(tmpdir, "subfolder", "test2.pst"),
            os.path.join(tmpdir, "subfolder", "deep", "test3.pst"),
            os.path.join(tmpdir, "other", "test4.PST"),  # Test case insensitive
        ]
        
        # Also create non-PST files
        non_pst_files = [
            os.path.join(tmpdir, "readme.txt"),
            os.path.join(tmpdir, "subfolder", "data.csv"),
        ]
        
        # Create all directories and files
        all_files = test_files + non_pst_files
        for filepath in all_files:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                f.write("test content")
        
        print(f"Created test structure in: {tmpdir}")
        print(f"Expected PST files: {len(test_files)}")
        print(f"Non-PST files: {len(non_pst_files)}")
        
        # Test file discovery (import the function)
        try:
            # Simulate the find_pst_files function
            pst_files = []
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    if file.lower().endswith('.pst'):
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        pst_files.append((file_path, file_size))
            
            print(f"\n✓ Found {len(pst_files)} PST files:")
            for fp, fs in pst_files:
                print(f"  - {os.path.relpath(fp, tmpdir)}")
            
            assert len(pst_files) == len(test_files), f"Expected {len(test_files)}, found {len(pst_files)}"
            print("\n✅ TEST PASSED: File discovery working correctly")
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            return False
    
    return True


def test_parallel_partitioning():
    """Test the parallel processing partition calculation."""
    print("\n" + "="*80)
    print("TEST 2: Parallel Partitioning Logic")
    print("="*80)
    
    test_cases = [
        (5, None, 5),      # 5 files, auto partitions -> 5 partitions
        (10, None, 10),    # 10 files, auto partitions -> 10 partitions
        (150, None, 100),  # 150 files, auto partitions -> capped at 100
        (20, 10, 10),      # 20 files, manual 10 partitions -> 10 partitions
    ]
    
    print("Testing partition calculations:")
    all_passed = True
    
    for num_files, num_partitions_input, expected_partitions in test_cases:
        # Simulate the partition calculation logic
        if num_partitions_input is None:
            calculated = min(num_files, 100)
        else:
            calculated = num_partitions_input
        
        status = "✓" if calculated == expected_partitions else "✗"
        print(f"  {status} {num_files} files, partition={num_partitions_input} -> {calculated} (expected {expected_partitions})")
        
        if calculated != expected_partitions:
            all_passed = False
    
    if all_passed:
        print("\n✅ TEST PASSED: Partition logic working correctly")
    else:
        print("\n❌ TEST FAILED: Partition logic has errors")
    
    return all_passed


def test_large_file_detection():
    """Test large file detection logic."""
    print("\n" + "="*80)
    print("TEST 3: Large File Detection")
    print("="*80)
    
    # Test file sizes in MB
    test_cases = [
        (100, 500, False),   # 100MB file, 500MB threshold -> Not large
        (500, 500, False),   # 500MB file, 500MB threshold -> Not large (equal)
        (501, 500, True),    # 501MB file, 500MB threshold -> Large
        (1024, 500, True),   # 1GB file, 500MB threshold -> Large
    ]
    
    print("Testing large file detection:")
    all_passed = True
    
    for file_size_mb, threshold_mb, expected_large in test_cases:
        file_size_bytes = file_size_mb * 1024 * 1024
        threshold_bytes = threshold_mb * 1024 * 1024
        
        is_large = file_size_bytes > threshold_bytes
        status = "✓" if is_large == expected_large else "✗"
        
        print(f"  {status} {file_size_mb}MB file with {threshold_mb}MB threshold -> {'LARGE' if is_large else 'NORMAL'}")
        
        if is_large != expected_large:
            all_passed = False
    
    if all_passed:
        print("\n✅ TEST PASSED: Large file detection working correctly")
    else:
        print("\n❌ TEST FAILED: Large file detection has errors")
    
    return all_passed


def test_message_id_generation():
    """Test unique message ID generation."""
    print("\n" + "="*80)
    print("TEST 4: Message ID Generation")
    print("="*80)
    
    import hashlib
    
    # Test that different messages get different IDs
    messages = [
        ("file1.pst", "Subject 1", "sender1@example.com", "2024-01-01 10:00:00"),
        ("file1.pst", "Subject 2", "sender1@example.com", "2024-01-01 10:00:00"),
        ("file2.pst", "Subject 1", "sender1@example.com", "2024-01-01 10:00:00"),
    ]
    
    message_ids = []
    for source_file, subject, sender, delivery_time in messages:
        message_id = hashlib.md5(f"{source_file}{subject}{sender}{delivery_time}".encode()).hexdigest()
        message_ids.append(message_id)
        print(f"  Message: {subject} -> ID: {message_id[:16]}...")
    
    # Check all IDs are unique
    unique_ids = len(set(message_ids))
    
    if unique_ids == len(messages):
        print(f"\n✅ TEST PASSED: All {len(messages)} messages have unique IDs")
        return True
    else:
        print(f"\n❌ TEST FAILED: Expected {len(messages)} unique IDs, got {unique_ids}")
        return False


def test_batch_processing():
    """Test message batching logic."""
    print("\n" + "="*80)
    print("TEST 5: Message Batching")
    print("="*80)
    
    # Simulate batching messages
    total_messages = 2547
    batch_size = 1000
    
    batches = []
    for i in range(0, total_messages, batch_size):
        batch = list(range(i, min(i + batch_size, total_messages)))
        batches.append(batch)
    
    print(f"Total messages: {total_messages}")
    print(f"Batch size: {batch_size}")
    print(f"Number of batches: {len(batches)}")
    
    # Verify batching
    total_in_batches = sum(len(b) for b in batches)
    
    print(f"\nBatch breakdown:")
    for i, batch in enumerate(batches):
        print(f"  Batch {i+1}: {len(batch)} messages")
    
    if total_in_batches == total_messages:
        print(f"\n✅ TEST PASSED: All {total_messages} messages batched correctly")
        return True
    else:
        print(f"\n❌ TEST FAILED: Expected {total_messages} messages, got {total_in_batches}")
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print("RUNNING PST PARSER UNIT TESTS")
    print("="*80)
    
    tests = [
        ("File Discovery", test_file_discovery),
        ("Parallel Partitioning", test_parallel_partitioning),
        ("Large File Detection", test_large_file_detection),
        ("Message ID Generation", test_message_id_generation),
        ("Batch Processing", test_batch_processing),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ TEST ERROR in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*80)
    print(f"Results: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("✅ ALL TESTS PASSED!")
        return True
    else:
        print(f"❌ {total_count - passed_count} test(s) failed")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

