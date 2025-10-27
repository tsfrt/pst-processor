#!/usr/bin/env python3
"""
Script to create test PST files for testing the PST parser.

This script creates sample email data in various formats for testing purposes.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
import random

def create_test_eml_files(output_dir, num_emails=10):
    """
    Create test EML files that can be imported into Outlook to create a PST file.
    
    Args:
        output_dir: Directory to save EML files
        num_emails: Number of test emails to create
    """
    import email
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    os.makedirs(output_dir, exist_ok=True)
    
    subjects = [
        "Project Update - Q4 2024",
        "Team Meeting Notes",
        "Budget Approval Request",
        "Client Presentation Materials",
        "Performance Review Schedule",
        "System Maintenance Notice",
        "New Policy Updates",
        "Training Session Invitation",
        "Quarterly Results Summary",
        "Action Items from Yesterday's Meeting"
    ]
    
    senders = [
        ("John Smith", "john.smith@example.com"),
        ("Jane Doe", "jane.doe@example.com"),
        ("Bob Johnson", "bob.johnson@example.com"),
        ("Alice Williams", "alice.williams@example.com"),
        ("Charlie Brown", "charlie.brown@example.com")
    ]
    
    recipients = [
        ("Team Lead", "team.lead@example.com"),
        ("Project Manager", "pm@example.com"),
        ("All Staff", "all-staff@example.com")
    ]
    
    print(f"Creating {num_emails} test EML files in {output_dir}...")
    
    for i in range(num_emails):
        msg = MIMEMultipart()
        
        # Select random sender
        sender_name, sender_email = random.choice(senders)
        msg['From'] = f"{sender_name} <{sender_email}>"
        
        # Select random recipient
        recipient_name, recipient_email = random.choice(recipients)
        msg['To'] = f"{recipient_name} <{recipient_email}>"
        
        # Subject
        subject = subjects[i % len(subjects)]
        msg['Subject'] = subject
        
        # Date (random date in past 6 months)
        days_ago = random.randint(0, 180)
        email_date = datetime.now() - timedelta(days=days_ago)
        msg['Date'] = email_date.strftime("%a, %d %b %Y %H:%M:%S %z")
        
        # Body
        body = f"""Hello {recipient_name},

This is a test email message #{i+1} regarding: {subject}

Key points:
- Item 1: Lorem ipsum dolor sit amet
- Item 2: Consectetur adipiscing elit
- Item 3: Sed do eiusmod tempor incididunt

Please review and let me know if you have any questions.

Best regards,
{sender_name}
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Save to file
        filename = f"test_email_{i+1:03d}.eml"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(msg.as_string())
        
        print(f"  ✓ Created {filename}")
    
    print(f"\n✅ Successfully created {num_emails} EML files!")
    print(f"\nTo create a PST file from these EMLs:")
    print("1. Open Microsoft Outlook")
    print("2. Create a new PST file (File > New > Outlook Data File)")
    print("3. Drag and drop the EML files into the PST file")
    print("4. The PST file will be saved in your Outlook data directory")
    
    return output_dir


def create_test_mbox(output_file, num_emails=10):
    """
    Create a test MBOX file (alternative to PST for testing).
    
    Args:
        output_file: Path to save MBOX file
        num_emails: Number of test emails to create
    """
    import mailbox
    from email.mime.text import MIMEText
    
    mbox = mailbox.mbox(output_file)
    
    subjects = [
        "Project Update - Q4 2024",
        "Team Meeting Notes",
        "Budget Approval Request",
        "Client Presentation Materials",
        "Performance Review Schedule"
    ]
    
    print(f"Creating MBOX file with {num_emails} emails: {output_file}")
    
    for i in range(num_emails):
        msg = MIMEText(f"This is test email #{i+1} with some sample content.")
        msg['Subject'] = subjects[i % len(subjects)]
        msg['From'] = f"sender{i % 5}@example.com"
        msg['To'] = "recipient@example.com"
        
        mbox.add(msg)
        print(f"  ✓ Added email {i+1}/{num_emails}")
    
    mbox.close()
    print(f"\n✅ Successfully created MBOX file: {output_file}")
    print("Note: MBOX is not the same as PST, but can be used for email testing")


