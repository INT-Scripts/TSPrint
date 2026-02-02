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

**Upload a File:**
```bash
uv run main.py upload my_document.pdf --copies 2
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
uv run main.py auto my_document.pdf
```

### Library

You can import `TSPrintClient` in your own scripts:

```python
from tsprint.client import TSPrintClient
from tsprint.exceptions import TSPrintError

client = TSPrintClient("username", "password")

try:
    client.login()
    client.upload_file("test.pdf")
    jobs = client.get_pending_jobs()
    print(jobs)
except TSPrintError as e:
    print(f"An error occurred: {e}")
```

## Features
- **Session Management**: Automatically handles cookies and JSESSIONID.
- **Web Print**: Helper for uploading PDFs.
- **Job Release**: Check pending jobs and release them to available printers.
- **Error Handling**: Custom exceptions for clear debugging.