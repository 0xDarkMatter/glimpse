"""Reveal command for showing target images"""

from datetime import datetime

import click

from glimpse.services.storage_service import StorageService
from glimpse.utils.code_generator import normalize_code
from glimpse.utils.helpers import get_data_dir, format_capture_date


@click.command()
@click.argument('code')
@click.option('-f', '--force', is_flag=True, help='Force reveal even if time has not elapsed')
def reveal(code, force):
    """Reveal a target by its code"""

    storage = StorageService(get_data_dir())

    # Find the session containing this target code
    all_sessions = storage.get_all_sessions()
    normalized_code = normalize_code(code).upper()

    target_session = None
    target_index = -1

    for session in all_sessions:
        for i, target in enumerate(session['targets']):
            if normalize_code(target['code']).upper() == normalized_code:
                target_session = session
                target_index = i
                break
        if target_session:
            break

    if not target_session or target_index == -1:
        click.echo(click.style(f'\nTarget not found: {code}\n', fg='red'))
        click.echo(click.style('Use "glimpse list" to see available targets.\n', fg='bright_black'))
        return

    target = target_session['targets'][target_index]

    # Check if already revealed
    if target['revealed']:
        click.echo(click.style(f'\nTarget {target["code"]} was already revealed.\n', fg='yellow'))
        show_target(target, target_session)
        return

    # Check if time has elapsed
    now = datetime.now()
    reveal_at = datetime.fromisoformat(target_session['revealAt'])
    if reveal_at.tzinfo is not None:
        reveal_at = reveal_at.replace(tzinfo=None)
    can_reveal = now >= reveal_at

    if not can_reveal and not force:
        time_remaining = reveal_at - now
        minutes_remaining = int(time_remaining.total_seconds() / 60)

        click.echo(click.style(f'\nTarget {target["code"]} is not ready to reveal yet.\n', fg='yellow'))
        click.echo(click.style(f'Time remaining: {minutes_remaining} minutes', fg='bright_black'))
        click.echo(click.style(f'Reveal at: {reveal_at.strftime("%Y-%m-%d %H:%M:%S")}\n', fg='bright_black'))

        if click.confirm('Do you want to force reveal anyway?'):
            pass
        else:
            click.echo(click.style('\nReveal cancelled.\n', fg='bright_black'))
            return

    # Mark target as revealed
    target_session['targets'][target_index]['revealed'] = True
    target_session['targets'][target_index]['revealedAt'] = datetime.now().isoformat()

    storage.save_session(target_session)

    click.echo(click.style('\nTarget revealed!\n', fg='green'))
    show_target(target_session['targets'][target_index], target_session)


def show_target(target, session):
    """Display target information"""
    click.echo(click.style('=' * 68, fg='green'))
    click.echo(click.style('  TARGET REVEALED', fg='green', bold=True))
    click.echo(click.style('=' * 68, fg='green'))
    click.echo()

    click.echo(f"  Code: {click.style(target['code'], fg='cyan', bold=True)}")

    if session.get('name'):
        click.echo(f"  Session: {click.style(session['name'], fg='bright_black')}")

    click.echo(f"  Source: {click.style(target['targetSource'], fg='bright_black')}")

    click.echo()
    click.echo('  Description:')

    # Word wrap description
    description = target['targetDescription']
    words = description.split()
    lines = []
    current_line = ''

    for word in words:
        if len(current_line) + len(word) + 1 <= 60:
            current_line += (word + ' ')
        else:
            lines.append(current_line.strip())
            current_line = word + ' '
    if current_line:
        lines.append(current_line.strip())

    for line in lines:
        click.echo('  ' + click.style(line, fg='yellow'))

    click.echo()
    if target.get('targetSource') == 'google_streetview':
        click.echo('  Street View Panorama:')
    else:
        click.echo('  Image URL:')
    click.echo('  ' + click.style(target['targetUrl'], fg='blue'))

    # Display location link for Street View
    if target.get('targetSource') == 'google_streetview' and target.get('targetLocationUrl'):
        click.echo()
        click.echo('  Location on Map:')
        click.echo('  ' + click.style(target['targetLocationUrl'], fg='blue'))

    # Display metadata for Street View
    if target.get('targetSource') == 'google_streetview':
        if target.get('targetDate'):
            click.echo()
            formatted_date = format_capture_date(target['targetDate'])
            click.echo(f"  Captured: {click.style(formatted_date, fg='bright_black')}")

    click.echo()

    if target.get('revealedAt'):
        revealed_str = datetime.fromisoformat(target['revealedAt']).strftime('%Y-%m-%d %H:%M:%S')
        click.echo(f"  Revealed: {click.style(revealed_str, fg='bright_black')}")

    click.echo()
    click.echo(click.style('=' * 68, fg='green'))
    click.echo()
