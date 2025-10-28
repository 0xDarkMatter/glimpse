"""JSON storage service for RV sessions"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from glimpse.utils.helpers import format_capture_date


def format_timestamp(iso_timestamp: str) -> str:
    """Format ISO timestamp to human-readable format"""
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime('%B %d, %Y at %I:%M:%S %p')
    except (ValueError, AttributeError):
        return iso_timestamp


class StorageService:
    """Service for storing and retrieving RV sessions"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.sessions_dir = os.path.join(data_dir, 'sessions')

    def _get_session_dir(self, session_id: str, session_data: Optional[Dict] = None) -> str:
        """
        Get the directory path for a session

        Args:
            session_id: The session ID
            session_data: Optional session data for creating new folders with timestamp

        Returns:
            Directory path for the session
        """
        # If creating a new session, use timestamp prefix
        if session_data and 'createdAt' in session_data:
            created_at = datetime.fromisoformat(session_data['createdAt'])
            timestamp = created_at.strftime('%Y%m%d%H%M')
            folder_name = f"{timestamp}_{session_id}"
            return os.path.join(self.sessions_dir, folder_name)

        # Otherwise, find existing folder by session_id
        try:
            for entry in os.listdir(self.sessions_dir):
                if entry.endswith(f'_{session_id}') or entry == session_id:
                    return os.path.join(self.sessions_dir, entry)
        except FileNotFoundError:
            pass

        # Fallback to session_id only (for backwards compatibility)
        return os.path.join(self.sessions_dir, session_id)

    def _get_session_path(self, session_id: str) -> str:
        """Get the JSON file path for a session"""
        return os.path.join(self._get_session_dir(session_id), 'session.json')

    def _get_session_markdown_path(self, session_id: str) -> str:
        """Get the markdown file path for a session"""
        return os.path.join(self._get_session_dir(session_id), 'session.md')

    def _generate_markdown(self, session: Dict) -> str:
        """Generate markdown summary for a session"""
        lines = []

        lines.append(f"# RV Session: {session.get('name', session['id'])}")
        lines.append('')
        lines.append(f"**Session ID:** {session['id']}")
        lines.append(f"**Created:** {format_timestamp(session['createdAt'])}")
        lines.append(f"**Reveal At:** {format_timestamp(session['revealAt'])}")
        lines.append(f"**Number of Targets:** {len(session['targets'])}")
        lines.append('')

        if session.get('notes'):
            lines.append('## Notes')
            lines.append('')
            lines.append(session['notes'])
            lines.append('')

        lines.append('## Targets')
        lines.append('')

        for i, target in enumerate(session['targets'], 1):
            lines.append(f"### Target {i}: {target['code']}")
            lines.append('')
            lines.append(f"**Code:** `{target['code']}`")
            status = 'Revealed' if target['revealed'] else 'Pending'
            lines.append(f"**Status:** {status}")
            lines.append(f"**Source:** {target['targetSource']}")

            if target['revealed']:
                lines.append('')
                lines.append('**Description:**')
                lines.append('')
                lines.append(target['targetDescription'])
                lines.append('')
                lines.append('**Image:**')
                lines.append('')
                lines.append(f"![Target Image]({target['targetUrl']})")
                lines.append('')

                # Generate appropriate link text based on source
                source = target.get('targetSource', 'unsplash')
                source_url = target.get('targetSourceUrl', target['targetUrl'])
                location_url = target.get('targetLocationUrl')

                if source == 'google_streetview':
                    lines.append('[View in Street View](' + source_url + ')')
                    if location_url:
                        lines.append(' • [View Location on Map](' + location_url + ')')
                elif source == 'unsplash':
                    lines.append(f"[View on Unsplash]({source_url})")
                else:
                    lines.append(f"[View Source]({source_url})")

                lines.append('')

                # Add metadata for Street View
                if source == 'google_streetview':
                    if target.get('targetDate'):
                        formatted_date = format_capture_date(target['targetDate'])
                        lines.append(f"**Captured:** {formatted_date}")
                        lines.append('')

                if target.get('revealedAt'):
                    lines.append(f"**Revealed At:** {format_timestamp(target['revealedAt'])}")

            lines.append('')
            lines.append('---')
            lines.append('')

        lines.append('')
        lines.append('---')
        lines.append('')
        lines.append('*Generated by Glimpse RV Testing CLI*')

        return '\n'.join(lines)

    def ensure_data_directory(self):
        """Ensure the data directory exists"""
        Path(self.sessions_dir).mkdir(parents=True, exist_ok=True)

    def save_session(self, session: Dict):
        """Save a session to JSON and markdown files"""
        self.ensure_data_directory()

        session_dir = self._get_session_dir(session['id'], session)
        json_path = os.path.join(session_dir, 'session.json')
        md_path = os.path.join(session_dir, 'session.md')

        # Create session directory
        Path(session_dir).mkdir(parents=True, exist_ok=True)

        # Save JSON file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

        # Save markdown file
        markdown = self._generate_markdown(session)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get a session by ID"""
        json_path = self._get_session_path(session_id)

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def get_all_sessions(self) -> List[Dict]:
        """Get all sessions"""
        self.ensure_data_directory()

        sessions = []

        try:
            for entry in os.listdir(self.sessions_dir):
                entry_path = os.path.join(self.sessions_dir, entry)
                if os.path.isdir(entry_path):
                    # Extract session_id from folder name
                    # Format: {timestamp}_{session_id} or just {session_id}
                    if '_' in entry and len(entry.split('_')[0]) == 12:
                        # New format with timestamp
                        session_id = entry.split('_', 1)[1]
                    else:
                        # Old format or session_id only
                        session_id = entry

                    session = self.get_session(session_id)
                    if session:
                        sessions.append(session)
        except FileNotFoundError:
            return []

        # Sort by creation date (newest first)
        def get_datetime(session):
            try:
                dt = datetime.fromisoformat(session['createdAt'])
                # Make naive if it has timezone info
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                return dt
            except Exception:
                return datetime.min

        sessions.sort(key=get_datetime, reverse=True)

        return sessions

    def update_session(self, session_id: str, updates: Dict):
        """Update a session with partial data"""
        session = self.get_session(session_id)
        if not session:
            raise Exception(f'Session {session_id} not found')

        session.update(updates)
        self.save_session(session)

    def delete_session(self, session_id: str):
        """Delete a session"""
        session_dir = self._get_session_dir(session_id)

        try:
            shutil.rmtree(session_dir)
        except FileNotFoundError:
            raise Exception(f'Session {session_id} not found')
