import { Command } from 'commander';
import chalk from 'chalk';
import boxen from 'boxen';
import inquirer from 'inquirer';
import { JsonStorageService } from '../services/storage-service';
import { normalizeCode } from '../utils/code-generator';
import { logger } from '../utils/logger';
import * as path from 'path';

export const revealCommand = new Command('reveal')
  .description('Reveal a target by its code')
  .argument('<code>', 'Target code to reveal')
  .option('-f, --force', 'Force reveal even if time has not elapsed')
  .action(async (code: string, options) => {
    try {
      const dataDir = path.join(process.cwd(), 'data');
      const storage = new JsonStorageService(dataDir);

      // Find the session containing this target code
      const allSessions = await storage.getAllSessions();
      const normalizedCode = normalizeCode(code).toUpperCase();

      let targetSession: any = null;
      let targetIndex = -1;

      for (const session of allSessions) {
        const index = session.targets.findIndex(
          (t) => normalizeCode(t.code).toUpperCase() === normalizedCode
        );
        if (index !== -1) {
          targetSession = session;
          targetIndex = index;
          break;
        }
      }

      if (!targetSession || targetIndex === -1) {
        console.log(chalk.red(`\nTarget not found: ${code}\n`));
        console.log(chalk.gray('Use "glimpse list" to see available targets.\n'));
        process.exit(1);
      }

      const target = targetSession.targets[targetIndex];

      // Check if already revealed
      if (target.revealed) {
        console.log(chalk.yellow(`\nTarget ${target.code} was already revealed.\n`));
        showTarget(target, targetSession);
        return;
      }

      // Check if time has elapsed
      const now = new Date();
      const canReveal = now >= targetSession.revealAt;

      if (!canReveal && !options.force) {
        const timeRemaining = targetSession.revealAt.getTime() - now.getTime();
        const minutesRemaining = Math.ceil(timeRemaining / (1000 * 60));

        console.log(chalk.yellow(`\nTarget ${target.code} is not ready to reveal yet.\n`));
        console.log(chalk.gray(`Time remaining: ${minutesRemaining} minutes`));
        console.log(chalk.gray(`Reveal at: ${targetSession.revealAt.toLocaleString()}\n`));

        const answers = await inquirer.prompt([
          {
            type: 'confirm',
            name: 'forceReveal',
            message: 'Do you want to force reveal anyway?',
            default: false,
          },
        ]);

        if (!answers.forceReveal) {
          console.log(chalk.gray('\nReveal cancelled.\n'));
          return;
        }
      }

      // Mark target as revealed
      targetSession.targets[targetIndex].revealed = true;
      targetSession.targets[targetIndex].revealedAt = new Date();

      await storage.saveSession(targetSession);

      console.log(chalk.green('\nTarget revealed!\n'));
      showTarget(targetSession.targets[targetIndex], targetSession);
    } catch (error) {
      logger.error('Failed to reveal target');
      if (error instanceof Error) {
        logger.error(error.message);
      }
      process.exit(1);
    }
  });

function showTarget(target: any, session: any): void {
  console.log(
    boxen(
      chalk.bold.green('TARGET REVEALED\n\n') +
        chalk.white(`Code: ${chalk.bold.cyan(target.code)}\n`) +
        (session.name ? chalk.white(`Session: ${chalk.gray(session.name)}\n`) : '') +
        chalk.white(`Source: ${chalk.gray(target.targetSource)}\n\n`) +
        chalk.white(`Description:\n${chalk.yellow(target.targetDescription)}\n\n`) +
        chalk.white(`Image URL:\n${chalk.blue(target.targetUrl)}\n\n`) +
        chalk.gray(`Session created: ${session.createdAt.toLocaleString()}\n`) +
        chalk.gray(`Target revealed: ${target.revealedAt?.toLocaleString() || 'N/A'}`),
      {
        padding: 1,
        margin: 1,
        borderStyle: 'round',
        borderColor: 'green',
      }
    )
  );
}
