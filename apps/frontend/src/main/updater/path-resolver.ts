/**
 * Path resolution utilities for Auto Sleuth updater
 */

import { existsSync, readFileSync } from 'fs';
import path from 'path';
import { app } from 'electron';

/**
 * Get the path to the bundled backend source
 */
export function getBundledSourcePath(): string {
  // In production, use app resources
  // In development, use the repo's apps/backend folder
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'backend');
  }

  // Development mode - look for backend in various locations
  const possiblePaths = [
    // New structure: apps/frontend -> apps/backend
    path.join(app.getAppPath(), '..', 'backend'),
    path.join(app.getAppPath(), '..', '..', 'apps', 'backend'),
    path.join(process.cwd(), 'apps', 'backend'),
    path.join(process.cwd(), '..', 'backend')
  ];

  for (const p of possiblePaths) {
    // Validate it's a proper backend source (must have runners/case_runner.py or legacy runners/spec_runner.py)
    const caseRunner = path.join(p, 'runners', 'case_runner.py');
    const specRunner = path.join(p, 'runners', 'spec_runner.py');
    if (existsSync(p) && (existsSync(caseRunner) || existsSync(specRunner))) {
      return p;
    }
  }

  // Fallback - warn if this path is also invalid
  const fallback = path.join(app.getAppPath(), '..', 'backend');
  const fallbackCaseRunner = path.join(fallback, 'runners', 'case_runner.py');
  const fallbackSpecRunner = path.join(fallback, 'runners', 'spec_runner.py');
  if (!existsSync(fallbackCaseRunner) && !existsSync(fallbackSpecRunner)) {
    console.warn(
      `[path-resolver] No valid backend source found in development paths, fallback "${fallback}" may be invalid`
    );
  }
  return fallback;
}

/**
 * Get the path for storing downloaded updates
 */
export function getUpdateCachePath(): string {
  const autoSleuthUpdates = path.join(app.getPath('userData'), 'auto-sleuth-updates');
  const legacyUpdates = path.join(app.getPath('userData'), 'auto-claude-updates');

  if (existsSync(autoSleuthUpdates)) {
    return autoSleuthUpdates;
  }

  if (existsSync(legacyUpdates)) {
    return legacyUpdates;
  }

  return autoSleuthUpdates;
}

/**
 * Get the effective source path (considers override from updates and settings)
 */
export function getEffectiveSourcePath(): string {
  // First, check user settings for configured autoBuildPath
  try {
    const settingsPath = path.join(app.getPath('userData'), 'settings.json');
    if (existsSync(settingsPath)) {
      const settings = JSON.parse(readFileSync(settingsPath, 'utf-8'));
      if (settings.autoBuildPath && existsSync(settings.autoBuildPath)) {
        // Validate it's a proper backend source (must have runners/case_runner.py or legacy runners/spec_runner.py)
        const caseRunner = path.join(settings.autoBuildPath, 'runners', 'case_runner.py');
        const specRunner = path.join(settings.autoBuildPath, 'runners', 'spec_runner.py');
        if (existsSync(caseRunner) || existsSync(specRunner)) {
          return settings.autoBuildPath;
        }
        // Invalid path - log warning and fall through to auto-detection
        console.warn(
          `[path-resolver] Configured autoBuildPath "${settings.autoBuildPath}" is missing runners/case_runner.py or legacy runners/spec_runner.py, falling back to bundled source`
        );
      }
    }
  } catch {
    // Ignore settings read errors
  }

  if (app.isPackaged) {
    // Check for user-updated source first
    const overridePath = path.join(app.getPath('userData'), 'backend-source');
    const overrideCaseRunner = path.join(overridePath, 'runners', 'case_runner.py');
    const overrideSpecRunner = path.join(overridePath, 'runners', 'spec_runner.py');
    if (existsSync(overridePath) && (existsSync(overrideCaseRunner) || existsSync(overrideSpecRunner))) {
      return overridePath;
    }
  }

  return getBundledSourcePath();
}

/**
 * Get the path where updates should be installed
 */
export function getUpdateTargetPath(): string {
  if (app.isPackaged) {
    // For packaged apps, store in userData as a source override
    return path.join(app.getPath('userData'), 'backend-source');
  } else {
    // In development, update the actual source
    return getBundledSourcePath();
  }
}
