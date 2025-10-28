"""List command for showing all sessions"""

from datetime import datetime

import click

from glimpse.services.storage_service import StorageService
from glimpse.utils.helpers import get_data_dir


@click.command('list')
def list_sessions():
    """List all RV sessions"""

    storage = StorageService(get_data_dir())

    sessions = storage.get_all_sessions()

    if not sessions:
        click.echo(click.style('\nNo sessions found.', fg='yellow'))
        click.echo(click.style('Create one with: glimpse create\n', fg='bright_black'))
        return

    click.echo()
    click.echo(click.style(f'Found {len(sessions)} session(s):', fg='cyan', bold=True))
    click.echo()

    for session in sessions:
        created_at = datetime.fromisoformat(session['createdAt'])
        reveal_at = datetime.fromisoformat(session['revealAt'])
        # Make naive if they have timezone info
        if created_at.tzinfo is not None:
            created_at = created_at.replace(tzinfo=None)
        if reveal_at.tzinfo is not None:
            reveal_at = reveal_at.replace(tzinfo=None)
        now = datetime.now()

        # Count revealed/total targets
        revealed_count = sum(1 for t in session['targets'] if t['revealed'])
        total_count = len(session['targets'])

        # Session header
        if session.get('name'):
            click.echo(click.style(f"  {session['name']}", fg='cyan', bold=True))
            click.echo(click.style(f"  ID: {session['id']}", fg='bright_black'))
        else:
            click.echo(click.style(f"  Session: {session['id']}", fg='cyan', bold=True))

        click.echo(f"  Created: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"  Reveal At: {reveal_at.strftime('%Y-%m-%d %H:%M:%S')}")

        # Status
        if now >= reveal_at:
            status = click.style('Ready to reveal', fg='green')
        else:
            time_remaining = reveal_at - now
            minutes_remaining = int(time_remaining.total_seconds() / 60)
            status = click.style(f'{minutes_remaining} minutes remaining', fg='yellow')

        click.echo(f"  Status: {status}")
        click.echo(f"  Targets: {revealed_count}/{total_count} revealed")
        click.echo()

        # List targets
        for target in session['targets']:
            status_icon = '[X]' if target['revealed'] else '[ ]'
            click.echo(f"    {status_icon} {click.style(target['code'], fg='cyan')}")

        click.echo()
        click.echo(click.style('  ' + '-' * 60, fg='bright_black'))
        click.echo()

    click.echo()
