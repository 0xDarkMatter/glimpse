# Glimpse - Remote Viewing Testing CLI

A professional CLI application for conducting Remote Viewing (RV) testing sessions with random target images.

## Overview

Glimpse is a command-line tool designed for Remote Viewing practitioners and researchers. It creates RV sessions with randomly selected target images from Unsplash, generates unique session codes using Crockford's Base32 encoding, and enforces time-based reveal mechanisms to ensure proper blind testing protocols.

## Features

- **Session Management**: Create, list, and manage RV testing sessions
- **Random Target Images**: Fetch random images from Unsplash API
- **Unique Session Codes**: Generate Crockford's Base32 codes (format: XXXX-XXXX)
- **Time-Based Reveals**: Automatically enable reveals after specified duration
- **Force Reveal**: Override time restrictions for testing purposes
- **Persistent Storage**: Sessions stored as JSON files
- **Status Tracking**: Monitor session status and time remaining

## Installation

### Prerequisites

- Node.js 18.0.0 or higher
- npm or yarn
- Unsplash API access key (free at [unsplash.com/developers](https://unsplash.com/developers))

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Glimpse
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your Unsplash API key:
```
UNSPLASH_ACCESS_KEY=your_actual_key_here
```

4. Build the project:
```bash
npm run build
```

5. (Optional) Link globally for system-wide access:
```bash
npm link
```

## Usage

### Create a New Session

Create an RV session with a 60-minute duration (default):
```bash
glimpse create
```

Create a session with custom duration:
```bash
glimpse create --duration 120
```

**Output:**
```
Session Code: AB3D-X7K2
Created: 2025-01-15 14:30:00
Reveal At: 2025-01-15 15:30:00
Duration: 60 minutes

Record your impressions, then use:
glimpse reveal AB3D-X7K2
```

### List Sessions

List all active (unrevealed) sessions:
```bash
glimpse list
```

List all sessions including revealed ones:
```bash
glimpse list --all
```

List only revealed sessions:
```bash
glimpse list --revealed
```

### Check Session Status

Check the status of a specific session:
```bash
glimpse status AB3D-X7K2
```

### Reveal Target

Reveal the target when time has elapsed:
```bash
glimpse reveal AB3D-X7K2
```

Force reveal before time expires (for testing):
```bash
glimpse reveal AB3D-X7K2 --force
```

## Project Structure

```
Glimpse/
├── src/
│   ├── commands/           # CLI command implementations
│   │   ├── create.ts       # Create new sessions
│   │   ├── list.ts         # List sessions
│   │   ├── reveal.ts       # Reveal targets
│   │   └── status.ts       # Check session status
│   ├── services/           # Business logic services
│   │   ├── unsplash-service.ts   # Unsplash API integration
│   │   └── storage-service.ts    # JSON storage adapter
│   ├── utils/              # Utility functions
│   │   ├── code-generator.ts     # Crockford Base32 generator
│   │   └── logger.ts             # Logging utility
│   ├── types/              # TypeScript type definitions
│   │   └── index.ts
│   └── index.ts            # CLI entry point
├── tests/                  # Test files
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── config/                 # Configuration files
│   └── default.json
├── data/                   # Session storage
│   └── sessions/           # Individual session JSON files
├── logs/                   # Application logs
├── dist/                   # Compiled JavaScript (gitignored)
├── .env                    # Environment variables (gitignored)
├── .env.example            # Environment template
├── package.json            # Dependencies and scripts
├── tsconfig.json           # TypeScript configuration
└── README.md               # This file
```

## Development

### Scripts

- `npm run dev` - Run in development mode with ts-node
- `npm run build` - Compile TypeScript to JavaScript
- `npm run watch` - Watch mode for development
- `npm test` - Run tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Generate test coverage report
- `npm run lint` - Lint code with ESLint
- `npm run lint:fix` - Auto-fix linting issues
- `npm run format` - Format code with Prettier
- `npm run clean` - Remove build artifacts

### Adding New Commands

1. Create a new file in `src/commands/`
2. Export a Commander.js Command instance
3. Import and register in `src/index.ts`

Example:
```typescript
import { Command } from 'commander';

export const myCommand = new Command('mycommand')
  .description('My command description')
  .action(async () => {
    // Implementation
  });
```

## Architecture

### Services Layer

**UnsplashService**: Handles API communication with Unsplash
- Fetches random images
- Validates API connection
- Error handling and retries

**JsonStorageService**: Manages session persistence
- CRUD operations for sessions
- File-based JSON storage
- Automatic directory creation

### Utilities

**Code Generator**: Crockford's Base32 implementation
- Cryptographically secure random generation
- Validation and normalization
- Customizable format

**Logger**: Structured logging
- Multiple log levels (DEBUG, INFO, WARN, ERROR)
- Colored console output
- File logging support (future)

## Future Enhancements

- SQLite database backend option
- Additional image sources (Pexels, Pixabay)
- Session history archiving
- Statistical analysis of RV sessions
- Export sessions to CSV/PDF
- Web dashboard for session management
- Multi-user support
- Session notes and feedback recording

## API Keys

### Unsplash

1. Sign up at [unsplash.com/developers](https://unsplash.com/developers)
2. Create a new application
3. Copy the "Access Key"
4. Add to `.env` as `UNSPLASH_ACCESS_KEY`

Free tier: 50 requests per hour

## License

MIT

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure linting passes
5. Submit a pull request

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

## Acknowledgments

- Unsplash API for providing high-quality random images
- Commander.js for CLI framework
- TypeScript community for excellent tooling
