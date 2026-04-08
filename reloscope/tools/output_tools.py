"""Output action tools — Google Sheets, Docs, and Calendar link generation.

These tools CREATE tangible outputs that users/judges can interact with:
- Google Sheets with scoring matrices and comparison data (shared via Drive)
- Google Docs with detailed reports (shared via Drive)
- Google Calendar event links (user clicks → adds to THEIR calendar)

All documents are shared with the user's email address so they appear
in the user's 'Shared with me' folder. Direct document links are returned.
"""

import urllib.parse
from google.oauth2 import service_account
from googleapiclient.discovery import build
import google.auth


def _get_credentials():
    """Get application default credentials for Sheets/Docs/Drive APIs."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials, project = google.auth.default(scopes=scopes)
    return credentials


def _share_with_user(file_id: str, credentials):
    """Make a file accessible to anyone with the link (for demo/judges)."""
    try:
        drive_service = build("drive", "v3", credentials=credentials, cache_discovery=False)

        # Also make it accessible to anyone with the link (for demo/judges)
        drive_service.permissions().create(
            fileId=file_id,
            body={
                "type": "anyone",
                "role": "reader",
            }
        ).execute()
    except Exception as e:
        # Non-fatal — doc is created even if sharing fails
        print(f"Warning: Could not share file {file_id}: {e}")


def create_shared_spreadsheet(title: str, sheets_data: list) -> dict:
    """Create a Google Sheet with structured data.

    Creates a new spreadsheet with the given data, shares it with the
        shares it with anyone with the link, and returns
    a direct link to the spreadsheet.

    Only call this when there is substantial data to present (comparisons,
    scoring matrices, detailed parameter tables). Do NOT create a sheet
    for trivial 3-5 line responses — answer those directly instead.

    Args:
        title: Title for the spreadsheet (e.g., 'City Comparison — Bangalore vs Pune vs Hyderabad').
        sheets_data: A list of dictionaries, each representing a sheet/tab:
            [
                {
                    "sheet_name": "Scoring Matrix",
                    "data": [
                        ["Parameter", "Weight", "Bangalore", "Pune", "Hyderabad"],
                        ["Air Quality (AQI)", "30%", "72 (Good)", "89 (Moderate)", "95 (Moderate)"],
                        ...
                    ]
                },
                {
                    "sheet_name": "Commute Details",
                    "data": [["From", "To", "Mode", "Distance", "Duration"], ...]
                }
            ]

    Returns:
        A dictionary with the direct spreadsheet URL and sheet ID.
    """
    try:
        credentials = _get_credentials()
        sheets_service = build("sheets", "v4", credentials=credentials, cache_discovery=False)

        # Build sheet properties for each tab
        sheet_properties = []
        for i, sheet in enumerate(sheets_data):
            sheet_properties.append({
                "properties": {
                    "title": sheet.get("sheet_name", f"Sheet{i+1}"),
                    "index": i
                }
            })

        # Create the spreadsheet
        spreadsheet = sheets_service.spreadsheets().create(
            body={
                "properties": {"title": title},
                "sheets": sheet_properties
            }
        ).execute()

        spreadsheet_id = spreadsheet["spreadsheetId"]
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"

        # Write data to each sheet
        for sheet in sheets_data:
            sheet_name = sheet.get("sheet_name", "Sheet1")
            data = sheet.get("data", [])
            if data:
                sheets_service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"'{sheet_name}'!A1",
                    valueInputOption="USER_ENTERED",
                    body={"values": data}
                ).execute()

        # Share with user
        _share_with_user(spreadsheet_id, credentials)

        return {
            "spreadsheet_url": spreadsheet_url,
            "spreadsheet_id": spreadsheet_id,
            "title": title,
            "sheets_created": len(sheets_data),
            "shared_with": "anyone with link",
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def create_shared_document(title: str, content_text: str) -> dict:
    """Create a Google Doc with formatted content.

    Creates a detailed report document with the analysis results. The document
    is shared via a public readable link and a direct link is returned.

    Only call this when a detailed, multi-section report is warranted
    (e.g., full city comparison, neighborhood deep-dive, investment thesis).
    For short answers, respond directly without creating a document.

    Args:
        title: Document title (e.g., 'Relocation Analysis: Bangalore vs Pune vs Hyderabad').
        content_text: The full document content as plain text with newlines.
            Use clear section headers, simple numbering (1., 2.), and paragraphs.
            Do NOT use markdown bold markers (**). Wait until you generate 
            the text. Then output it cleanly. Keep concise (under 2 pages).

    Returns:
        A dictionary with the direct Google Docs URL and document ID.
    """
    try:
        credentials = _get_credentials()
        docs_service = build("docs", "v1", credentials=credentials, cache_discovery=False)

        # Create the document
        doc = docs_service.documents().create(
            body={"title": title}
        ).execute()

        doc_id = doc["documentId"]
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

        # Insert content
        if content_text:
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={
                    "requests": [
                        {
                            "insertText": {
                                "location": {"index": 1},
                                "text": content_text
                            }
                        }
                    ]
                }
            ).execute()

        # Share with user
        _share_with_user(doc_id, credentials)

        return {
            "document_url": doc_url,
            "document_id": doc_id,
            "title": title,
            "shared_with": "anyone with link",
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def generate_calendar_link(event_title: str, description: str, start_datetime: str, end_datetime: str, location: str = "") -> dict:
    """Generate a Google Calendar event link that the user can click to add to THEIR calendar.

    This creates a URL that, when clicked, opens Google Calendar's event creation
    page pre-filled with the event details. The event is added to whichever
    Google account the user is logged into — no OAuth needed from our side.

    Args:
        event_title: Title of the event (e.g., 'Visit Kondapur — Scout apartments').
        description: Event description with details about what to do/check.
        start_datetime: Start date/time in format 'YYYYMMDDTHHMMSS'
                       (e.g., '20260412T100000' for April 12, 2026 at 10:00 AM).
        end_datetime: End date/time in same format
                     (e.g., '20260412T130000' for April 12, 2026 at 1:00 PM).
        location: Optional location string (e.g., 'Kondapur, Hyderabad, India').

    Returns:
        A dictionary with the calendar event link that the user can click.
        Inform the user: 'Click this link to add the event to YOUR Google Calendar.'
    """
    try:
        params = {
            "action": "TEMPLATE",
            "text": event_title,
            "details": description,
            "dates": f"{start_datetime}/{end_datetime}",
        }
        if location:
            params["location"] = location
        params["ctz"] = "Asia/Kolkata"

        calendar_url = "https://calendar.google.com/calendar/r/eventedit?" + urllib.parse.urlencode(params)

        return {
            "calendar_event_link": calendar_url,
            "event_title": event_title,
            "instruction_for_user": "Click this link to add the event to YOUR Google Calendar. It will open Google Calendar and let you save the event to your own account.",
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
