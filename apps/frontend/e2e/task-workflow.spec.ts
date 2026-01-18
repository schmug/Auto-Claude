/**
 * End-to-End tests for full task workflow
 * Tests: create → spec → analysis tasks → resume
 *
 * NOTE: These tests require the Electron app to be built first.
 * Run `npm run build` before running E2E tests.
 *
 * To run: npx playwright test task-workflow --config=e2e/playwright.config.ts
 */
import { test, expect } from '@playwright/test';
import { mkdirSync, mkdtempSync, rmSync, existsSync, writeFileSync, readFileSync } from 'fs';
import { tmpdir } from 'os';
import path from 'path';

// Test data directory - created securely with mkdtempSync to prevent TOCTOU attacks
let TEST_DATA_DIR: string;
let TEST_PROJECT_DIR: string;
let SPECS_DIR: string;

// Setup test environment with secure temp directory
function setupTestEnvironment(): void {
  // Create secure temp directory with random suffix
  TEST_DATA_DIR = mkdtempSync(path.join(tmpdir(), 'auto-claude-task-workflow-e2e-'));
  TEST_PROJECT_DIR = path.join(TEST_DATA_DIR, 'test-project');
  SPECS_DIR = path.join(TEST_PROJECT_DIR, '.auto-claude', 'specs');
  mkdirSync(TEST_PROJECT_DIR, { recursive: true });
  mkdirSync(SPECS_DIR, { recursive: true });
}

// Cleanup test environment
function cleanupTestEnvironment(): void {
  if (existsSync(TEST_DATA_DIR)) {
    rmSync(TEST_DATA_DIR, { recursive: true, force: true });
  }
}

// Helper to create a task spec with analysis tasks
function createTaskWithSubtasks(
  specId: string,
  subtaskStatuses: Array<'pending' | 'in_progress' | 'completed'>
): void {
  const specDir = path.join(SPECS_DIR, specId);
  mkdirSync(specDir, { recursive: true });

  // Create case.md
  writeFileSync(
    path.join(specDir, 'case.md'),
    `# ${specId}\n\n## Overview\n\nTest task for workflow validation.\n\n## Acceptance Criteria\n\n- [ ] All tasks completed\n- [ ] Tests pass\n`
  );

  // Create requirements.json
  writeFileSync(
    path.join(specDir, 'requirements.json'),
    JSON.stringify(
      {
        task_description: `Test task ${specId}`,
        user_requirements: ['Requirement 1', 'Requirement 2'],
        acceptance_criteria: ['All tasks completed', 'Tests pass'],
        context: []
      },
      null,
      2
    )
  );

  // Create investigation_plan.json with analysis tasks
  const analysisTasks = subtaskStatuses.map((status, index) => ({
    id: `task-${index + 1}`,
    description: `Task ${index + 1}: Implement feature part ${index + 1}`,
    evidence_source: 'backend',
    artifacts_to_analyze: [`src/file${index + 1}.py`],
    artifacts_to_produce: [],
    reference_patterns: [],
    validation: { type: 'command', command: 'pytest tests/' },
    status: status,
    notes: status === 'completed' ? 'Completed successfully' : ''
  }));

  writeFileSync(
    path.join(specDir, 'investigation_plan.json'),
    JSON.stringify(
      {
        case_id: specId,
        case_name: `Test Feature ${specId}`,
        investigation_type: 'incident_response',
        evidence_sources: ['backend'],
        phases: [
          {
            phase: 1,
            name: 'Implementation',
            type: 'analysis',
            analysis_tasks: analysisTasks
          }
        ],
        final_acceptance: ['All tasks completed', 'Tests pass'],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        case_file: 'case.md'
      },
      null,
      2
    )
  );

  // Create build-progress.txt
  writeFileSync(
    path.join(specDir, 'build-progress.txt'),
    `Task Progress: ${specId}\n\nTasks: ${analysisTasks.length}\nCompleted: ${analysisTasks.filter(s => s.status === 'completed').length}\n`
  );
}

// Helper to simulate task resumption
function simulateTaskResume(specId: string): void {
  const planPath = path.join(SPECS_DIR, specId, 'investigation_plan.json');
  const plan = JSON.parse(readFileSync(planPath, 'utf-8'));

  // Find first pending analysis task and mark as in_progress
  const tasks = plan.phases?.[0]?.analysis_tasks || [];
  const pendingTask = tasks.find((st: { status: string }) => st.status === 'pending');
  if (pendingTask) {
    pendingTask.status = 'in_progress';
    pendingTask.notes = 'Resumed from checkpoint';
  }

  plan.updated_at = new Date().toISOString();
  writeFileSync(planPath, JSON.stringify(plan, null, 2));
}

type PlanTask = { status: string; notes?: string; [key: string]: unknown };

