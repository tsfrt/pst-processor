# Quick Start Guide

## 🚀 Get Started in 5 Minutes (with Spark Parallelism!)

### Step 1: Import Notebook to Databricks

1. Open your Databricks workspace
2. Navigate to your desired folder
3. Click **Import**
4. Upload `pst_processor.ipynb`

### Step 2: Configure Settings

Update these configuration values in **Cell 3**:

```python
# Required
VOLUME_PATH = "/Volumes/your_catalog/your_schema/your_volume"
DELTA_TABLE_NAME = "your_catalog.your_schema.pst_emails"

# Optional - Parallel Processing (enabled by default)
ENABLE_PARALLEL_PROCESSING = True  # ⚡ For 10-100x speedup!
NUM_PARTITIONS = None  # Auto-detect (recommended)
```

### Step 3: Run the Notebook

Execute cells in order:
- **Cells 1-19**: Setup and function definitions (run once)
- **Cell 21**: Execute the main pipeline with Spark parallelism ⚡
- **Cells 23-24**: View results 📊

That's it! 🎉

**Note:** Parallel processing is enabled by default for maximum performance!

## 📁 Example Configuration

```python
# Example for a "main" catalog, "emails" schema
VOLUME_PATH = "/Volumes/main/emails/pst_files"
DELTA_TABLE_NAME = "main.emails.pst_emails"
MAX_FILE_SIZE_MB = 500  # Optional: adjust for large files

# Parallel Processing (Enabled by Default)
ENABLE_PARALLEL_PROCESSING = True  # ⚡ 10-100x faster!
NUM_PARTITIONS = None  # Auto-detect optimal partitions
BATCH_SIZE_PER_EXECUTOR = 1000  # Messages per batch
```

## ✅ What Gets Processed

For each PST file, the notebook extracts:
- ✉️ All emails (inbox, sent, deleted, etc.)
- 👤 Sender and recipient information
- 📝 Subject and body content
- 📅 Timestamps (sent, created, modified)
- 📎 Attachment counts
- 📂 Folder hierarchy

## 🔍 Quick Queries

After processing, try these queries:

**Count total emails:**
```sql
SELECT COUNT(*) FROM main.emails.pst_emails;
```

**Find recent emails:**
```sql
SELECT * FROM main.emails.pst_emails
WHERE delivery_time > '2024-01-01'
ORDER BY delivery_time DESC
LIMIT 100;
```

**Top senders:**
```sql
SELECT sender_email, COUNT(*) as count
FROM main.emails.pst_emails
GROUP BY sender_email
ORDER BY count DESC
LIMIT 10;
```

## ⚙️ Advanced Options

### Disable Parallel Processing (For Debugging)

If you need to debug or process files sequentially:
```python
ENABLE_PARALLEL_PROCESSING = False  # Process one file at a time
```

### Tune Parallel Performance

**Many Small Files (100+ files):**
```python
NUM_PARTITIONS = 50  # More parallelism
BATCH_SIZE_PER_EXECUTOR = 500
```

**Few Large Files (< 10 files):**
```python
NUM_PARTITIONS = 5  # Fewer partitions
BATCH_SIZE_PER_EXECUTOR = 2000
```

### Process Specific Folder Only

Modify the volume path to target a specific subdirectory:
```python
VOLUME_PATH = "/Volumes/main/emails/pst_files/2024"
```

### Scale Up for Large Batches

For 100+ files or large PST archives:
1. Use a multi-node cluster (4+ workers)
2. Enable auto-scaling
3. Let `NUM_PARTITIONS = None` for auto-detection

## 🐛 Common Issues

**Issue:** `pypff-python installation failed`  
**Fix:** Run Cell 1 again or check internet connectivity

**Issue:** `Volume path not found`  
**Fix:** Verify path with: `dbutils.fs.ls("/Volumes/catalog/schema/volume")`

**Issue:** `Permission denied on table`  
**Fix:** Ensure you have CREATE TABLE permissions on the catalog/schema

**Issue:** `PST file won't parse`  
**Fix:** File may be corrupted - notebook will skip and continue with other files

**Issue:** `Slow parallel processing`  
**Fix:** 
- Ensure you have a multi-node cluster
- Check Spark UI for executor utilization
- Try increasing `NUM_PARTITIONS`

**Issue:** `Out of memory errors`  
**Fix:**
- Reduce `NUM_PARTITIONS` (fewer files per executor)
- Reduce `BATCH_SIZE_PER_EXECUTOR` (smaller batches)
- Increase executor memory in cluster config

## 📊 Monitor Progress

The notebook provides real-time progress updates:
- File discovery progress
- Spark partition distribution (parallel mode)
- Executor-level processing logs
- Files being processed in parallel
- Messages extracted per file
- Batches saved to Delta table
- Final summary with timing statistics

**Performance Metrics:**
- Total processing time
- Messages per second throughput
- Success/failure rates per file

## 🎯 Next Steps

After successful processing:

1. **Benchmark performance** - Use Cell 26 to compare parallel vs sequential
2. **Create views** for common queries
3. **Set up dashboards** in Databricks SQL
4. **Enable auto-optimize** for better performance
5. **Schedule notebook** for periodic processing of new PST files
6. **Scale cluster** based on your typical workload

## ⚡ Performance Expectations

With parallel processing enabled:

| File Count | Total Size | Cluster | Expected Time |
|-----------|------------|---------|---------------|
| 10 files | 1 GB | Single node | ~2-5 minutes |
| 50 files | 10 GB | 2 workers | ~10-20 minutes |
| 100 files | 50 GB | 4 workers | ~20-40 minutes |
| 500+ files | 100+ GB | 8 workers | ~1-2 hours |

*Sequential processing would take 10-100x longer!*

For detailed documentation, see [README.md](README.md)

