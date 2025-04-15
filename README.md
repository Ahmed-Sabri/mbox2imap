# MBOX to IMAP Uploader

A simple command-line Python script to upload emails from a local MBOX file to a specified folder on an IMAP email server. This is useful for migrating emails from local archives (like Thunderbird exports) to webmail services (like Gmail, Outlook, Yandex Mail, etc.).

---

## Features

*   **MBOX Input:** Reads standard MBOX files.
*   **IMAP Upload:** Connects to any standard IMAP server.
*   **SSL/TLS Support:** Supports secure connections (default) and non-secure connections.
*   **Interactive Setup:** Prompts the user for MBOX file path, IMAP server details, username, password (hidden input), and target folder.
*   **Folder Creation:** Automatically attempts to create the target IMAP folder if it doesn't exist.
*   **Date Preservation:** Attempts to preserve the original date of the emails during upload.
*   **Progress Indicator:** Shows progress during the upload process.
*   **Configurable Delay:** Includes a small delay between uploads to help avoid server rate limiting.
*   **Error Handling:** Basic error handling for connection issues, login failures, and message upload problems.
*   **Standard Libraries Only:** Uses only Python's built-in libraries (no external dependencies to install).

---

## Requirements

*   Python 3 (tested with Python 3.7+, should work on most Python 3 versions)
*   Access to the source MBOX file.
*   IMAP access enabled on the target email account.
    *   **Note:** For services like Gmail or others with 2-Factor Authentication (2FA), you will likely need to generate an "App Password" instead of using your regular account password.

---

## How to Use

1.  **Download:** Save the script (e.g., as `mbox_to_imap.py`).
2.  **Prepare MBOX:** Place your MBOX file (e.g., `my_archive.mbox`) in a location accessible by the script. You can put it in the same directory or note its full path.
3.  **Run the Script:** Open a terminal or command prompt, navigate to the directory containing the script, and run it using Python:
    ```
    python3 mbox_to_imap.py
    ```
4.  **Follow Prompts:** The script will ask you for the following information:
    *   **Path to MBOX file:** Enter the path or press Enter to use the default (`mail.mbox` in the script's directory).
    *   **IMAP host:** e.g., `imap.gmail.com`, `outlook.office365.com`, `imap.yandex.com`.
    *   **IMAP port:** Usually `993` for SSL (default) or `143` for non-SSL.
    *   **Use SSL?** Enter `yes` (default) or `no`.
    *   **IMAP username:** Your full email address.
    *   **IMAP password:** Your email password or an App Password (input will be hidden).
    *   **Target IMAP folder name:** The name of the folder where emails should be uploaded (e.g., `Migrated Emails`). The script will try to create this folder if it doesn't exist.

5.  **Monitor:** The script will connect, log in, prepare the folder, and then start uploading emails, printing progress updates. A summary will be shown at the end.

---

## Configuration (Inside the Script)

While the script is interactive, you can modify the default values near the top of the `.py` file if needed:

*   `DEFAULT_MBOX_PATH`: Default path if the user just presses Enter.
*   `DEFAULT_IMAP_HOST`, `DEFAULT_IMAP_PORT`, `DEFAULT_USE_SSL`: Default server settings.
*   `DEFAULT_TARGET_MAILBOX`: Default folder name.
*   `UPLOAD_DELAY_SECONDS`: Time to wait between uploading messages. Increase if you hit server rate limits.
*   `PROGRESS_INTERVAL`: How often to print progress (e.g., every 50 messages).

---

## Notes and Considerations

*   **App Passwords:** Strongly recommended (and often required) for accounts using 2FA. Search your email provider's help documentation for "App Password".
*   **Large MBOX Files:** The script currently reads the entire MBOX file into memory before uploading. This might consume significant RAM for very large files (many gigabytes).
*   **Rate Limiting:** Email servers often limit how many emails you can upload in a certain period. The `UPLOAD_DELAY_SECONDS` helps mitigate this, but you might need to adjust it or run the script in batches for huge archives.
*   **Error Handling:** If an error occurs during the upload of a specific message, the script will report it and continue with the next message. Critical errors (like login failure) will stop the script.

---

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details (or you can choose another license like GPL, Apache, etc., and update this section).



*This script provides a basic utility. Always back up your MBOX file before migration. Use at your own risk.*
