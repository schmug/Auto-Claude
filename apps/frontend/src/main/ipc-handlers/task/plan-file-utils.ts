/**
 * Plan File Utilities
 *
 * Provides thread-safe operations for reading and writing investigation_plan.json files.
 * Uses an in-memory lock to serialize updates and prevent race conditions when multiple
 * IPC handlers try to update the same plan file concurrently.
 *
 * IMPORTANT LIMITATION:
 * The synchronous function `persistPlanStatusSync` does NOT participate in the locking
 * mechanism. It bypasses the async lock entirely, which means:
 * - It can race with concurrent async operations (persistPlanStatus, updatePlanFile, etc.)
 * - It should ONLY be used when you are certain no async operations are pending on the same file
 * - Prefer using the async `persistPlanStatus` whenever possible
 *
 * If you need synchronous behavior, ensure that:
 * 1. No async plan operations are in flight for the same file path
 * 2. The calling context truly cannot use async/await (e.g., synchronous event handlers)
 */

import path from 'path';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { AUTO_BUILD_PATHS, getSpecsDir } from '../../../shared/constants';
import type { TaskStatus, Project, Task } from '../../../shared/types';
import { projectStore } from '../../project-store';

// In-memory locks for plan file operations
// Key: plan file path, Value: Promise chain for serializing operations
const planLocks = new Map<string, Promise<void>>();

/**
 * Serialize operations on a specific plan file to prevent race conditions.
 * Each operation waits for the previous one to complete before starting.
 */
async function withPlanLock<T>(planPath: string, operation: () => Promise<T>): Promise<T> {
  // Get or create the lock chain for this file
  const currentLock = planLocks.get(planPath) || Promise.resolve();

  // Create a new promise that will resolve after our operation completes
  let resolve: () => void;
  const newLock = new Promise<void>((r) => { resolve = r; });
  planLocks.set(planPath, newLock);

  try {
    // Wait for any previous operation to complete
    await currentLock;
    // Execute our operation
    return await operation();
  } finally {
    // Release the lock
    resolve!();
    // Clean up if this was the last operation
    if (planLocks.get(planPath) === newLock) {
      planLocks.delete(planPath);
    }
  }
}

/**
 * Check if an error is a "file not found" error
 */
function isFileNotFoundError(err: unknown): boolean {
  return (err as NodeJS.ErrnoException).code === 'ENOENT';
}

/**
 * Get the plan file path for a task
 */
function getCaseDirFromSpecPath(specDir: string): string | null {
  const normalized = path.normalize(specDir);
  const root = path.parse(normalized).root;
  const parts = normalized.slice(root.length).split(path.sep).filter(Boolean);

  for (let i = 0; i < parts.length - 2; i++) {
    const part = parts[i];
    if ((part === '.auto-sleuth' || part === 'auto-sleuth') && parts[i + 1] === 'cases') {
      return path.join(root, ...parts.slice(0, i + 3));
    }
  }

  return null;
}

function getCasePlanCandidates(specDir: string, projectPath?: string, specId?: string): string[] {
  const candidates: string[] = [];
  const caseDir = getCaseDirFromSpecPath(specDir);
  if (caseDir) {
    candidates.push(path.join(caseDir, AUTO_BUILD_PATHS.INVESTIGATION_PLAN));
  }

  if (projectPath && specId) {
    candidates.push(path.join(projectPath, '.auto-sleuth', 'cases', specId, AUTO_BUILD_PATHS.INVESTIGATION_PLAN));
    candidates.push(path.join(projectPath, 'auto-sleuth', 'cases', specId, AUTO_BUILD_PATHS.INVESTIGATION_PLAN));
  }

  return candidates;
}

export function resolvePlanPath(specDir: string, projectPath?: string, specId?: string): string {
  for (const candidate of getCasePlanCandidates(specDir, projectPath, specId)) {
    if (existsSync(candidate)) {
      return candidate;
    }
  }

  const investigationPlanPath = path.join(specDir, AUTO_BUILD_PATHS.INVESTIGATION_PLAN);
  if (existsSync(investigationPlanPath)) {
    return investigationPlanPath;
  }

  // Default to investigation_plan.json for new DFIR workflow
  return investigationPlanPath;
}

