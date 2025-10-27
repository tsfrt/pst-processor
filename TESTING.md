# Testing Guide for PST Parser

This guide explains how to test the PST parser with sample data.

## Quick Start

```bash
# 1. Run unit tests (no PST files needed)
python test_pst_parser.py

# 2. Create sample email files
python create_test_pst.py --create-eml --num-emails 50

# 3. Get information about obtaining PST files
python create_test_pst.py --info
```

## Testing Options

### Option 1: Unit Tests (No PST Files Required)

Run the unit test suite to verify the parser logic:

```bash
python test_pst_parser.py
```

This tests:
- ✅ File discovery and recursive search
- ✅ Parallel partitioning logic
- ✅ Large file detection (>500MB)
- ✅ Message ID generation
- ✅ Batch processing logic

**No PST files required** - tests use mock data.

### Option 2: Create EML Files for Import

Create sample email files that can be imported into Outlook:

```bash
# Create 50 sample emails
python create_test_pst.py --create-eml --num-emails 50 --output-dir ./test_data

# Create 100 sample emails with different output directory
python create_test_pst.py --create-eml --num-emails 100 --output-dir ./emails
```

**Then import into Outlook:**
1. Open Microsoft Outlook
2. File → New → Outlook Data File (.pst)
3. Name it `test_emails.pst`
4. Drag and drop the EML files into the PST file
5. Close Outlook
6. Use the PST file for testing

### Option 3: Create Mock PST Files

Create mock PST files for testing file discovery and parallel processing:

```bash
# Create 10 mock PST files
python create_test_pst.py --create-mock --num-files 10 --output-dir ./test_data
```

⚠️ **Note:** These are NOT real PST files - they're just binary files with `.pst` extension for testing file discovery and parallel distribution logic.

### Option 4: Download Sample PST Files

Get information about downloading real sample PST files:

```bash
python create_test_pst.py --info
```

**Recommended Sources:**

1. **Microsoft Format Corpus**
   - GitHub: https://github.com/openpreserve/format-corpus/tree/master/pst-format
   - Small sample PST files for testing

2. **Digital Corpora**
   - Website: https://digitalcorpora.org/corpora/files
   - Various email format samples

3. **Create Your Own**
   - Use Microsoft Outlook to export your own emails
   - File → Export → Outlook Data File (.pst)

## Testing in Databricks

### 1. Prepare Test Data

```python
# In Databricks notebook
import os

# Create test directory in DBFS
test_dir = "/dbfs/tmp/pst_test_data"
os.makedirs(test_dir, exist_ok=True)

# Upload PST files to this directory
# You can use dbutils.fs.cp to copy files
```

### 2. Run with Test Data

```python
# Update configuration to use test directory
VOLUME_PATH = "/tmp/pst_test_data"  # Local DBFS path
DELTA_TABLE_NAME = "default.pst_test_emails"  # Test table

# Enable parallel processing
ENABLE_PARALLEL_PROCESSING = True
NUM_PARTITIONS = 2  # Small number for testing

# Run the processor
results = process_pst_files(
    volume_path=VOLUME_PATH,
    table_name=DELTA_TABLE_NAME,
    enable_parallel=True,
    num_partitions=2
)
```

### 3. Verify Results

```python
# Check the test table
df = spark.table("default.pst_test_emails")
print(f"Total records: {df.count()}")
df.show(10)

# Clean up test data
spark.sql("DROP TABLE IF EXISTS default.pst_test_emails")
```

## Performance Testing

### Test Parallel vs Sequential

Use Cell 26 in the notebook to compare performance:

```python
# Uncomment the performance comparison code in Cell 26
# Run on a small subset of PST files (5-10 files)
# Compare processing times
```

### Benchmark Different Cluster Sizes

Test with different cluster configurations:

| Cluster | Files | Expected Time |
|---------|-------|---------------|
| Single node (8 cores) | 10 files | 5-10 min |
| 2 workers (16 cores) | 10 files | 2-5 min |
| 4 workers (32 cores) | 10 files | 1-3 min |

## Common Test Scenarios

### Scenario 1: Small Batch (Development)

```python
# 5-10 PST files, < 1GB total
NUM_PARTITIONS = 5
BATCH_SIZE_PER_EXECUTOR = 500
```

**Expected:** Quick processing for code validation

### Scenario 2: Medium Batch (Staging)

```python
# 50-100 PST files, 10-20GB total
NUM_PARTITIONS = None  # Auto
BATCH_SIZE_PER_EXECUTOR = 1000
```

**Expected:** Realistic performance testing

### Scenario 3: Large Batch (Production)

```python
# 500+ PST files, 100GB+ total
NUM_PARTITIONS = None  # Auto
BATCH_SIZE_PER_EXECUTOR = 1000
# Use 4+ worker cluster
```

**Expected:** Full-scale performance validation

## Troubleshooting Tests

### Issue: pypff not installed

```bash
pip install pypff-python
```

### Issue: No PST files found

```bash
# Verify test data location
ls -la ./test_data/

# Check Databricks volume path
%fs ls /Volumes/catalog/schema/volume_name
```

### Issue: Test fails with mock files

Mock PST files (from `--create-mock`) cannot be parsed by pypff. They're only for testing:
- File discovery
- Parallel distribution
- Error handling

For actual parsing tests, use real PST files or EML imports.

### Issue: EML files not working

EML files must be imported into Outlook to create a PST file:
1. Use Outlook desktop application (not web)
2. Create new PST file first
3. Then drag EML files into it

## Automated Testing Workflow

```bash
#!/bin/bash

# Complete test workflow

echo "1. Running unit tests..."
python test_pst_parser.py

echo "2. Creating sample data..."
python create_test_pst.py --create-eml --num-emails 20 --output-dir ./test_data

echo "3. Creating mock PST files..."
python create_test_pst.py --create-mock --num-files 5 --output-dir ./test_data

echo "Testing complete!"
echo "Next: Import EML files into Outlook to create test PST file"
```

## CI/CD Integration

For continuous integration:

```yaml
# Example GitHub Actions workflow
- name: Run PST Parser Tests
  run: |
    pip install -r requirements.txt
    python test_pst_parser.py
```

## Test Data Cleanup

```bash
# Remove test data
rm -rf ./test_data

# Clean up Databricks test tables
# In Databricks:
# DROP TABLE IF EXISTS default.pst_test_emails;
```

## Best Practices

1. **Always test with small data first** - Start with 5-10 files
2. **Use mock files for CI/CD** - Don't require real PST files for automated tests
3. **Test both modes** - Run parallel and sequential to compare
4. **Monitor Spark UI** - Check task distribution during parallel tests
5. **Validate data quality** - Verify parsed emails match source
6. **Test error handling** - Include corrupted files in test suite

## Additional Resources

- Main README: [README.md](README.md)
- Quick Start Guide: [QUICKSTART.md](QUICKSTART.md)
- Parallel Processing Guide: [PARALLEL_PROCESSING_GUIDE.md](PARALLEL_PROCESSING_GUIDE.md)

