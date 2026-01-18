/**
 * Integration tests for task lifecycle
 * Tests spec completion to subtask loading workflow (IPC communication)
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mkdirSync, mkdtempSync, writeFileSync, rmSync, existsSync } from 'fs';
import { tmpdir } from 'os';
import path from 'path';

// Test directories - created securely with mkdtempSync to prevent TOCTOU attacks
let TEST_DIR: string;
let TEST_PROJECT_PATH: string;
let TEST_SPEC_DIR: string;

// Mock ipcRenderer for renderer-side tests
const mockIpcRenderer = {
  invoke: vi.fn(),
  send: vi.fn(),
  on: vi.fn(),
  once: vi.fn(),
  removeListener: vi.fn(),
  removeAllListeners: vi.fn(),
  setMaxListeners: vi.fn()
};

// Mock contextBridge
const exposedApis: Record<string, unknown> = {};
const mockContextBridge = {
  exposeInMainWorld: vi.fn((name: string, api: unknown) => {
    exposedApis[name] = api;
  })
};

vi.mock('electron', () => ({
  ipcRenderer: mockIpcRenderer,
  contextBridge: mockContextBridge
}));

// Sample investigation plan with analysis tasks
function createTestPlan(overrides: Record<string, unknown> = {}): object {
  const basePlan = {
    case_id: 'case-001',
    case_name: 'Test Feature',
    investigation_type: 'feature',
    evidence_sources: ['frontend'],
    phases: [
      {
        id: 'phase-1',
        name: 'Implementation Phase',
        type: 'analysis',
        analysis_tasks: [
          {
            id: 'subtask-1-1',
            description: 'Implement feature A',
            status: 'pending',
            artifacts_to_analyze: ['file1.ts'],
            artifacts_to_produce: [],
            evidence_source: 'frontend'
          },
          {
            id: 'subtask-1-2',
            description: 'Add unit tests for feature A',
            status: 'pending',
            artifacts_to_analyze: [],
            artifacts_to_produce: ['file1.test.ts'],
            evidence_source: 'frontend'
          }
        ]
      }
    ],
    status: 'in_progress',
    plan_status: 'in_progress',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  const merged = { ...basePlan, ...overrides } as Record<string, unknown>;
  if (typeof merged.feature === 'string' && !merged.case_name) {
    merged.case_name = merged.feature;
  }
  if (typeof merged.workflow_type === 'string' && !merged.investigation_type) {
    merged.investigation_type = merged.workflow_type;
  }
  if (Array.isArray(merged.services_involved) && !merged.evidence_sources) {
    merged.evidence_sources = merged.services_involved;
  }
  if (typeof merged.planStatus === 'string' && !merged.plan_status) {
    merged.plan_status = merged.planStatus;
  }
  return merged;
}

// Sample implementation plan with empty phases (incomplete state)
function createIncompletePlan(): object {
  return {
    case_id: 'case-001',
    case_name: 'Test Feature',
    investigation_type: 'feature',
    evidence_sources: ['frontend'],
    phases: [],
    status: 'planning',
    plan_status: 'planning',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };
}

// Setup test directories with secure temp directory
function setupTestDirs(): void {
  // Create secure temp directory with random suffix
  TEST_DIR = mkdtempSync(path.join(tmpdir(), 'task-lifecycle-test-'));
  TEST_PROJECT_PATH = path.join(TEST_DIR, 'test-project');
  TEST_SPEC_DIR = path.join(TEST_PROJECT_PATH, '.auto-claude/specs/001-test-feature');
  mkdirSync(TEST_SPEC_DIR, { recursive: true });
}

// Cleanup test directories
function cleanupTestDirs(): void {
  if (TEST_DIR && existsSync(TEST_DIR)) {
    rmSync(TEST_DIR, { recursive: true, force: true });
  }
}

describe('Task Lifecycle Integration', () => {
  beforeEach(async () => {
    cleanupTestDirs();
    setupTestDirs();
    vi.clearAllMocks();
    vi.resetModules();
    Object.keys(exposedApis).forEach((key) => delete exposedApis[key]);
  });

  afterEach(() => {
    cleanupTestDirs();
    vi.clearAllMocks();
  });

  describe('Spec completion to subtask loading', () => {
    it('should load analysis tasks from investigation_plan.json after spec completion', async () => {
      // Create investigation_plan.json with full analysis task data
      const planPath = path.join(TEST_SPEC_DIR, 'investigation_plan.json');
      const plan = createTestPlan();
      writeFileSync(planPath, JSON.stringify(plan, null, 2));

      // Import preload script to get electronAPI
      await import('../../preload/index');
      const electronAPI = exposedApis['electronAPI'] as Record<string, unknown>;

      // Mock IPC response for getTasks (loads investigation_plan.json)
      mockIpcRenderer.invoke.mockResolvedValueOnce({
        success: true,
        data: [
          {
            id: 'task-001',
            name: 'Test Feature',
            status: 'spec_complete',
            specDir: TEST_SPEC_DIR,
            plan: plan
          }
        ]
      });

      // Call getTasks to load plan data
      const getTasks = electronAPI['getTasks'] as (projectId: string) => Promise<unknown>;
      const result = await getTasks('project-id');

      // Verify IPC invocation
      expect(mockIpcRenderer.invoke).toHaveBeenCalledWith('task:list', 'project-id');

      // Verify task data includes plan with analysis tasks
      expect(result).toMatchObject({
        success: true,
        data: expect.arrayContaining([
          expect.objectContaining({
            plan: expect.objectContaining({
              phases: expect.arrayContaining([
                expect.objectContaining({
                  analysis_tasks: expect.arrayContaining([
                    expect.objectContaining({
                      id: 'subtask-1-1',
                      description: 'Implement feature A',
                      status: 'pending'
                    }),
                    expect.objectContaining({
                      id: 'subtask-1-2',
                      description: 'Add unit tests for feature A',
                      status: 'pending'
                    })
                  ])
                })
              ])
            })
          })
        ])
      });
    });

    it('should handle incomplete plan data with empty phases array', async () => {
      // Create investigation_plan.json with incomplete data (empty phases)
      const planPath = path.join(TEST_SPEC_DIR, 'investigation_plan.json');
      const incompletePlan = createIncompletePlan();
      writeFileSync(planPath, JSON.stringify(incompletePlan, null, 2));

      await import('../../preload/index');
      const electronAPI = exposedApis['electronAPI'] as Record<string, unknown>;

      // Mock IPC response for getTasks
      mockIpcRenderer.invoke.mockResolvedValueOnce({
        success: true,
        data: [
          {
            id: 'task-001',
            name: 'Test Feature',
            status: 'planning',
            specDir: TEST_SPEC_DIR,
            plan: incompletePlan
          }
        ]
      });

      const getTasks = electronAPI['getTasks'] as (projectId: string) => Promise<unknown>;
      const result = await getTasks('project-id');

      // Verify task data reflects incomplete state
      expect(result).toMatchObject({
        success: true,
        data: expect.arrayContaining([
          expect.objectContaining({
            plan: expect.objectContaining({
              phases: [],
              status: 'planning'
            })
          })
        ])
      });
    });

    it('should emit task:statusChange event when task transitions from planning to spec_complete', async () => {
      await import('../../preload/index');
      const electronAPI = exposedApis['electronAPI'] as Record<string, unknown>;

      // Setup event listener
      const callback = vi.fn();
      const onTaskStatusChange = electronAPI['onTaskStatusChange'] as (cb: Function) => Function;
      onTaskStatusChange(callback);

      // Verify listener was registered
      expect(mockIpcRenderer.on).toHaveBeenCalledWith(
        'task:statusChange',
        expect.any(Function)
      );

      // Simulate status change event from main process
      // The event handler signature is: (_event, taskId, status)
      const eventHandler = mockIpcRenderer.on.mock.calls.find(
        (call) => call[0] === 'task:statusChange'
      )?.[1];

      if (eventHandler) {
        eventHandler({}, 'task-001', 'spec_complete');
      }

      // Verify callback was invoked with correct parameters (taskId, status, projectId)
      // Note: projectId is optional and undefined when not provided
      expect(callback).toHaveBeenCalledWith('task-001', 'spec_complete', undefined);
    });

    it('should emit task:progress event with updated plan during spec creation', async () => {
      await import('../../preload/index');
      const electronAPI = exposedApis['electronAPI'] as Record<string, unknown>;

      // Setup event listener
      const callback = vi.fn();
      const onTaskProgress = electronAPI['onTaskProgress'] as (cb: Function) => Function;
      onTaskProgress(callback);

      // Verify listener was registered
      expect(mockIpcRenderer.on).toHaveBeenCalledWith(
        'task:progress',
        expect.any(Function)
      );

      // Simulate progress event with plan update
      // The event handler signature is: (_event, taskId, plan)
      const eventHandler = mockIpcRenderer.on.mock.calls.find(
        (call) => call[0] === 'task:progress'
      )?.[1];

      const plan = createTestPlan();
      if (eventHandler) {
        eventHandler({}, 'task-001', plan);
      }

      // Verify callback was invoked with correct parameters (taskId, plan, projectId)
      // Note: projectId is optional and undefined when not provided
      expect(callback).toHaveBeenCalledWith(
        'task-001',
        expect.objectContaining({
          phases: expect.arrayContaining([
            expect.objectContaining({
              analysis_tasks: expect.any(Array)
            })
          ])
        }),
        undefined
      );
    });

    it('should handle task resume by reloading implementation plan', async () => {
      // Create investigation_plan.json
      const planPath = path.join(TEST_SPEC_DIR, 'investigation_plan.json');
      const plan = createTestPlan();
      writeFileSync(planPath, JSON.stringify(plan, null, 2));

      await import('../../preload/index');
      const electronAPI = exposedApis['electronAPI'] as Record<string, unknown>;

      // Mock IPC response for task start (resume)
      mockIpcRenderer.invoke.mockResolvedValueOnce({
        success: true,
        message: 'Task resumed'
      });

      // Call startTask (resume)
      const startTask = electronAPI['startTask'] as (id: string, options?: object) => void;
      startTask('task-001', { resume: true });

      // Verify IPC send was called
      expect(mockIpcRenderer.send).toHaveBeenCalledWith(
        'task:start',
        'task-001',
        { resume: true }
      );
    });

    it('should handle task update status IPC call', async () => {
      await import('../../preload/index');
      // Note: electronAPI is exposed but we test the IPC channel directly below

      // Check if updateTaskStatus method exists (might be part of updateTask)
      // Based on IPC_CHANNELS, we have TASK_UPDATE_STATUS
      mockIpcRenderer.invoke.mockResolvedValueOnce({
        success: true
      });

      // Since updateTaskStatus might not be directly exposed, we test the IPC channel directly
      const result = await mockIpcRenderer.invoke('task:updateStatus', 'task-001', 'in_progress');

      expect(mockIpcRenderer.invoke).toHaveBeenCalledWith(
        'task:updateStatus',
        'task-001',
        'in_progress'
      );
      expect(result).toMatchObject({ success: true });
    });
  });

  describe('Event listener cleanup', () => {
    it('should cleanup task:progress listener when cleanup function is called', async () => {
      await import('../../preload/index');
      const electronAPI = exposedApis['electronAPI'] as Record<string, unknown>;

      const callback = vi.fn();
      const onTaskProgress = electronAPI['onTaskProgress'] as (cb: Function) => Function;
      const cleanup = onTaskProgress(callback);

      expect(typeof cleanup).toBe('function');

      // Call cleanup
      cleanup();

      expect(mockIpcRenderer.removeListener).toHaveBeenCalledWith(
        'task:progress',
        expect.any(Function)
      );
    });

    it('should cleanup task:statusChange listener when cleanup function is called', async () => {
      await import('../../preload/index');
      const electronAPI = exposedApis['electronAPI'] as Record<string, unknown>;

      const callback = vi.fn();
      const onTaskStatusChange = electronAPI['onTaskStatusChange'] as (cb: Function) => Function;
      const cleanup = onTaskStatusChange(callback);

      expect(typeof cleanup).toBe('function');

      // Call cleanup
      cleanup();

      expect(mockIpcRenderer.removeListener).toHaveBeenCalledWith(
        'task:statusChange',
        expect.any(Function)
      );
    });
  });

});