export function getPlanPaths(specDir: string, projectPath?: string, specId?: string): string[] {
  const paths = new Set<string>();
  const investigationPlanPath = path.join(specDir, AUTO_BUILD_PATHS.INVESTIGATION_PLAN);

  if (existsSync(investigationPlanPath)) {
    paths.add(investigationPlanPath);
  }

  for (const candidate of getCasePlanCandidates(specDir, projectPath, specId)) {
    if (existsSync(candidate)) {
      paths.add(candidate);
    }
  }

  if (paths.size === 0) {
    paths.add(investigationPlanPath);
  }

  return Array.from(paths);
}

export function getPlanPath(project: Project, task: Task): string {
  const specsBaseDir = getSpecsDir(project.autoBuildPath);
  const specDir = task.specsPath || path.join(project.path, specsBaseDir, task.specId);
  return resolvePlanPath(specDir, project.path, task.specId);
}

/**
 * Map UI TaskStatus to plan_status
 */
export function mapStatusToPlanStatus(status: TaskStatus): string {
  switch (status) {
    case 'in_progress':
      return 'in_progress';
    case 'ai_review':
    case 'human_review':
      return 'review';
    case 'pr_created':
      return 'pr_created';
    case 'done':
      return 'completed';
    default:
      return 'pending';
  }
}

/**
 * Persist task status to investigation_plan.json file.
 * This is thread-safe and prevents race conditions when multiple handlers update the same file.
 *
 * @param planPath - Path to the plan file
 * @param status - The TaskStatus to persist
 * @param projectId - Optional project ID to invalidate cache (recommended for performance)
 * @returns true if status was persisted, false if plan file doesn't exist
 */
export async function persistPlanStatus(planPath: string, status: TaskStatus, projectId?: string): Promise<boolean> {
  return withPlanLock(planPath, async () => {
    try {
      console.warn(`[plan-file-utils] Reading plan file to update status to: ${status}`, { planPath });
      // Read file directly without existence check to avoid TOCTOU race condition
      const planContent = readFileSync(planPath, 'utf-8');
      const plan = JSON.parse(planContent);

      plan.status = status;
      plan.plan_status = mapStatusToPlanStatus(status);
      if ('planStatus' in plan) {
        delete plan.planStatus;
      }
      plan.updated_at = new Date().toISOString();

      writeFileSync(planPath, JSON.stringify(plan, null, 2));
      console.warn(`[plan-file-utils] Successfully persisted status: ${status} to plan file`);

      // Invalidate tasks cache since status changed
      if (projectId) {
        projectStore.invalidateTasksCache(projectId);
      }

      return true;
    } catch (err) {
      // File not found is expected - return false
      if (isFileNotFoundError(err)) {
        console.warn(`[plan-file-utils] Plan file not found at ${planPath} - status not persisted`);
        return false;
      }
      console.warn(`[plan-file-utils] Could not persist status to ${planPath}:`, err);
      return false;
    }
  });
}

/**
 * Persist task status synchronously (for use in event handlers where async isn't practical).
 *
 * WARNING: This function bypasses the async locking mechanism entirely!
 *
 * This means it can race with concurrent async operations (persistPlanStatus, updatePlanFile,
 * createPlanIfNotExists) that may be in flight for the same file. Using this function while
 * async operations are pending can result in:
 * - Lost updates (this write may overwrite changes from an async operation, or vice versa)
 * - Corrupted JSON (if writes interleave at the filesystem level)
 * - Inconsistent state between what was written and what the async operation expected to read
 *
 * ONLY use this function when ALL of the following conditions are met:
 * 1. You are in a synchronous context that cannot use async/await (e.g., certain event handlers)
 * 2. You are certain no async plan operations are pending or in-flight for this file path
 * 3. No other code will initiate async plan operations until this function returns
 *
 * When possible, prefer using the async `persistPlanStatus` function instead, which properly
 * participates in the locking mechanism and prevents race conditions.
 *
 * @param planPath - Path to the investigation_plan.json file
 * @param status - The TaskStatus to persist
 * @param projectId - Optional project ID to invalidate cache (recommended for performance)
 * @returns true if status was persisted, false otherwise
 */
