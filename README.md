# PST File Parser for Databricks (with Spark Parallelism)

This project provides a comprehensive Databricks notebook for parsing Microsoft Outlook PST (Personal Storage Table) files and storing the extracted email data in Delta Lake tables. **Now with Spark parallel processing for significantly faster performance!**

## Features

- **⚡ Spark Parallel Processing**: Processes multiple PST files concurrently using Spark executors
- **Recursive File Discovery**: Automatically finds all PST files in a Databricks volume
- **Large File Handling**: Processes files larger than 500MB in batches to manage memory
- **Comprehensive Email Extraction**: Extracts all email metadata including:
  - Subject, sender, recipients (To/CC/BCC)
  - Email body (plain text and HTML)
  - Timestamps (delivery, creation, modification)
  - Attachment counts
  - Message size
  - Folder hierarchy
- **Delta Lake Storage**: Stores all parsed data in a structured Delta table
- **Error Handling**: Robust error handling for corrupted files or parsing issues
- **Batch Processing**: Processes messages in batches for memory efficiency

## Prerequisites

### Databricks Requirements
- Databricks Runtime 11.0 or higher
- Access to Databricks Volumes (Unity Catalog)
- Permissions to create and write to Delta tables

### Python Libraries
The notebook automatically installs the required library:
- `pypff-python`: Python library for reading PST files

## Setup Instructions

### 1. Upload PST Files to Databricks Volume

First, upload your PST files to a Databricks Volume:

```python
# Example volume path structure:
# /Volumes/<catalog>/<schema>/<volume_name>/
```

### 2. Configure the Notebook

Open `pst_processor.ipynb` and update the configuration variables in Cell 3:

```python
# Configuration
VOLUME_PATH = "/Volumes/catalog/schema/volume_name"  # Update with your volume path
MAX_FILE_SIZE_MB = 500
DELTA_TABLE_NAME = "catalog.schema.pst_emails"  # Update with your catalog/schema

# Parallelism Configuration
NUM_PARTITIONS = None  # Set to None for auto, or specify an integer
BATCH_SIZE_PER_EXECUTOR = 1000  # Messages per batch to write to Delta
ENABLE_PARALLEL_PROCESSING = True  # Set to False for sequential processing
```

**Required Configuration:**
- `VOLUME_PATH`: Path to your Databricks volume containing PST files
- `DELTA_TABLE_NAME`: Full name of the target Delta table (catalog.schema.table)

**Optional Configuration:**
- `MAX_FILE_SIZE_MB`: Threshold for processing large files in batches (default: 500MB)
- `NUM_PARTITIONS`: Number of Spark partitions (None = auto, based on file count)
- `BATCH_SIZE_PER_EXECUTOR`: Messages per batch for Delta writes (default: 1000)
- `ENABLE_PARALLEL_PROCESSING`: Enable/disable parallel processing (default: True)

### 3. Run the Notebook

Execute the notebook cells in order:
1. **Cell 1**: Installs pypff-python library
2. **Cells 2-3**: Imports and configuration
3. **Cells 4-19**: Function definitions (no execution needed, just define functions)
4. **Cell 21**: Execute the main processing pipeline with Spark parallelism ⚡
5. **Cells 23-24**: Verify results and view statistics
6. **Cell 26**: (Optional) Performance comparison between parallel and sequential modes

## Delta Table Schema

The parsed emails are stored in a Delta table with the following schema:

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| message_id | String | Unique identifier (MD5 hash) |
| source_file | String | Path to source PST file |
| folder_name | String | Folder path within PST |
| subject | String | Email subject |
| sender_name | String | Sender's display name |
| sender_email | String | Sender's email address |
| recipients_to | String | To recipients (semicolon-separated) |
| recipients_cc | String | CC recipients (semicolon-separated) |
| recipients_bcc | String | BCC recipients (semicolon-separated) |
| body | String | Email body (plain text or HTML) |
| delivery_time | Timestamp | Email delivery time |
| creation_time | Timestamp | Email creation time |
| modification_time | Timestamp | Email modification time |
| message_size | Integer | Message size in bytes |
| attachments_count | Integer | Number of attachments |
| processing_timestamp | Timestamp | When the email was processed |

