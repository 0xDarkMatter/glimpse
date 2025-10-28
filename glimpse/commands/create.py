"""Create command for generating new RV sessions"""

import os
import secrets
from datetime import datetime, timedelta

import click

from glimpse.services.storage_service import StorageService
from glimpse.services.unsplash_service import UnsplashService
from glimpse.utils.code_generator import generate_code


@click.command()
@click.option('-d', '--duration', default=60, type=int, help='Duration until reveal (in minutes)')
@click.option('-t', '--targets', default=1, type=int, help='Number of targets to create')
@click.option('-n', '--name', default=None, help='Optional session name')
@click.option('-s', '--source', default='unsplash', help='Image source (unsplash)')
def create(duration, targets, name, source):
    """Create a new RV session with random target images"""

    # Validate environment
    unsplash_key = os.getenv('UNSPLASH_ACCESS_KEY')
    if not unsplash_key:
        click.echo(click.style('Error: Unsplash API key not found', fg='red'))
        click.echo(click.style('\nPlease set UNSPLASH_ACCESS_KEY in your .env file or environment', fg='yellow'))
        click.echo(click.style('Get your key at: https://unsplash.com/developers\n', fg='bright_black'))
        return

    # Validate target count
    if targets < 1 or targets > 10:
        click.echo(click.style('Error: Target count must be between 1 and 10', fg='red'))
        return

    # Initialize services
    try:
        image_service = UnsplashService(unsplash_key)
        data_dir = os.path.join(os.getcwd(), 'data')
        storage = StorageService(data_dir)
    except Exception as e:
        click.echo(click.style(f'Error initializing services: {e}', fg='red'))
        return

    # Generate session ID
    session_id = secrets.token_hex(8)

    # Calculate times
    created_at = datetime.now()
    reveal_at = created_at + timedelta(minutes=duration)

    # Create targets
    target_list = []

    with click.progressbar(
        range(targets),
        label='Creating targets',
        show_pos=True
    ) as bar:
        for i in bar:
            try:
                # Generate unique code
                code = generate_code()

                # Fetch random image
                image = image_service.fetch_random_image()

                target_list.append({
                    'code': code,
                    'targetUrl': image['url'],
                    'targetDescription': image['description'],
                    'targetSource': 'unsplash',
                    'revealed': False
                })
            except Exception as e:
                click.echo(click.style(f'\nError creating target: {e}', fg='red'))
                return

    # Create session
    session = {
        'id': session_id,
        'name': name,
        'targets': target_list,
        'createdAt': created_at.isoformat(),
        'revealAt': reveal_at.isoformat()
    }

    # Save session
    try:
        storage.save_session(session)
    except Exception as e:
        click.echo(click.style(f'Error saving session: {e}', fg='red'))
        return

    # Display session info
    click.echo()
    click.echo(click.style('=' * 58, fg='green'))
    click.echo(click.style('  SESSION CREATED', fg='green', bold=True))
    click.echo(click.style('=' * 58, fg='green'))

    click.echo()
    if name:
        click.echo(f'  Name: {click.style(name, bold=True)}')

    click.echo(f'  Session ID: {click.style(session_id, fg="bright_black")}')
    click.echo(f'  Targets: {click.style(str(targets), fg="bright_black")}')
    click.echo()
    click.echo('  Target Codes:')

    for i, target in enumerate(target_list, 1):
        click.echo(f"    {i}. {click.style(target['code'], fg='cyan', bold=True)}")

    click.echo()
    created_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
    reveal_str = reveal_at.strftime('%Y-%m-%d %H:%M:%S')
    click.echo(f'  Created: {click.style(created_str, fg="bright_black")}')
    click.echo(f'  Reveal At: {click.style(reveal_str, fg="bright_black")}')
    click.echo(f'  Duration: {click.style(f"{duration} minutes", fg="bright_black")}')
    click.echo()
    click.echo('  ' + click.style('Record your impressions, then reveal targets with:', fg='yellow'))
    click.echo('  ' + click.style('glimpse reveal <code>', fg='cyan'))
    click.echo()
    click.echo(click.style('=' * 58, fg='green'))
    click.echo()
