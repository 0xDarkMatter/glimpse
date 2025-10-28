#!/usr/bin/env node

import { Command } from 'commander';
import { config } from 'dotenv';
import chalk from 'chalk';
import { createCommand } from './commands/create';
import { listCommand } from './commands/list';
import { revealCommand } from './commands/reveal';
import { statusCommand } from './commands/status';

// Load environment variables
config();

const program = new Command();

program
  .name('glimpse')
  .description('CLI application for Remote Viewing testing with random target images')
  .version('0.1.0');

// Register commands
program.addCommand(createCommand);
program.addCommand(listCommand);
program.addCommand(revealCommand);
program.addCommand(statusCommand);

// Error handling
program.exitOverride();

try {
  program.parse(process.argv);
} catch (error) {
  if (error instanceof Error) {
    console.error(chalk.red(`Error: ${error.message}`));
    process.exit(1);
  }
}

// Show help if no command provided
if (!process.argv.slice(2).length) {
  program.outputHelp();
}
