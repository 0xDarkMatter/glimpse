import { Command } from 'commander';
import chalk from 'chalk';
import { JsonStorageService } from '../services/storage-service';
import { logger } from '../utils/logger';
import * as path from 'path';

export const listCommand = new Command('list')
  .description('List all RV sessions')
  .option('-a, --all', 'Show all sessions including revealed ones')
  .option('-r, --revealed', 'Show only revealed sessions')
  .action(async (options) => {
    try {
      const dataDir = path.join(process.cwd(), 'data');
      const storage = new JsonStorageService(dataDir);

      const sessions = await storage.getAllSessions();

      if (sessions.length === 0) {
        console.log(chalk.yellow('\nNo sessions found.'));
        console.log(chalk.gray('Create one with: glimpse create\n'));
        return;
      }

      // Filter based on options
      let filteredSessions = sessions;
      if (options.revealed) {
        // Show only sessions with all targets revealed
        filteredSessions = sessions.filter((s) =>
          s.targets.every((t) => t.revealed)
        );
      } else if (!options.all) {
        // Show only sessions with at least one unrevealed target
        filteredSessions = sessions.filter((s) =>
          s.targets.some((t) => !t.revealed)
        );
      }

      if (filteredSessions.length === 0) {
        console.log(chalk.yellow('\nNo sessions match the filter.\n'));
        return;
      }

      // Display sessions
      console.log(chalk.bold.cyan(`\nRV Sessions (${filteredSessions.length}):\n`));

      filteredSessions.forEach((session) => {
        const now = new Date();
        const canReveal = now >= session.revealAt;
        const revealedCount = session.targets.filter((t) => t.revealed).length;
        const totalTargets = session.targets.length;

        const status =
          revealedCount === totalTargets
            ? chalk.green('ALL REVEALED')
            : canReveal
            ? chalk.yellow('READY')
            : chalk.blue('ACTIVE');

        const sessionName = session.name ? chalk.bold(`${session.name}`) : chalk.gray(session.id);
        console.log(`${sessionName} - ${status}`);
        console.log(chalk.gray(`  ID: ${session.id}`));
        console.log(chalk.gray(`  Created: ${session.createdAt.toLocaleString()}`));
        console.log(chalk.gray(`  Reveal:  ${session.revealAt.toLocaleString()}`));
        console.log(chalk.gray(`  Targets: ${revealedCount}/${totalTargets} revealed\n`));

        // List target codes
        session.targets.forEach((target, index) => {
          const targetStatus = target.revealed ? chalk.green('[REVEALED]') : chalk.yellow('[HIDDEN]');
          console.log(chalk.gray(`    ${index + 1}. ${chalk.cyan(target.code)} ${targetStatus}`));
        });

        console.log('');
      });

      // Show summary
      const totalTargets = sessions.reduce((sum, s) => sum + s.targets.length, 0);
      const revealedTargets = sessions.reduce(
        (sum, s) => sum + s.targets.filter((t) => t.revealed).length,
        0
      );
      console.log(
        chalk.gray(
          `Total Sessions: ${sessions.length} | Total Targets: ${totalTargets} | Revealed: ${revealedTargets}\n`
        )
      );
    } catch (error) {
      logger.error('Failed to list sessions');
      if (error instanceof Error) {
        logger.error(error.message);
      }
      process.exit(1);
    }
  });
