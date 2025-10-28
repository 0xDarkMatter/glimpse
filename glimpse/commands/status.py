"""Status command for checking sessions"""

import os
from datetime import datetime

import click

from glimpse.services.storage_service import StorageService


@click.command()
def status():
    """Check status of all sessions"""

    data_dir = os.path.join(os.getcwd(), 'data')
    storage = StorageService(data_dir)

    sessions = storage.get_all_sessions()

    if not sessions:
        click.echo(click.style('\nNo sessions found.', fg='yellow'))
        click.echo(click.style('Create one with: glimpse create\n', fg='bright_black'))
        return

    now = datetime.now()

    # Count totals
    total_sessions = len(sessions)
    total_targets = sum(len(s['targets']) for s in sessions)
    revealed_targets = sum(sum(1 for t in s['targets'] if t['revealed']) for s in sessions)

    def is_ready(session):
        reveal_at = datetime.fromisoformat(session['revealAt'])
        if reveal_at.tzinfo is not None:
            reveal_at = reveal_at.replace(tzinfo=None)
        return now >= reveal_at

    ready_sessions = sum(1 for s in sessions if is_ready(s))

    click.echo()
    click.echo(click.style('-' * 50, fg='cyan'))
    click.echo(click.style('  GLIMPSE RV STATUS', fg='cyan', bold=True))
    click.echo(click.style('-' * 50, fg='cyan'))
    click.echo()
    click.echo(f"  Total Sessions: {click.style(str(total_sessions), fg='green', bold=True)}")
    click.echo(f"  Ready to Reveal: {click.style(str(ready_sessions), fg='yellow', bold=True)}")
    click.echo(f"  Total Targets: {click.style(str(total_targets), fg='cyan', bold=True)}")
    click.echo(f"  Revealed: {click.style(str(revealed_targets), fg='green', bold=True)} / Pending: {click.style(str(total_targets - revealed_targets), fg='yellow', bold=True)}")
    click.echo()

    if ready_sessions > 0:
        click.echo(click.style('  Sessions ready to reveal:', fg='green', bold=True))
        click.echo()
        for session in sessions:
            reveal_at = datetime.fromisoformat(session['revealAt'])
            if reveal_at.tzinfo is not None:
                reveal_at = reveal_at.replace(tzinfo=None)
            if now >= reveal_at:
                name = session.get('name') or session['id']
                unrevealed = [t for t in session['targets'] if not t['revealed']]
                if unrevealed:
                    click.echo(f"    * {click.style(name, fg='cyan')}")
                    for target in unrevealed:
                        click.echo(f"      - {click.style(target['code'], fg='yellow')}")
        click.echo()

    click.echo(click.style('-' * 50, fg='cyan'))
    click.echo()
