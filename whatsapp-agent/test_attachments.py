#!/usr/bin/env python3
"""
Test script for Google Drive attachment functionality
Tests downloading and caching without sending WhatsApp messages
"""

import sys
from gdrive_attachment_handler import GDriveAttachmentHandler
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_parse_attachments():
    """Test parsing attachments from message text"""
    handler = GDriveAttachmentHandler()
    
    print("\n=== Test 1: Parse Attachments ===")
    
    test_message = """Hi John,

Here are the property details you requested.

Attachments: [https://drive.google.com/file/d/1ABC123/view, https://drive.google.com/file/d/2XYZ789/view]
"""
    
    clean_msg, urls = handler.parse_attachments_from_message(test_message)
    
    print(f"Original message:\n{test_message}")
    print(f"\nCleaned message:\n{clean_msg}")
    print(f"\nFound {len(urls)} attachment(s):")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")
    
    assert len(urls) == 2, "Should find 2 attachments"
    assert "Attachments:" not in clean_msg, "Attachments line should be removed"
    print("✓ Test passed!")


def test_parse_no_attachments():
    """Test message without attachments"""
    handler = GDriveAttachmentHandler()
    
    print("\n=== Test 2: No Attachments ===")
    
    test_message = "Hi John, just following up on our last conversation."
    
    clean_msg, urls = handler.parse_attachments_from_message(test_message)
    
    print(f"Message: {test_message}")
    print(f"Attachments found: {len(urls)}")
    
    assert len(urls) == 0, "Should find no attachments"
    assert clean_msg == test_message, "Message should remain unchanged"
    print("✓ Test passed!")


def test_cache_system():
    """Test the caching system"""
    handler = GDriveAttachmentHandler(cache_dir="./test_cache")
    
    print("\n=== Test 3: Cache System ===")
    
    test_url = "https://drive.google.com/file/d/1ABC123xyz/view"
    
    # Check if already cached
    cached = handler.cache_manager.get_cached_file(test_url)
    if cached:
        print(f"✓ File already in cache: {cached}")
    else:
        print("✗ File not in cache (this is expected on first run)")
    
    print("Cache index contents:")
    for url_hash, path in handler.cache_manager.cache_index.items():
        print(f"  {url_hash[:8]}... -> {path}")
    
    print("✓ Test passed!")


def test_download_with_real_url():
    """
    Test downloading with a real Google Drive URL
    Replace with your own test file URL
    """
    print("\n=== Test 4: Real Download (Optional) ===")
    print("Skipping - Replace with your own Google Drive test URL")
    
    # Uncomment and add your own test URL to test actual downloading:
    # handler = GDriveAttachmentHandler(cache_dir="./test_cache")
    # test_url = "YOUR_GOOGLE_DRIVE_URL_HERE"
    # file_path = handler.download_file(test_url)
    # if file_path:
    #     print(f"✓ Downloaded successfully: {file_path}")
    # else:
    #     print("✗ Download failed")


def test_extract_file_id():
    """Test extracting file IDs from various URL formats"""
    handler = GDriveAttachmentHandler()
    
    print("\n=== Test 5: Extract File IDs ===")
    
    test_urls = [
        "https://drive.google.com/file/d/1ABC123xyz/view?usp=sharing",
        "https://drive.google.com/file/d/1ABC123xyz/view",
        "https://drive.google.com/open?id=1ABC123xyz",
        "https://drive.google.com/file/d/1ABC123xyz",
    ]
    
    for url in test_urls:
        file_id = handler._extract_file_id(url)
        print(f"URL: {url}")
        print(f"  -> File ID: {file_id}")
        assert file_id == "1ABC123xyz", f"Failed to extract file ID from {url}"
    
    print("✓ All file IDs extracted correctly!")


if __name__ == "__main__":
    print("WhatsApp Attachment Handler - Test Suite")
    print("=" * 50)
    
    try:
        test_parse_attachments()
        test_parse_no_attachments()
        test_extract_file_id()
        test_cache_system()
        test_download_with_real_url()
        
        print("\n" + "=" * 50)
        print("✓ All tests passed!")
        print("\nTo test with real Google Drive files:")
        print("1. Upload a test file to Google Drive")
        print("2. Get the shareable link")
        print("3. Update test_download_with_real_url() with your URL")
        print("4. Uncomment the code in that function")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
