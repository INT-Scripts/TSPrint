# TSPrint

A Python client and CLI for the PaperCut printing service (FollowMe).

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

1. Clone the repository.
2. Install dependencies:
   ```bash
   uv sync
   ```

## Configuration

Create a `.env` file in the root directory with your credentials:

```env
IMPRIMERIE_USER=your_username
IMPRIMERIE_PASS=your_password
```

## Usage

You can use the tool via the Command Line Interface (CLI) or as a Python library.

### CLI

Run commands using `uv run`:

**Check Login:**
```bash
uv run main.py login
```

**List Web Print Printers (Check for Color):**
```bash
uv run main.py list-webprint
# Output example:
# [0] Black & White
# [1] Color
```

**Upload a File:**
```bash
# Default (usually Black & White)
uv run main.py upload my_document.pdf --copies 2

# Select specific printer (e.g., Color) using index from list-webprint
uv run main.py upload my_document.pdf --printer-index 1
```

**List Pending Jobs:**
```bash
uv run main.py jobs
```

**Release a Job:**
```bash
uv run main.py release --job-name "my_document.pdf"
# Optionally specify a printer filter
uv run main.py release --job-name "my_document.pdf" --printer "MFP"
```

**Automated Flow (Upload & Release):**
```bash
uv run main.py auto my_document.pdf --printer-index 0
```

### Library

You can import `TSPrintClient` in your own scripts:

```python
from tsprint.client import TSPrintClient
from tsprint.exceptions import TSPrintError

client = TSPrintClient("username", "password")

try:
    client.login()
    # List available printers
    printers = client.get_webprint_printers()
    print(printers)
    
    # Upload to specific printer (index 1 = Color, usually)
    client.upload_file("test.pdf", printer_index=1)
    
    jobs = client.get_pending_jobs()
    print(jobs)
except TSPrintError as e:
    print(f"An error occurred: {e}")
```

## Features
- **Session Management**: Automatically handles cookies and JSESSIONID.
- **Web Print**: Helper for uploading PDFs with printer selection (Color/B&W).
- **Job Release**: Check pending jobs and release them to available printers.
- **Error Handling**: Custom exceptions for clear debugging.