## Usage Examples

### Basic Usage (Parallel Mode - Default)

```python
# Run with Spark parallelism (fastest)
results = process_pst_files(
    volume_path="/Volumes/main/emails/pst_files",
    table_name="main.emails.pst_emails",
    enable_parallel=True,  # Enable Spark parallelism
    num_partitions=None,   # Auto-determine based on file count
    batch_size=1000
)

print(f"Processed {results['files_processed']} files")
print(f"Total messages: {results['total_messages']}")
```

### Sequential Mode (For Debugging)

```python
# Run sequentially (one file at a time)
results = process_pst_files(
    volume_path="/Volumes/main/emails/pst_files",
    table_name="main.emails.pst_emails",
    enable_parallel=False  # Process files one at a time
)
```

### Custom Parallelism

```python
# Specify exact number of partitions for fine-tuned control
results = process_pst_files(
    volume_path="/Volumes/main/emails/pst_files",
    table_name="main.emails.pst_emails",
    enable_parallel=True,
    num_partitions=20,  # Use exactly 20 partitions
    batch_size=500      # Smaller batches
)
```

### Query the Results

```sql
-- Count total emails
SELECT COUNT(*) FROM catalog.schema.pst_emails;

-- Find emails by sender
SELECT * FROM catalog.schema.pst_emails
WHERE sender_email = 'user@example.com';

-- Get emails in a date range
SELECT * FROM catalog.schema.pst_emails
WHERE delivery_time BETWEEN '2023-01-01' AND '2023-12-31';

-- Summary by PST file
SELECT 
    source_file,
    COUNT(*) as email_count,
    MIN(delivery_time) as oldest_email,
    MAX(delivery_time) as newest_email
FROM catalog.schema.pst_emails
GROUP BY source_file;
```

### Advanced Queries

```sql
-- Find emails with attachments
SELECT * FROM catalog.schema.pst_emails
WHERE attachments_count > 0;

-- Search email body
SELECT * FROM catalog.schema.pst_emails
WHERE body LIKE '%meeting%';

-- Analyze email traffic by sender
SELECT 
    sender_email,
    COUNT(*) as email_count,
    AVG(message_size) as avg_size_bytes
FROM catalog.schema.pst_emails
GROUP BY sender_email
ORDER BY email_count DESC;
```

## File Processing Logic

### Spark Parallel Processing

The notebook uses Spark's distributed processing to handle multiple PST files concurrently:

1. **File Discovery**: All PST files are found recursively
2. **Work Distribution**: Files are distributed across Spark executors using RDD partitions
3. **Parallel Parsing**: Each executor processes its assigned PST files independently
4. **Result Aggregation**: Messages from all executors are collected and written to Delta
5. **Batch Writing**: Results are written to Delta table in configurable batch sizes

**Benefits:**
- ⚡ **10-100x faster** processing depending on cluster size and file count
- 🎯 Automatic work distribution across available executors
- 📊 Better resource utilization on multi-node clusters
- 🔄 Each file is processed independently for maximum parallelism

### How Large Files are Handled

Files larger than the configured threshold (default 500MB) are processed in batches:

1. **Size Check**: Files larger than threshold are flagged
2. **Batch Processing**: Messages are extracted in batches of 1,000
3. **Incremental Save**: Each batch is written to Delta table

This approach ensures:
- Memory-efficient processing
- Progress is saved incrementally
- Large files don't cause out-of-memory errors

### Error Handling

The notebook includes comprehensive error handling:
- **File Access Errors**: Skips inaccessible files and continues
- **Parsing Errors**: Logs errors and continues with next message
- **Table Write Errors**: Catches and logs write failures

## Performance Tuning

### Optimizing Parallel Processing

**For Many Small Files (100+ files < 100MB each):**
```python
# Use more partitions for better distribution
NUM_PARTITIONS = 50  # Or up to 100
BATCH_SIZE_PER_EXECUTOR = 500
```

**For Few Large Files (< 10 files > 1GB each):**
```python
# Use fewer partitions, let each executor handle one file
NUM_PARTITIONS = 5
BATCH_SIZE_PER_EXECUTOR = 2000
```

