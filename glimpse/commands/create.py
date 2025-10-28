"""Create command for generating new RV sessions"""

import os
import secrets
from datetime import datetime, timedelta

import click

from glimpse.services.storage_service import StorageService
from glimpse.services.unsplash_service import UnsplashService
from glimpse.services.google_streetview_service import GoogleStreetViewService
from glimpse.utils.code_generator import generate_code
from glimpse.utils.helpers import get_data_dir


def get_image_service(source: str):
    """Get the appropriate image service based on source"""
    if source == 'unsplash':
        api_key = os.getenv('UNSPLASH_ACCESS_KEY')
        if not api_key:
            raise ValueError(
                'UNSPLASH_ACCESS_KEY not found in environment.\n'
                'Please set it in your .env file.\n'
                'Get your key at: https://unsplash.com/developers'
            )
        return UnsplashService(api_key)

    elif source == 'google_streetview':
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not api_key:
            raise ValueError(
                'GOOGLE_MAPS_API_KEY not found in environment.\n'
                'Please set it in your .env file.\n'
                'Get your key at: https://console.cloud.google.com/\n'
                'Enable "Street View Static API" for your project.'
            )
        return GoogleStreetViewService(api_key)

    else:
        raise ValueError(f'Unknown image source: {source}')


@click.command()
@click.option('-d', '--duration', default=60, type=int, help='Duration until reveal (in minutes)')
@click.option('-t', '--targets', default=1, type=int, help='Number of targets to create')
@click.option('-n', '--name', default=None, help='Optional session name')
@click.option('-s', '--source', default='unsplash',
              type=click.Choice(['unsplash', 'google_streetview'], case_sensitive=False),
              help='Image source to use')
@click.option('--debug', is_flag=True, help='Display target details after creation')
def create(duration, targets, name, source, debug):
    """Create a new RV session with random target images"""

    # Validate target count
    if targets < 1 or targets > 10:
        click.echo(click.style('Error: Target count must be between 1 and 10', fg='red'))
        return

    # Initialize services
    try:
        image_service = get_image_service(source)
        storage = StorageService(get_data_dir())
    except ValueError as e:
        click.echo(click.style(f'Error: {str(e)}', fg='red'))
        click.echo()
        return
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

                target_dict = {
                    'code': code,
                    'targetUrl': image['url'],  # Street View panorama URL
                    'targetDescription': image['description'],
                    'targetSource': image_service.name,
                    'revealed': False
                }

                # Add optional fields if available
                if image.get('locationUrl'):
                    target_dict['targetLocationUrl'] = image['locationUrl']
                if image.get('date'):
                    target_dict['targetDate'] = image['date']

                target_list.append(target_dict)
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

    # Debug output
    if debug:
        click.echo()
        click.echo(click.style('=' * 70, fg='yellow'))
        click.echo(click.style('  DEBUG: TARGET DETAILS', fg='yellow', bold=True))
        click.echo(click.style('=' * 70, fg='yellow'))
        click.echo()

        for i, target in enumerate(target_list, 1):
            click.echo(click.style(f'Target {i}: {target["code"]}', fg='cyan', bold=True))
            click.echo()
            click.echo(f'  Description: {target["targetDescription"]}')
            click.echo()
            click.echo('  Street View Panorama:')
            click.echo(f'  {target["targetUrl"]}')
            click.echo()

            if target.get('targetLocationUrl'):
                click.echo('  Location on Map:')
                click.echo(f'  {target["targetLocationUrl"]}')
                click.echo()

            if target.get('targetDate'):
                click.echo(f'  Captured: {target["targetDate"]}')
                click.echo()

            click.echo(click.style('-' * 70, fg='bright_black'))
            click.echo()

        click.echo(click.style('=' * 70, fg='yellow'))
        click.echo()
