#!/usr/bin/env python3

import mailbox
import imaplib
import email
import email.utils
import email.message # For type hinting
import time
import os
import getpass
import socket
import sys
import traceback # For detailed error reporting

# --- Configuration (Review these defaults) ---

# Path to your MBOX file (Update if the script is not in the same directory)
DEFAULT_MBOX_PATH = "mail.mbox"

# Default IMAP server details (Change if needed, or enter when prompted)
DEFAULT_IMAP_HOST = "imap.yandex.com" # e.g., imap.gmail.com, outlook.office365.com
DEFAULT_IMAP_PORT = 993  # Common SSL port
DEFAULT_USE_SSL = True   # Set to False for non-SSL (port 143 usually)

# Default target mailbox/folder on the IMAP server
DEFAULT_TARGET_MAILBOX = "Imported_Mbox"

# Delay between uploading messages in seconds (to avoid rate limiting)
UPLOAD_DELAY_SECONDS = 0.1

# How often to print progress updates (e.g., every 50 messages)
PROGRESS_INTERVAL = 50

# --- End Configuration ---

def get_imap_details():
    """Gets IMAP connection details from the user."""
    print("--- IMAP Server Configuration ---")
    host = input(f"Enter IMAP host [{DEFAULT_IMAP_HOST}]: ") or DEFAULT_IMAP_HOST
    port_str = input(f"Enter IMAP port [{DEFAULT_IMAP_PORT}]: ") or str(DEFAULT_IMAP_PORT)
    ssl_choice = input(f"Use SSL? (yes/no) [{ 'yes' if DEFAULT_USE_SSL else 'no'}]: ").lower()

    use_ssl = DEFAULT_USE_SSL
    if ssl_choice == 'no':
        use_ssl = False
    elif ssl_choice == 'yes':
        use_ssl = True

    try:
        port = int(port_str)
    except ValueError:
        print(f"Invalid port number. Using default: {DEFAULT_IMAP_PORT}")
        port = DEFAULT_IMAP_PORT

    print("\n--- IMAP Account ---")
    user = input("Enter IMAP username (your full email address): ")
    # Use getpass for secure password entry
    password = getpass.getpass("Enter IMAP password (or App Password): ")

    target_mailbox = input(f"Enter target IMAP folder name [{DEFAULT_TARGET_MAILBOX}]: ") or DEFAULT_TARGET_MAILBOX

    return host, port, use_ssl, user, password, target_mailbox

def get_message_date(msg: email.message.Message) -> tuple | None:
    """Attempts to get the internal date from the message header."""
    date_str = msg.get('Date')
    if not date_str:
        return None
    try:
        # Parse the date string into a datetime object
        dt = email.utils.parsedate_to_datetime(date_str)
        # Convert to struct_time (required by Time2Internaldate)
        tt = dt.timetuple()
        # Convert to IMAP internal date format
        return imaplib.Time2Internaldate(time.mktime(tt))
    except Exception:
        # Handle invalid or unparseable dates gracefully
        return None

