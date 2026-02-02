import argparse
import os
import sys
import logging
from dotenv import load_dotenv
from tsprint.client import TSPrintClient
from tsprint.exceptions import TSPrintError

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("tsprint")

def get_client():
    load_dotenv()
    user = os.getenv("IMPRIMERIE_USER")
    password = os.getenv("IMPRIMERIE_PASS")
    
    if not user or not password:
        logger.error("Error: IMPRIMERIE_USER and IMPRIMERIE_PASS must be set in .env")
        sys.exit(1)
        
    return TSPrintClient(user, password)

def cmd_login(args):
    client = get_client()
    try:
        client.login()
        logger.info("Login check successful!")
    except TSPrintError as e:
        logger.error(f"Login failed: {e}")
        sys.exit(1)

def cmd_upload(args):
    client = get_client()
    try:
        client.login()
        client.upload_file(args.file, args.copies)
        logger.info("File uploaded successfully to Web Print queue.")
    except TSPrintError as e:
        logger.error(f"Upload failed: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

def cmd_jobs(args):
    client = get_client()
    try:
        client.login()
        jobs = client.get_pending_jobs()
        if not jobs:
            logger.info("No pending jobs found.")
        else:
            logger.info(f"Found {len(jobs)} pending jobs:")
            for i, job in enumerate(jobs):
                logger.info(f"[{i+1}] {job['name']}")
    except TSPrintError as e:
        logger.error(f"Error checking jobs: {e}")
        sys.exit(1)

def cmd_release(args):
    client = get_client()
    try:
        client.login()
        jobs = client.get_pending_jobs()
        if not jobs:
            logger.info("No jobs to release.")
            return

        # Find matching job
        target_job = None
        if args.job_name:
             for job in jobs:
                 if args.job_name in job['name']:
                     target_job = job
                     break
        else:
            # Default to first one or interactive? 
            # CLI is usually non-interactive unless specified. 
            # Let's take the first one if not specified or ask user if interactive mode were added.
            # But the requirement implies commands.
            if len(jobs) == 1:
                target_job = jobs[0]
            else:
                logger.error("Multiple jobs found. Please specify --job-name.")
                for job in jobs: logger.info(f"- {job['name']}")
                sys.exit(1)
        
        if not target_job:
            logger.error(f"Job matching '{args.job_name}' not found.")
            sys.exit(1)

        logger.info(f"Releasing job: {target_job['name']}")
        client.release_job(target_job, printer_name_filter=args.printer)
        logger.info("Release command sent.")
        
    except TSPrintError as e:
        logger.error(f"Release failed: {e}")
        sys.exit(1)

def cmd_auto(args):
    """Uploads and then immediately releases."""
    client = get_client()
    try:
        client.login()
        
        # Upload
        client.upload_file(args.file, args.copies)
        
        # Poll for job
        logger.info("Waiting for job to appear in release queue...")
        import time
        found_job = None
        for i in range(10):
            jobs = client.get_pending_jobs()
            filename = os.path.basename(args.file)
            # Web print might change name (e.g. "Microsoft Word - ...")
            # But usually it keeps filename or close to it.
            # We look for something that contains our filename or part of it?
            # Or just the most recent one?
            # For simplicity, let's look for exact match or substring.
            
            for job in jobs:
                 # Simple heuristic
                 if filename in job['name']:
                     found_job = job
                     break
            
            if found_job: break
            time.sleep(3)
            
        if not found_job:
            logger.error("Job verification failed: File not found in release queue.")
            sys.exit(1)
            
        logger.info(f"Job found: {found_job['name']}")
        client.release_job(found_job, printer_name_filter=args.printer)
        logger.info("Job released successfully.")

    except TSPrintError as e:
        logger.error(f"Auto-print failed: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="TSPrint CLI - Manage PaperCut printing")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Login
    subparsers.add_parser("login", help="Test login credentials")

    # Upload
    upload_parser = subparsers.add_parser("upload", help="Upload a PDF file")
    upload_parser.add_argument("file", help="Path to PDF file")
    upload_parser.add_argument("--copies", type=int, default=1, help="Number of copies")

    # Jobs
    subparsers.add_parser("jobs", help="List pending jobs")

    # Release
    release_parser = subparsers.add_parser("release", help="Release a pending job")
    release_parser.add_argument("--job-name", help="Partial name of the job to release")
    release_parser.add_argument("--printer", help="Filter for printer name")

    # Auto
    auto_parser = subparsers.add_parser("auto", help="Upload and release automatically")
    auto_parser.add_argument("file", help="Path to PDF file")
    auto_parser.add_argument("--copies", type=int, default=1, help="Number of copies")
    auto_parser.add_argument("--printer", help="Filter for printer name")

    args = parser.parse_args()

    if args.command == "login":
        cmd_login(args)
    elif args.command == "upload":
        cmd_upload(args)
    elif args.command == "jobs":
        cmd_jobs(args)
    elif args.command == "release":
        cmd_release(args)
    elif args.command == "auto":
        cmd_auto(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
