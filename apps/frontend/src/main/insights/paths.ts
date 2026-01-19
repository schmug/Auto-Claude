import path from 'path';
import { existsSync } from 'fs';

const INSIGHTS_DIR = '.auto-sleuth/insights';
const LEGACY_INSIGHTS_DIR = '.auto-claude/insights';
const SESSIONS_DIR = 'sessions';
const CURRENT_SESSION_FILE = 'current_session.json';

/**
 * Path utilities for insights service
 * Provides consistent path resolution for sessions and insights data
 */
export class InsightsPaths {
  /**
   * Get insights directory path for a project
   */
  getInsightsDir(projectPath: string): string {
    const autoSleuthPath = path.join(projectPath, INSIGHTS_DIR);
    if (existsSync(autoSleuthPath)) {
      return autoSleuthPath;
    }

    const legacyPath = path.join(projectPath, LEGACY_INSIGHTS_DIR);
    if (existsSync(legacyPath)) {
      return legacyPath;
    }

    return autoSleuthPath;
  }

  /**
   * Get sessions directory path for a project
   */
  getSessionsDir(projectPath: string): string {
    return path.join(this.getInsightsDir(projectPath), SESSIONS_DIR);
  }

  /**
   * Get session file path for a specific session
   */
  getSessionPath(projectPath: string, sessionId: string): string {
    return path.join(this.getSessionsDir(projectPath), `${sessionId}.json`);
  }

  /**
   * Get current session pointer file path
   */
  getCurrentSessionPath(projectPath: string): string {
    return path.join(this.getInsightsDir(projectPath), CURRENT_SESSION_FILE);
  }

  /**
   * Get old session path for migration
   */
  getOldSessionPath(projectPath: string): string {
    return path.join(this.getInsightsDir(projectPath), 'session.json');
  }
}