export function persistPlanStatusSync(planPath: string, status: TaskStatus, projectId?: string): boolean {
  try {
    // Read file directly without existence check to avoid TOCTOU race condition
    const planContent = readFileSync(planPath, 'utf-8');
    const plan = JSON.parse(planContent);

    plan.status = status;
    plan.plan_status = mapStatusToPlanStatus(status);
    if ('planStatus' in plan) {
      delete plan.planStatus;
    }
    plan.updated_at = new Date().toISOString();

    writeFileSync(planPath, JSON.stringify(plan, null, 2));

    // Invalidate tasks cache since status changed
    if (projectId) {
      projectStore.invalidateTasksCache(projectId);
    }

    return true;
  } catch (err) {
    // File not found is expected - return false
    if (isFileNotFoundError(err)) {
      return false;
    }
    console.warn(`[plan-file-utils] Could not persist status to ${planPath}:`, err);
    return false;
  }
}

/**
 * Read and update the plan file atomically.
 *
 * @param planPath - Path to the investigation_plan.json file
 * @param updater - Function that receives the current plan and returns the updated plan
 * @returns The updated plan, or null if the file doesn't exist
 */
export async function updatePlanFile<T extends Record<string, unknown>>(
  planPath: string,
  updater: (plan: T) => T
): Promise<T | null> {
  return withPlanLock(planPath, async () => {
    try {
      console.warn(`[plan-file-utils] Reading plan file for update`, { planPath });
      // Read file directly without existence check to avoid TOCTOU race condition
      const planContent = readFileSync(planPath, 'utf-8');
      const plan = JSON.parse(planContent) as T;

      const updatedPlan = updater(plan);
      // Add updated_at timestamp - use type assertion since T extends Record<string, unknown>
      (updatedPlan as Record<string, unknown>).updated_at = new Date().toISOString();

      writeFileSync(planPath, JSON.stringify(updatedPlan, null, 2));
      console.warn(`[plan-file-utils] Successfully updated plan file`);
      return updatedPlan;
    } catch (err) {
      // File not found is expected - return null
      if (isFileNotFoundError(err)) {
        console.warn(`[plan-file-utils] Plan file not found at ${planPath} - update skipped`);
        return null;
      }
      console.warn(`[plan-file-utils] Could not update plan at ${planPath}:`, err);
      return null;
    }
  });
}

/**
 * Create a new plan file if it doesn't exist.
 *
 * @param planPath - Path to the investigation_plan.json file
 * @param task - The task to create the plan for
 * @param status - Initial status for the plan
 */
export async function createPlanIfNotExists(
  planPath: string,
  task: Task,
  status: TaskStatus
): Promise<void> {
  return withPlanLock(planPath, async () => {
    // Try to read the file first - if it exists, do nothing
    try {
      readFileSync(planPath, 'utf-8');
      return; // File exists, nothing to do
    } catch (err) {
      if (!isFileNotFoundError(err)) {
        throw err; // Re-throw unexpected errors
      }
      // File doesn't exist, continue to create it
    }

    const plan = {
      case_id: task.specId,
      case_name: task.title,
      investigation_type: 'investigation',
      description: task.description || '',
      created_at: task.createdAt.toISOString(),
      updated_at: new Date().toISOString(),
      status: status,
      plan_status: mapStatusToPlanStatus(status),
      phases: []
    };

    // Ensure directory exists - use try/catch pattern
    const planDir = path.dirname(planPath);
    try {
      mkdirSync(planDir, { recursive: true });
    } catch (err) {
      // Directory might already exist or be created concurrently - that's fine
      if ((err as NodeJS.ErrnoException).code !== 'EEXIST') {
        throw err;
      }
    }

    writeFileSync(planPath, JSON.stringify(plan, null, 2));
  });
}

/**
 * Update task_metadata.json to add PR URL.
 * This is a simple JSON file update (no locking needed as it's rarely updated concurrently).
 *
 * @param metadataPath - Path to the task_metadata.json file
 * @param prUrl - The PR URL to add to metadata
 * @returns true if metadata was updated, false if file doesn't exist or failed
 */
export function updateTaskMetadataPrUrl(metadataPath: string, prUrl: string): boolean {
  try {
    let metadata: Record<string, unknown> = {};

    // Try to read existing metadata
    try {
      const content = readFileSync(metadataPath, 'utf-8');
      metadata = JSON.parse(content);
    } catch (err) {
      if (!isFileNotFoundError(err)) {
        throw err;
      }
      // File doesn't exist, will create new one
    }

    // Update with prUrl
    metadata.prUrl = prUrl;

    // Ensure parent directory exists before writing
    mkdirSync(path.dirname(metadataPath), { recursive: true });

    // Write back
    writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
    return true;
  } catch (err) {
    console.warn(`[plan-file-utils] Could not update metadata at ${metadataPath}:`, err);
    return false;
  }
}