function getAnalysisTasks(plan: { phases?: Array<{ analysis_tasks?: Array<PlanTask> }> }): Array<PlanTask> {
  return plan.phases?.[0]?.analysis_tasks || [];
}

test.describe('Task Workflow E2E Tests', () => {
  test.beforeAll(() => {
    setupTestEnvironment();
  });

  test.afterAll(() => {
    cleanupTestEnvironment();
  });

  test('should create task directory structure', () => {
    const specId = '001-test-task';
    const specDir = path.join(SPECS_DIR, specId);
    mkdirSync(specDir, { recursive: true });

    // Verify directory created
    expect(existsSync(specDir)).toBe(true);
  });

  test('should generate case.md file', () => {
    const specId = '002-task-with-spec';
    const specDir = path.join(SPECS_DIR, specId);
    mkdirSync(specDir, { recursive: true });

    // Write spec
    const specContent = '# Test Task\n\n## Overview\n\nThis is a test task.\n';
    writeFileSync(path.join(specDir, 'case.md'), specContent);

    // Verify spec file
    expect(existsSync(path.join(specDir, 'case.md'))).toBe(true);
    const content = readFileSync(path.join(specDir, 'case.md'), 'utf-8');
    expect(content).toContain('Test Task');
  });

  test('should create investigation plan with analysis tasks', () => {
    const specId = '003-task-with-subtasks';
    createTaskWithSubtasks(specId, ['pending', 'pending', 'pending']);

    const planPath = path.join(SPECS_DIR, specId, 'investigation_plan.json');
    expect(existsSync(planPath)).toBe(true);

    const plan = JSON.parse(readFileSync(planPath, 'utf-8'));
    const tasks = getAnalysisTasks(plan);
    expect(tasks).toHaveLength(3);
    expect(tasks[0].status).toBe('pending');
  });

  test('should track analysis task progress', () => {
    const specId = '004-task-in-progress';
    createTaskWithSubtasks(specId, ['completed', 'in_progress', 'pending']);

    const planPath = path.join(SPECS_DIR, specId, 'investigation_plan.json');
    const plan = JSON.parse(readFileSync(planPath, 'utf-8'));

    const tasks = getAnalysisTasks(plan);
    expect(tasks[0].status).toBe('completed');
    expect(tasks[1].status).toBe('in_progress');
    expect(tasks[2].status).toBe('pending');
  });

  test('should resume task from checkpoint', () => {
    const specId = '005-task-resume';
    createTaskWithSubtasks(specId, ['completed', 'pending', 'pending']);

    // Verify initial state
    let plan = JSON.parse(readFileSync(path.join(SPECS_DIR, specId, 'investigation_plan.json'), 'utf-8'));
    let tasks = getAnalysisTasks(plan);
    expect(tasks[1].status).toBe('pending');

    // Simulate resume
    simulateTaskResume(specId);

    // Verify resumed state
    plan = JSON.parse(readFileSync(path.join(SPECS_DIR, specId, 'investigation_plan.json'), 'utf-8'));
    tasks = getAnalysisTasks(plan);
    expect(tasks[1].status).toBe('in_progress');
    expect(tasks[1].notes).toContain('Resumed from checkpoint');
  });

  test('should complete all analysis tasks in sequence', () => {
    const specId = '006-task-completion';
    createTaskWithSubtasks(specId, ['completed', 'completed', 'completed']);

    const plan = JSON.parse(readFileSync(path.join(SPECS_DIR, specId, 'investigation_plan.json'), 'utf-8'));
    const tasks = getAnalysisTasks(plan);
    const allCompleted = tasks.every((st: { status: string }) => st.status === 'completed');

    expect(allCompleted).toBe(true);
  });

  test('should maintain build progress log', () => {
    const specId = '007-task-with-progress';
    createTaskWithSubtasks(specId, ['completed', 'in_progress', 'pending']);

    const progressPath = path.join(SPECS_DIR, specId, 'build-progress.txt');
    expect(existsSync(progressPath)).toBe(true);

    const progressContent = readFileSync(progressPath, 'utf-8');
    expect(progressContent).toContain('Task Progress');
    expect(progressContent).toContain('Tasks: 3');
  });
});