def download_sample_pst():
    """
    Provide instructions for downloading sample PST files.
    """
    print("\n" + "="*80)
    print("HOW TO GET SAMPLE PST FILES FOR TESTING")
    print("="*80)
    
    print("\n📥 Option 1: Download Sample PST Files")
    print("-" * 80)
    print("Microsoft and other sources provide sample PST files:")
    print()
    print("1. Microsoft Sample PSTs:")
    print("   https://github.com/openpreserve/format-corpus/tree/master/pst-format")
    print()
    print("2. Digital Corpora:")
    print("   https://digitalcorpora.org/corpora/files")
    print()
    print("3. Open Preservation Foundation:")
    print("   Various format samples including PST files")
    
    print("\n📧 Option 2: Create Your Own PST File")
    print("-" * 80)
    print("Using Microsoft Outlook:")
    print()
    print("1. Open Microsoft Outlook (Windows or Mac)")
    print("2. File > New > Outlook Data File (.pst)")
    print("3. Choose a location and name (e.g., 'test_emails.pst')")
    print("4. Create some test emails:")
    print("   - Send yourself a few test emails")
    print("   - Move them to the new PST file")
    print("5. Close the PST file in Outlook")
    print("6. Copy the PST file to your Databricks volume")
    
    print("\n🔧 Option 3: Use EML Files (Generated by this script)")
    print("-" * 80)
    print("Run this script with --create-eml flag:")
    print("   python create_test_pst.py --create-eml --num-emails 50")
    print()
    print("Then import the EML files into Outlook to create a PST file.")
    
    print("\n💾 Option 4: Export from Gmail/Exchange")
    print("-" * 80)
    print("If you have Gmail or Exchange:")
    print()
    print("Gmail:")
    print("1. Go to Google Takeout (takeout.google.com)")
    print("2. Select Mail")
    print("3. Choose MBOX format (can be converted)")
    print()
    print("Exchange/Outlook 365:")
    print("1. Use Outlook desktop client")
    print("2. File > Open & Export > Import/Export")
    print("3. Export to a file > Outlook Data File (.pst)")
    print("4. Select folders to export")
    
    print("\n" + "="*80)


def create_mock_pst_structure(output_dir, num_files=3, size_mb_per_file=1):
    """
    Create mock PST file structure with test data for unit testing.
    This creates simple text files that simulate PST structure for testing purposes.
    
    Args:
        output_dir: Directory to create mock files
        num_files: Number of mock PST files
        size_mb_per_file: Approximate size per file in MB
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Creating {num_files} mock PST files in {output_dir}...")
    
    for i in range(num_files):
        filename = f"mock_test_{i+1}.pst"
        filepath = os.path.join(output_dir, filename)
        
        # Create a file with test data (not a real PST, but for testing file discovery)
        with open(filepath, 'wb') as f:
            # Write some binary-looking data
            size_bytes = size_mb_per_file * 1024 * 1024
            data = bytes(random.randint(0, 255) for _ in range(size_bytes))
            f.write(data)
        
        actual_size = os.path.getsize(filepath) / (1024 * 1024)
        print(f"  ✓ Created {filename} ({actual_size:.2f} MB)")
    
    print(f"\n✅ Created {num_files} mock PST files")
    print("⚠️  Note: These are NOT real PST files, just for testing file discovery")
    print("   They cannot be parsed by pypff, but can test the parallel processing logic")


def main():
    parser = argparse.ArgumentParser(
        description="Create test PST files or sample email data for testing the PST parser"
    )
    
    parser.add_argument(
        '--create-eml',
        action='store_true',
        help='Create sample EML files that can be imported into Outlook'
    )
    
    parser.add_argument(
        '--create-mbox',
        action='store_true',
        help='Create sample MBOX file (alternative email format)'
    )
    
    parser.add_argument(
        '--create-mock',
        action='store_true',
        help='Create mock PST files for testing (not real PST files)'
    )
    
    parser.add_argument(
        '--num-emails',
        type=int,
        default=50,
        help='Number of test emails to create (default: 50)'
    )
    
    parser.add_argument(
        '--num-files',
        type=int,
        default=5,
        help='Number of mock PST files to create (default: 5)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./test_data',
        help='Output directory for test files (default: ./test_data)'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show information about how to get sample PST files'
    )
    
    args = parser.parse_args()
    
    # If no arguments, show help and info
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n")
        download_sample_pst()
        return
    
    if args.info:
        download_sample_pst()
        return
    
    if args.create_eml:
        eml_dir = os.path.join(args.output_dir, 'eml_files')
        create_test_eml_files(eml_dir, args.num_emails)
    
    if args.create_mbox:
        mbox_file = os.path.join(args.output_dir, 'test_emails.mbox')
        os.makedirs(args.output_dir, exist_ok=True)
        create_test_mbox(mbox_file, args.num_emails)
    
    if args.create_mock:
        mock_dir = os.path.join(args.output_dir, 'mock_pst_files')
        create_mock_pst_structure(mock_dir, args.num_files)


if __name__ == '__main__':
    main()