**For Balanced Workload:**
```python
# Let Spark auto-determine (recommended)
NUM_PARTITIONS = None
BATCH_SIZE_PER_EXECUTOR = 1000
```

### Cluster Sizing Recommendations

- **Small batch (<50 files, <10GB)**: Single node cluster (8-16 cores)
- **Medium batch (50-500 files, 10-100GB)**: 2-4 worker nodes (32-64 cores)
- **Large batch (500+ files, 100GB+)**: 4+ worker nodes (64+ cores)

### Expected Performance

With parallel processing enabled:
- **Processing Rate**: ~1,000-10,000 messages/second (cluster dependent)
- **Speedup**: 10-100x faster than sequential processing
- **Example**: 100 PST files with 10,000 messages each = ~10-60 minutes (vs 5-10 hours sequential)

## Troubleshooting

### Common Issues

1. **Library Installation Fails**
   ```
   Error: pypff-python installation failed
   ```
   **Solution**: Ensure you have internet access and try:
   ```python
   %pip install --upgrade pip
   %pip install pypff-python
   ```

2. **Volume Path Not Found**
   ```
   Error: No such file or directory
   ```
   **Solution**: Verify your volume path is correct and accessible:
   ```python
   dbutils.fs.ls("/Volumes/catalog/schema/volume_name/")
   ```

3. **Delta Table Permissions**
   ```
   Error: Permission denied
   ```
   **Solution**: Ensure you have CREATE TABLE and INSERT permissions on the target catalog/schema

4. **PST File Corrupted**
   ```
   Error parsing PST file
   ```
   **Solution**: The notebook will log the error and continue with other files. Check if the PST file can be opened in Outlook.

4. **Slow Parallel Processing**
   ```
   Performance is not as expected
   ```
   **Solution**: 
   - Check cluster utilization in Spark UI
   - Increase `NUM_PARTITIONS` if executors are idle
   - Decrease `NUM_PARTITIONS` if too much overhead
   - Ensure cluster has multiple worker nodes

5. **Out of Memory During Parallel Processing**
   ```
   Error: Executor lost / Out of memory
   ```
   **Solution**:
   - Reduce `NUM_PARTITIONS` to give more memory per partition
   - Reduce `BATCH_SIZE_PER_EXECUTOR` to process smaller batches
   - Increase executor memory in cluster configuration

### Performance Optimization

For large-scale processing:

1. **Enable Parallel Processing**: Make sure `ENABLE_PARALLEL_PROCESSING = True`

2. **Optimize Partition Count**: 
   ```python
   # Rule of thumb: 2-4 partitions per CPU core
   NUM_PARTITIONS = num_cpu_cores * 2
   ```

3. **Use Larger Cluster**: Scale up your Databricks cluster for faster processing
   - More worker nodes = more parallelism
   - More cores per node = better throughput

4. **Enable Auto Optimize**: For better query performance
   ```sql
   ALTER TABLE catalog.schema.pst_emails 
   SET TBLPROPERTIES (delta.autoOptimize.optimizeWrite = true);
   ```

5. **Monitor Spark UI**: 
   - Check task distribution across executors
   - Look for stragglers or uneven work distribution
   - Adjust partitions accordingly

## Security Considerations

- **Sensitive Data**: PST files may contain sensitive information. Ensure appropriate access controls on:
  - Source volumes
  - Delta tables
  - Databricks workspace

- **Compliance**: Consider data retention policies and compliance requirements when storing email data

- **Encryption**: Use Unity Catalog's encryption features for data at rest

## Limitations

- **Attachment Content**: Currently only counts attachments, doesn't extract attachment content
- **HTML Rendering**: Stores HTML as text, doesn't render or parse HTML structure
- **Duplicate Detection**: Basic deduplication using MD5 hash, may have collisions
- **PST Version**: Supports most PST formats, but very old formats may not parse correctly

## Future Enhancements

Potential improvements:
- Extract and store attachments separately
- Parse HTML body for better text extraction
- Add support for OST files
- Implement incremental processing (skip already processed files)
- Add data quality checks and validation

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Databricks logs for detailed error messages
3. Verify PST file integrity using Outlook or PST repair tools

## License

This project is provided as-is for use in Databricks environments.

