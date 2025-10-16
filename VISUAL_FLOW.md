# WhatsApp Attachments - Visual Flow

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Google Sheets                             │
│  Message Column:                                                 │
│  "Hi John! Attachments: [gdrive_url1, gdrive_url2]"            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              whatsapp_messaging.py (Main Script)                 │
│  • Reads messages from Google Sheets                            │
│  • Calls attachment_handler.parse_attachments_from_message()    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│          gdrive_attachment_handler.py (Handler Module)           │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐          │
│  │  1. Parse Attachments                             │          │
│  │     Input:  "Message Attachments: [url1, url2]"   │          │
│  │     Output: ("Message", ["url1", "url2"])         │          │
│  └──────────────────────────────────────────────────┘          │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────┐          │
│  │  2. Check Cache                                   │          │
│  │     • Generate MD5 hash of URL                    │          │
│  │     • Look up in cache_index.json                 │          │
│  │     • Return cached file if exists                │          │
│  └──────────────────────────────────────────────────┘          │
│              │                       │                           │
│         (cached)                 (not cached)                   │
│              │                       │                           │
│              │                       ▼                           │
│              │     ┌─────────────────────────────────┐          │
│              │     │  3. Download from Google Drive  │          │
│              │     │     • Extract file ID           │          │
│              │     │     • Convert to download URL   │          │
│              │     │     • Download file             │          │
│              │     │     • Save to gdrive_cache/     │          │
│              │     │     • Add to cache_index.json   │          │
│              │     └─────────────────────────────────┘          │
│              │                       │                           │
│              └───────────┬───────────┘                           │
│                          ▼                                        │
│  ┌──────────────────────────────────────────────────┐          │
│  │  4. Return Local File Paths                       │          │
│  │     ["gdrive_cache/1ABC.jpg", "gdrive_cache/..."] │          │
│  └──────────────────────────────────────────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│            whatsapp_messaging.py (Sending Logic)                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐          │
│  │  1. Open WhatsApp Chat                            │          │
│  │     driver.get(whatsapp_url)                      │          │
│  └──────────────────────────────────────────────────┘          │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────┐          │
│  │  2. Attach Files (if present)                     │          │
│  │     • Click attachment button (📎)                │          │
│  │     • Find file input element                     │          │
│  │     • Send file paths (newline-separated)         │          │
│  │     • Wait for preview                            │          │
│  └──────────────────────────────────────────────────┘          │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────┐          │
│  │  3. Type Message in Caption Field                 │          │
│  │     • Find caption input field                    │          │
│  │     • Type cleaned message (without URLs)         │          │
│  └──────────────────────────────────────────────────┘          │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────┐          │
│  │  4. Send Message                                  │          │
│  │     • Click send button                           │          │
│  │     • Message + Attachments sent together         │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Cache System Details

```
gdrive_cache/
├── cache_index.json
│   {
│     "5d41402abc4b2a76b9719d911017c592": "gdrive_cache/1ABC123xyz.jpg",
│     "098f6bcd4621d373cade4e832627b4f6": "gdrive_cache/2XYZ789abc.pdf"
│   }
│
├── 1ABC123xyz.jpg    ← Downloaded image (Google Drive file ID)
└── 2XYZ789abc.pdf    ← Downloaded PDF

Flow:
1. URL → MD5 Hash → Check cache_index.json
2. If found: Return local path
3. If not found: Download → Save → Add to index → Return path
```

## Message Format Examples

### Example 1: Single Image
```
┌────────────────────────────────────────┐
│ Google Sheets Message Column           │
├────────────────────────────────────────┤
│ Hi John!                               │
│                                        │
│ Here's the floor plan.                 │
│                                        │
│ Attachments: [https://drive.google... │
└────────────────────────────────────────┘
         │
         ▼ Parse
┌────────────────────────────────────────┐
│ Cleaned Message: "Hi John!\n\nHere's   │
│ the floor plan."                       │
│                                        │
│ URLs: ["https://drive.google..."]      │
└────────────────────────────────────────┘
         │
         ▼ Send to WhatsApp
┌────────────────────────────────────────┐
│ WhatsApp Message:                      │
│ [IMAGE]                                │
│ Hi John!                               │
│ Here's the floor plan.                 │
└────────────────────────────────────────┘
```

