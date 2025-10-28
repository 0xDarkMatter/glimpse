import * as fs from 'fs/promises';
import * as path from 'path';
import { RVSession, StorageAdapter } from '../types';
import { logger } from '../utils/logger';

export class JsonStorageService implements StorageAdapter {
  private dataDir: string;

  constructor(dataDir: string) {
    this.dataDir = dataDir;
  }

  private getSessionPath(id: string): string {
    return path.join(this.dataDir, 'sessions', `${id}.json`);
  }

  async ensureDataDirectory(): Promise<void> {
    const sessionsDir = path.join(this.dataDir, 'sessions');
    try {
      await fs.mkdir(sessionsDir, { recursive: true });
    } catch (error) {
      logger.error('Failed to create data directory:', error);
      throw error;
    }
  }

  async saveSession(session: RVSession): Promise<void> {
    await this.ensureDataDirectory();
    const filePath = this.getSessionPath(session.id);

    try {
      await fs.writeFile(filePath, JSON.stringify(session, null, 2), 'utf-8');
      logger.debug(`Session ${session.id} saved to ${filePath}`);
    } catch (error) {
      logger.error('Failed to save session:', error);
      throw new Error(`Failed to save session: ${error}`);
    }
  }

  async getSession(id: string): Promise<RVSession | null> {
    const filePath = this.getSessionPath(id);

    try {
      const data = await fs.readFile(filePath, 'utf-8');
      const session = JSON.parse(data);
      // Convert date strings back to Date objects
      session.createdAt = new Date(session.createdAt);
      session.revealAt = new Date(session.revealAt);
      if (session.revealedAt) {
        session.revealedAt = new Date(session.revealedAt);
      }
      return session;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        return null;
      }
      logger.error('Failed to read session:', error);
      throw error;
    }
  }

  async getAllSessions(): Promise<RVSession[]> {
    await this.ensureDataDirectory();
    const sessionsDir = path.join(this.dataDir, 'sessions');

    try {
      const files = await fs.readdir(sessionsDir);
      const sessions: RVSession[] = [];

      for (const file of files) {
        if (file.endsWith('.json')) {
          const id = file.replace('.json', '');
          const session = await this.getSession(id);
          if (session) {
            sessions.push(session);
          }
        }
      }

      // Sort by creation date (newest first)
      return sessions.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
    } catch (error) {
      logger.error('Failed to list sessions:', error);
      return [];
    }
  }

  async updateSession(id: string, updates: Partial<RVSession>): Promise<void> {
    const session = await this.getSession(id);
    if (!session) {
      throw new Error(`Session ${id} not found`);
    }

    const updatedSession = { ...session, ...updates };
    await this.saveSession(updatedSession);
  }

  async deleteSession(id: string): Promise<void> {
    const filePath = this.getSessionPath(id);

    try {
      await fs.unlink(filePath);
      logger.debug(`Session ${id} deleted`);
    } catch (error) {
      logger.error('Failed to delete session:', error);
      throw new Error(`Failed to delete session: ${error}`);
    }
  }
}