def main():
    """Main function to perform the MBOX to IMAP upload."""
    # --- Get MBOX Path ---
    mbox_path_input = input(f"Enter path to MBOX file [{DEFAULT_MBOX_PATH}]: ") or DEFAULT_MBOX_PATH
    mbox_path = os.path.abspath(mbox_path_input)

    if not os.path.isfile(mbox_path):
        print(f"Error: MBOX file not found at '{mbox_path}'")
        sys.exit(1)

    # --- Get IMAP Details ---
    imap_host, imap_port, use_ssl, imap_user, imap_password, target_mailbox = get_imap_details()

    if not all([imap_host, imap_port, imap_user, imap_password, target_mailbox]):
        print("Error: Missing required IMAP connection details.")
        sys.exit(1)

    print("\n--- Starting Upload Process ---")
    print(f"Source MBOX: {mbox_path}")
    print(f"Target Server: {imap_host}:{imap_port} (SSL: {use_ssl})")
    print(f"Target User: {imap_user}")
    print(f"Target Folder: {target_mailbox}")
    print("Connecting to IMAP server...")

    server = None
    total_messages = 0
    uploaded_count = 0
    error_count = 0

    try:
        # --- Connect to IMAP Server ---
        if use_ssl:
            server = imaplib.IMAP4_SSL(imap_host, imap_port)
        else:
            server = imaplib.IMAP4(imap_host, imap_port)
        print("Connected successfully.")

        # --- Login ---
        print(f"Logging in as {imap_user}...")
        try:
            status, data = server.login(imap_user, imap_password)
            if status != 'OK':
                print(f"Error: IMAP login failed: {data}")
                sys.exit(1)
            print("Login successful.")
        except imaplib.IMAP4.error as e:
            print(f"Error: IMAP login failed: {e}")
            print("Hint: Check username/password. If using 2FA, you might need an 'App Password'.")
            sys.exit(1)

        # --- Prepare Target Mailbox ---
        print(f"Checking/Creating target folder '{target_mailbox}'...")
        try:
            # Try creating the mailbox. Ignore error if it already exists.
            status, data = server.create(f'"{target_mailbox}"') # Use quotes for names with spaces/special chars
            if status == 'OK':
                print(f"Folder '{target_mailbox}' created.")
            elif "exists" in str(data[0]).lower():
                 print(f"Folder '{target_mailbox}' already exists.")
            else:
                # Raise unexpected errors during creation
                raise imaplib.IMAP4.error(f"Failed to create/verify folder: {data}")
        except imaplib.IMAP4.error as e:
            # Ignore "already exists" errors, raise others
            if "exists" not in str(e).lower():
                print(f"Error creating/selecting mailbox '{target_mailbox}': {e}")
                sys.exit(1)
            else:
                 print(f"Folder '{target_mailbox}' already exists (error ignored).")


        # --- Open and Process MBOX ---
        print(f"Opening MBOX file: {mbox_path}")
        mbox = mailbox.mbox(mbox_path)
        print("Reading messages and starting upload...")

        message_list = list(mbox) # Read all messages into memory (may use significant RAM for large MBOX)
        total_messages = len(message_list)
        print(f"Found {total_messages} messages to upload.")

        for i, msg in enumerate(message_list):
            current_msg_num = i + 1
            try:
                # Get message data as bytes
                message_bytes = msg.as_bytes()
                # Try to get the internal date
                message_date = get_message_date(msg)
                # Flags (start with None, could attempt to map MBOX flags later if needed)
                message_flags = None

                # Append the message
                status, data = server.append(f'"{target_mailbox}"',
                                             message_flags,
                                             message_date,
                                             message_bytes)

                if status == 'OK':
                    uploaded_count += 1
                    if uploaded_count % PROGRESS_INTERVAL == 0 or current_msg_num == total_messages:
                        print(f"Uploaded message {uploaded_count}/{total_messages}")
                else:
                    error_count += 1
                    print(f"Error uploading message {current_msg_num}/{total_messages}: {data}")

                # Add a small delay
                time.sleep(UPLOAD_DELAY_SECONDS)

            except Exception as e:
                error_count += 1
                print(f"Critical error processing/uploading message {current_msg_num}/{total_messages}: {e}")
                # print(traceback.format_exc()) # Uncomment for full error details

        print("\n--- Upload Summary ---")
        print(f"Total messages in MBOX: {total_messages}")
        print(f"Successfully uploaded:   {uploaded_count}")
        print(f"Errors encountered:     {error_count}")

    except FileNotFoundError:
        print(f"Error: MBOX file not found at '{mbox_path}'")
    except socket.gaierror as e:
         print(f"Error: Could not resolve IMAP host '{imap_host}'. Check hostname and network connection. Details: {e}")
    except imaplib.IMAP4.error as e:
        print(f"An IMAP error occurred: {e}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(traceback.format_exc())

    finally:
        # --- Logout and Close Connection ---
        if server:
            try:
                print("Logging out from IMAP server...")
                server.logout()
                print("Logout successful.")
            except Exception as e:
                print(f"Error during IMAP logout: {e}")
        print("Script finished.")

# --- Run the main function ---
if __name__ == "__main__":
    main()
