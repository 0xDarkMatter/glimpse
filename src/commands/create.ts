import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import boxen from 'boxen';
import { RVSession, RVTarget } from '../types';
import { UnsplashService } from '../services/unsplash-service';
import { JsonStorageService } from '../services/storage-service';
import { generateCode } from '../utils/code-generator';
import { logger } from '../utils/logger';
import * as path from 'path';
import { randomBytes } from 'crypto';

export const createCommand = new Command('create')
  .description('Create a new RV session with random target images')
  .option('-d, --duration <minutes>', 'Duration until reveal (in minutes)', '60')
  .option('-t, --targets <count>', 'Number of targets to create', '1')
  .option('-n, --name <name>', 'Optional session name')
  .option('-s, --source <source>', 'Image source (unsplash)', 'unsplash')
  .action(async (options) => {
    const spinner = ora('Creating RV session...').start();

    try {
      // Validate environment
      const unsplashKey = process.env.UNSPLASH_ACCESS_KEY;
      if (!unsplashKey) {
        spinner.fail('Unsplash API key not found');
        console.log(
          chalk.yellow('\nPlease set UNSPLASH_ACCESS_KEY in your .env file or environment')
        );
        console.log(chalk.gray('Get your key at: https://unsplash.com/developers\n'));
        process.exit(1);
      }

      // Initialize services
      const imageService = new UnsplashService(unsplashKey);
      const dataDir = path.join(process.cwd(), 'data');
      const storage = new JsonStorageService(dataDir);

      // Parse options
      const targetCount = parseInt(options.targets, 10);
      const duration = parseInt(options.duration, 10);

      if (targetCount < 1 || targetCount > 10) {
        spinner.fail('Invalid target count');
        console.log(chalk.yellow('\nTarget count must be between 1 and 10\n'));
        process.exit(1);
      }

      // Generate session ID
      const sessionId = randomBytes(8).toString('hex');

      // Calculate reveal time
      const createdAt = new Date();
      const revealAt = new Date(createdAt.getTime() + duration * 60 * 1000);

      // Create targets
      const targets: RVTarget[] = [];

      for (let i = 0; i < targetCount; i++) {
        spinner.text = `Creating target ${i + 1}/${targetCount}...`;

        // Generate unique code
        const code = generateCode();

        // Fetch random image
        const image = await imageService.fetchRandomImage();

        targets.push({
          code,
          targetUrl: image.url,
          targetDescription: image.description,
          targetSource: 'unsplash',
          revealed: false,
        });
      }

      // Create session
      const session: RVSession = {
        id: sessionId,
        name: options.name,
        targets,
        createdAt,
        revealAt,
      };

      // Save session
      spinner.text = 'Saving session...';
      await storage.saveSession(session);

      spinner.succeed('RV session created successfully!');

      // Display session info
      const targetsList = targets
        .map((t, i) => chalk.white(`  ${i + 1}. ${chalk.bold.cyan(t.code)}`))
        .join('\n');

      console.log(
        boxen(
          chalk.bold.green('SESSION CREATED\n\n') +
            (session.name ? chalk.white(`Name: ${chalk.bold(session.name)}\n`) : '') +
            chalk.white(`Session ID: ${chalk.gray(sessionId)}\n`) +
            chalk.white(`Targets: ${chalk.gray(targetCount)}\n\n`) +
            chalk.white(`Target Codes:\n${targetsList}\n\n`) +
            chalk.white(`Created: ${chalk.gray(createdAt.toLocaleString())}\n`) +
            chalk.white(`Reveal At: ${chalk.gray(revealAt.toLocaleString())}\n`) +
            chalk.white(`Duration: ${chalk.gray(`${duration} minutes`)}\n\n`) +
            chalk.yellow('Record your impressions, then reveal targets with:\n') +
            chalk.cyan(`glimpse reveal <code>`),
          {
            padding: 1,
            margin: 1,
            borderStyle: 'round',
            borderColor: 'green',
          }
        )
      );
    } catch (error) {
      spinner.fail('Failed to create session');
      if (error instanceof Error) {
        logger.error(error.message);
      }
      process.exit(1);
    }
  });
