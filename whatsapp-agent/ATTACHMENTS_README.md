# WhatsApp Attachments Feature

## Overview

The WhatsApp automation now supports sending images, videos, and documents from Google Drive along with your messages. Files are automatically downloaded and cached locally to avoid re-downloading the same files.

## How to Use

### 1. Upload Files to Google Drive

1. Upload your images, PDFs, or videos to Google Drive
2. Right-click on the file and select "Get link"
3. Make sure the sharing is set to "Anyone with the link can view"
4. Copy the Google Drive URL

### 2. Add Attachments to Your Google Sheet Message

In your message column, use this format:

```
Your message text goes here.

Attachments: [url1, url2, url3]
```

**Example:**

```
Hi {first_name},

Here are the property brochures you requested. Let me know if you have any questions!

Attachments: [https://drive.google.com/file/d/1ABC123xyz/view?usp=sharing, https://drive.google.com/file/d/1XYZ789abc/view?usp=sharing]
```

### 3. Supported File Types

- **Images**: .jpg, .jpeg, .png, .gif, .webp
- **Videos**: .mp4 (recommended for WhatsApp compatibility)
- **Documents**: .pdf, .doc, .docx

### 4. Multiple Attachments

You can send multiple files in one message by separating the URLs with commas:

```
Check out these properties!

Attachments: [https://drive.google.com/file/d/FILE_ID_1/view, https://drive.google.com/file/d/FILE_ID_2/view, https://drive.google.com/file/d/FILE_ID_3/view]
```

## How It Works

### Caching System

The system includes a smart caching mechanism:

1. **First Download**: When you send a message with an attachment, the file is downloaded from Google Drive to the local `gdrive_cache` folder
2. **Cache Storage**: The file is stored with its Google Drive file ID as the filename
3. **Cache Index**: A `cache_index.json` file maintains a mapping of Google Drive URLs to local file paths
4. **Reuse**: On subsequent uses of the same URL, the file is loaded from cache instead of re-downloading

**Benefits:**
- ⚡ Faster message sending (no re-downloading)
- 💾 Reduced bandwidth usage
- 🔄 Works offline if files are already cached

### Cache Location

Files are cached in: `whatsapp-agent/gdrive_cache/`

This folder structure:
```
whatsapp-agent/
  ├── gdrive_cache/
  │   ├── cache_index.json       # Mapping of URLs to files
  │   ├── 1ABC123xyz.jpg         # Cached image
  │   ├── 1XYZ789abc.pdf         # Cached PDF
  │   └── ...
```

## Troubleshooting

### Attachments Not Sending

1. **Check Google Drive Permissions**: Ensure the file is shared with "Anyone with the link"
2. **Verify URL Format**: Make sure the URL is a valid Google Drive link
3. **Check File Size**: WhatsApp has limits (typically 16MB for media, 100MB for documents)
4. **Check Logs**: Look at the campaign logs for specific error messages

### Cache Issues

**Clear the cache manually:**
```bash
rm -rf whatsapp-agent/gdrive_cache/*
```

The cache will rebuild as you send new messages.

### Slow Downloads

- Large files will take time to download on first use
- Once cached, subsequent sends will be instant
- Consider compressing images/videos before uploading to Google Drive

## URL Format Examples

All these Google Drive URL formats are supported:

1. `https://drive.google.com/file/d/FILE_ID/view?usp=sharing`
2. `https://drive.google.com/file/d/FILE_ID/view`
3. `https://drive.google.com/open?id=FILE_ID`
4. `https://drive.google.com/file/d/FILE_ID`

The system automatically converts them to direct download URLs.

## Message Format Examples

### Single Image
```
Hi! Here's the floor plan you asked for.

Attachments: [https://drive.google.com/file/d/1ABC/view]
```

### Multiple Images
```
Property photos attached below.

Attachments: [https://drive.google.com/file/d/IMG1/view, https://drive.google.com/file/d/IMG2/view, https://drive.google.com/file/d/IMG3/view]
```

### Mixed Media
```
Details about the property:

Attachments: [https://drive.google.com/file/d/BROCHURE.pdf/view, https://drive.google.com/file/d/FLOORPLAN.jpg/view, https://drive.google.com/file/d/VIDEO.mp4/view]
```

### Text Only (No Attachments)
```
Just wanted to follow up on our last conversation. Let me know if you're interested!
```

## Tips

1. **Keep URLs Clean**: Remove any extra parameters after the file ID if possible
2. **Test First**: Use testing mode to verify attachments work before sending to all contacts
3. **Organize on Drive**: Keep your property images/docs organized in folders on Google Drive
4. **Consistent Naming**: Name your files descriptively on Google Drive for easier management
5. **Monitor Cache Size**: Periodically clean the cache folder if it gets too large

## Technical Details

- **Library Used**: Selenium WebDriver for WhatsApp Web automation
- **Download Library**: Python requests for file downloads
- **Cache Format**: JSON index with MD5 hash keys
- **File Storage**: Local filesystem with Google Drive file IDs as filenames