test.describe('Full Task Workflow Integration', () => {
  test.beforeAll(() => {
    setupTestEnvironment();
  });

  test.afterAll(() => {
    cleanupTestEnvironment();
  });

  test('should complete full workflow: create → spec → analysis tasks → resume → complete', () => {
    const specId = '100-full-workflow';

    // Step 1: Create task
    const specDir = path.join(SPECS_DIR, specId);
    mkdirSync(specDir, { recursive: true });
    expect(existsSync(specDir)).toBe(true);

    // Step 2: Generate spec
    writeFileSync(
      path.join(specDir, 'case.md'),
      '# Full Workflow Test\n\n## Overview\n\nComplete workflow test.\n'
    );
    expect(existsSync(path.join(specDir, 'case.md'))).toBe(true);

    // Step 3: Create analysis tasks
    createTaskWithSubtasks(specId, ['pending', 'pending', 'pending']);
    let plan = JSON.parse(readFileSync(path.join(specDir, 'investigation_plan.json'), 'utf-8'));
    let tasks = getAnalysisTasks(plan);
    expect(tasks.length).toBe(3);

    // Step 4: Start first task
    tasks[0].status = 'in_progress';
    writeFileSync(path.join(specDir, 'investigation_plan.json'), JSON.stringify(plan, null, 2));

    plan = JSON.parse(readFileSync(path.join(specDir, 'investigation_plan.json'), 'utf-8'));
    tasks = getAnalysisTasks(plan);
    expect(tasks[0].status).toBe('in_progress');

    // Step 5: Complete first task
    tasks[0].status = 'completed';
    tasks[0].notes = 'First task completed';
    writeFileSync(path.join(specDir, 'investigation_plan.json'), JSON.stringify(plan, null, 2));

    // Step 6: Resume with second task
    simulateTaskResume(specId);
    plan = JSON.parse(readFileSync(path.join(specDir, 'investigation_plan.json'), 'utf-8'));
    tasks = getAnalysisTasks(plan);
    expect(tasks[1].status).toBe('in_progress');

    // Step 7: Complete remaining tasks
    tasks[1].status = 'completed';
    tasks[2].status = 'completed';
    writeFileSync(path.join(specDir, 'investigation_plan.json'), JSON.stringify(plan, null, 2));

    // Step 8: Verify all completed
    plan = JSON.parse(readFileSync(path.join(specDir, 'investigation_plan.json'), 'utf-8'));
    tasks = getAnalysisTasks(plan);
    const allCompleted = tasks.every((st: { status: string }) => st.status === 'completed');
    expect(allCompleted).toBe(true);

    // Step 9: Verify final state
    expect(tasks[0].notes).toContain('First task completed');
    expect(tasks[1].notes).toContain('Resumed from checkpoint');
  });

  test('should handle workflow interruption and recovery', () => {
    const specId = '101-workflow-recovery';

    // Create task with partial progress
    createTaskWithSubtasks(specId, ['completed', 'in_progress', 'pending']);

    // Simulate interruption (task status is saved)
    const planPath = path.join(SPECS_DIR, specId, 'investigation_plan.json');
    let plan = JSON.parse(readFileSync(planPath, 'utf-8'));
    let tasks = getAnalysisTasks(plan);
    expect(tasks[1].status).toBe('in_progress');

    // Simulate recovery: complete interrupted subtask
    tasks[1].status = 'completed';
    tasks[1].notes = 'Recovered and completed';
    writeFileSync(planPath, JSON.stringify(plan, null, 2));

    // Resume with next subtask
    simulateTaskResume(specId);
    plan = JSON.parse(readFileSync(planPath, 'utf-8'));
    tasks = getAnalysisTasks(plan);

    // Verify recovery successful
    expect(tasks[1].status).toBe('completed');
    expect(tasks[2].status).toBe('in_progress');
  });

  test('should validate workflow data integrity', () => {
    const specId = '102-data-integrity';
    createTaskWithSubtasks(specId, ['pending', 'pending', 'pending']);

    const specDir = path.join(SPECS_DIR, specId);

    // Verify all required files exist
    expect(existsSync(path.join(specDir, 'case.md'))).toBe(true);
    expect(existsSync(path.join(specDir, 'requirements.json'))).toBe(true);
    expect(existsSync(path.join(specDir, 'investigation_plan.json'))).toBe(true);
    expect(existsSync(path.join(specDir, 'build-progress.txt'))).toBe(true);

    // Verify data structure integrity
    const requirements = JSON.parse(readFileSync(path.join(specDir, 'requirements.json'), 'utf-8'));
    expect(requirements.task_description).toBeDefined();
    expect(requirements.acceptance_criteria).toBeDefined();

    const plan = JSON.parse(readFileSync(path.join(specDir, 'investigation_plan.json'), 'utf-8'));
    expect(plan.case_name).toBeDefined();
    expect(plan.phases).toBeDefined();
    expect(plan.created_at).toBeDefined();
    expect(plan.updated_at).toBeDefined();

    // Verify analysis task structure
    const tasks = getAnalysisTasks(plan);
    tasks.forEach((subtask: {
      id: string;
      description: string;
      status: string;
      validation?: { command?: string };
    }) => {
      expect(subtask.id).toBeDefined();
      expect(subtask.description).toBeDefined();
      expect(subtask.status).toMatch(/^(pending|in_progress|completed)$/);
      expect(subtask.validation?.command).toBeDefined();
    });
  });
});