### Example 2: Multiple Files
```
┌────────────────────────────────────────┐
│ Google Sheets Message Column           │
├────────────────────────────────────────┤
│ Property details below.                │
│                                        │
│ Attachments: [                         │
│   https://drive.google.../IMG1.jpg,    │
│   https://drive.google.../PLAN.pdf,    │
│   https://drive.google.../IMG2.jpg     │
│ ]                                      │
└────────────────────────────────────────┘
         │
         ▼ Parse
┌────────────────────────────────────────┐
│ Cleaned Message: "Property details...  │
│                                        │
│ URLs: [URL1, URL2, URL3]               │
└────────────────────────────────────────┘
         │
         ▼ Download & Send
┌────────────────────────────────────────┐
│ WhatsApp Message:                      │
│ [IMAGE1] [PDF] [IMAGE2]                │
│ Property details below.                │
└────────────────────────────────────────┘
```

## Code Flow Sequence

```
1. send_followup_messages()
   │
   ├─→ Read message from Google Sheets
   │
   ├─→ attachment_handler.parse_attachments_from_message(message)
   │   └─→ Returns: (clean_message, attachment_urls)
   │
   ├─→ If attachment_urls exist:
   │   │
   │   ├─→ attachment_handler.download_multiple(attachment_urls)
   │   │   │
   │   │   └─→ For each URL:
   │   │       ├─→ cache_manager.get_cached_file(url)
   │   │       │   └─→ Returns cached path OR None
   │   │       │
   │   │       ├─→ If not cached:
   │   │       │   ├─→ download_file(url)
   │   │       │   └─→ cache_manager.add_to_cache(url, file_path)
   │   │       │
   │   │       └─→ Returns: [local_path1, local_path2, ...]
   │   │
   │   └─→ attach_files_to_whatsapp(driver, downloaded_files)
   │       ├─→ Click attachment button
   │       ├─→ Find file input element
   │       └─→ Send file paths to input
   │
   ├─→ Type clean_message (without attachment URLs)
   │
   ├─→ Send (Keys.RETURN)
   │
   └─→ Update Google Sheets with clean_message
```

## Key Functions

```python
# Parse attachments from message
clean_msg, urls = handler.parse_attachments_from_message(message)

# Download with caching
files = handler.download_multiple(urls)

# Attach to WhatsApp
attach_files_to_whatsapp(driver, files)

# Send message
text_input.send_keys(clean_message)
text_input.send_keys(Keys.RETURN)
```

## Error Handling

```
┌───────────────────────────────────────────────┐
│ Error Scenarios                               │
├───────────────────────────────────────────────┤
│                                               │
│ 1. Invalid Google Drive URL                  │
│    → Log error, skip attachment, send text    │
│                                               │
│ 2. Download fails                             │
│    → Log error, skip that file, continue      │
│                                               │
│ 3. Attachment button not found                │
│    → Log error, send text only                │
│                                               │
│ 4. File too large                             │
│    → WhatsApp will show error, log it         │
│                                               │
│ 5. Cache corrupted                            │
│    → Clear cache entry, re-download           │
│                                               │
└───────────────────────────────────────────────┘
```

## Performance Comparison

```
Scenario 1: First Send (No Cache)
┌────────────────────────────────────────┐
│ Parse:         0.1s                    │
│ Download:      5-20s (depends on size) │
│ Cache Save:    0.1s                    │
│ Attach:        2s                      │
│ Type & Send:   3s                      │
│ TOTAL:         ~10-25s                 │
└────────────────────────────────────────┘

Scenario 2: Subsequent Send (Cached)
┌────────────────────────────────────────┐
│ Parse:         0.1s                    │
│ Cache Lookup:  0.01s                   │
│ Attach:        2s                      │
│ Type & Send:   3s                      │
│ TOTAL:         ~5s                     │
└────────────────────────────────────────┘
```
