import { Command } from 'commander';
import chalk from 'chalk';
import { JsonStorageService } from '../services/storage-service';
import { normalizeCode } from '../utils/code-generator';
import { logger } from '../utils/logger';
import * as path from 'path';

export const statusCommand = new Command('status')
  .description('Check the status of a target or session')
  .argument('<code>', 'Target code or session ID to check')
  .action(async (code: string) => {
    try {
      const dataDir = path.join(process.cwd(), 'data');
      const storage = new JsonStorageService(dataDir);

      // First, try to find as session ID
      let session = await storage.getSession(code);

      if (!session) {
        // If not a session ID, search for target code
        const allSessions = await storage.getAllSessions();
        const normalizedCode = normalizeCode(code).toUpperCase();

        for (const s of allSessions) {
          const target = s.targets.find(
            (t) => normalizeCode(t.code).toUpperCase() === normalizedCode
          );
          if (target) {
            session = s;
            // Show specific target status
            showTargetStatus(target, s);
            return;
          }
        }

        console.log(chalk.red(`\nTarget or session not found: ${code}\n`));
        console.log(chalk.gray('Use "glimpse list" to see available sessions and targets.\n'));
        process.exit(1);
      }

      // Show session status
      showSessionStatus(session);
    } catch (error) {
      logger.error('Failed to check status');
      if (error instanceof Error) {
        logger.error(error.message);
      }
      process.exit(1);
    }
  });

function showTargetStatus(target: any, session: any): void {
  const now = new Date();
  const canReveal = now >= session.revealAt;
  const timeUntilReveal = session.revealAt.getTime() - now.getTime();

  console.log(chalk.bold.cyan(`\nTarget Status: ${target.code}\n`));
  console.log(chalk.white(`Status: ${getStatusBadge(target.revealed, canReveal)}`));
  console.log(chalk.gray(`Session: ${session.name || session.id}`));
  console.log(chalk.gray(`Created: ${session.createdAt.toLocaleString()}`));
  console.log(chalk.gray(`Reveal:  ${session.revealAt.toLocaleString()}`));

  if (target.revealed) {
    console.log(chalk.gray(`Revealed: ${target.revealedAt?.toLocaleString()}`));
  } else if (canReveal) {
    console.log(chalk.green('\nReady to reveal!'));
    console.log(chalk.gray(`Use: glimpse reveal ${target.code}\n`));
  } else {
    const minutes = Math.ceil(timeUntilReveal / (1000 * 60));
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;

    console.log(chalk.yellow(`\nTime remaining: ${hours}h ${remainingMinutes}m`));
    console.log(chalk.gray(`Use "glimpse reveal ${target.code} --force" to reveal now\n`));
  }
}

function showSessionStatus(session: any): void {
  const now = new Date();
  const canReveal = now >= session.revealAt;
  const timeUntilReveal = session.revealAt.getTime() - now.getTime();
  const revealedCount = session.targets.filter((t: any) => t.revealed).length;
  const totalTargets = session.targets.length;

  console.log(chalk.bold.cyan(`\nSession Status\n`));
  console.log(chalk.white(`ID: ${chalk.bold(session.id)}`));
  if (session.name) {
    console.log(chalk.white(`Name: ${session.name}`));
  }
  console.log(chalk.gray(`Created: ${session.createdAt.toLocaleString()}`));
  console.log(chalk.gray(`Reveal:  ${session.revealAt.toLocaleString()}`));
  console.log(chalk.gray(`Targets: ${revealedCount}/${totalTargets} revealed\n`));

  if (canReveal) {
    console.log(chalk.green('Session is ready to reveal!\n'));
  } else {
    const minutes = Math.ceil(timeUntilReveal / (1000 * 60));
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    console.log(chalk.yellow(`Time remaining: ${hours}h ${remainingMinutes}m\n`));
  }

  // List targets
  console.log(chalk.bold('Targets:'));
  session.targets.forEach((target: any, index: number) => {
    const status = getStatusBadge(target.revealed, canReveal);
    console.log(chalk.gray(`  ${index + 1}. ${chalk.cyan(target.code)} - ${status}`));
  });
  console.log('');
}

function getStatusBadge(revealed: boolean, canReveal: boolean): string {
  if (revealed) {
    return chalk.green('REVEALED');
  }
  if (canReveal) {
    return chalk.yellow('READY');
  }
  return chalk.blue('ACTIVE');
}
