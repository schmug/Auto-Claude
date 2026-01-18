# Case Handlers Module

This directory contains the refactored case-related IPC handlers, previously consolidated in a single 1,873-line file. The code has been reorganized into smaller, focused modules for better maintainability.

## Module Structure

### Core Modules

| Module | Lines | Responsibility |
|--------|-------|----------------|
| `crud-handlers.ts` | ~428 | Case CRUD operations (Create, Read, Update, Delete, List) |
| `execution-handlers.ts` | ~553 | Case execution lifecycle (Start, Stop, Review, Status, Recovery) |
| `worktree-handlers.ts` | ~759 | Git worktree management (Status, Diff, Merge, Preview, Discard, List) |
| `logs-handlers.ts` | ~111 | Case logs operations (Get, Watch, Unwatch) |
| `shared.ts` | ~22 | Shared utilities and helper functions |
| `index.ts` | ~41 | Main module exports and registration |

### Main Entry Point

The main `task-handlers.ts` file (now 22 lines) serves as a simple re-export of the modular implementation.

## Module Responsibilities

### CRUD Handlers (`crud-handlers.ts`)
Handles basic case lifecycle operations:
- **TASK_LIST** - List all cases for a project
- **TASK_CREATE** - Create new case with case spec directory
- **TASK_DELETE** - Delete case and associated files
- **TASK_UPDATE** - Update case metadata, title, description

Features:
- Auto-generates case titles using Claude AI
- Manages attached images (save to disk, maintain references)
- Creates case spec directories with proper structure
- Updates implementation plans and requirements

### Execution Handlers (`execution-handlers.ts`)
Manages case execution lifecycle:
- **TASK_START** - Start case execution (case spec creation or implementation)
- **TASK_STOP** - Stop running case
- **TASK_REVIEW** - Approve or reject case results
- **TASK_UPDATE_STATUS** - Update case status manually
- **TASK_CHECK_RUNNING** - Check if case has active process
- **TASK_RECOVER_STUCK** - Recover cases stuck in inconsistent state

Features:
- Handles case spec creation phase vs implementation phase
- Auto-starts cases when moved to in_progress
- Intelligent recovery with subtask analysis
- File watcher integration

### Worktree Handlers (`worktree-handlers.ts`)
Manages git worktree operations:
- **TASK_WORKTREE_STATUS** - Get worktree status and git info
- **TASK_WORKTREE_DIFF** - Get detailed file-level diff
- **TASK_WORKTREE_MERGE** - Merge worktree into main branch
- **TASK_WORKTREE_MERGE_PREVIEW** - Preview merge conflicts
- **TASK_WORKTREE_DISCARD** - Discard worktree and branch
- **TASK_LIST_WORKTREES** - List all project worktrees

Features:
- Per-case spec worktree architecture (`.worktrees/{spec-name}/`)
- Smart merge with AI-powered conflict resolution
- Merge preview with conflict analysis
- Stage-only merge option (--no-commit)
- Comprehensive git statistics

### Logs Handlers (`logs-handlers.ts`)
Manages case logs and streaming:
- **TASK_LOGS_GET** - Get case logs organized by phase
- **TASK_LOGS_WATCH** - Start watching case spec for log changes
- **TASK_LOGS_UNWATCH** - Stop watching case spec

Features:
- Real-time log streaming to renderer
- Event forwarding for logs-changed and stream-chunk
- Phase-organized logs (planning, coding, validation)

### Shared Utilities (`shared.ts`)
Common helper functions:
- `findTaskAndProject()` - Locate case and project by ID

## Usage

Import the main registration function:

```typescript
import { registerTaskHandlers } from './ipc-handlers/task-handlers';

// Register all case handlers
registerTaskHandlers(agentManager, pythonEnvManager, getMainWindow);
```

## Benefits of Refactoring

### Code Quality
- **Single Responsibility**: Each module has one clear purpose
- **Readability**: Smaller files are easier to understand
- **Maintainability**: Changes are isolated to relevant modules
- **Testability**: Modules can be tested independently

### Developer Experience
- **Navigation**: Find specific handlers quickly
- **Context**: Related functionality grouped together
- **Documentation**: Clear module boundaries
- **Scalability**: Easy to add new handlers

### Metrics

| Metric | Before | After |
|--------|--------|-------|
| Main file size | 1,885 lines | 22 lines |
| Number of files | 1 | 7 (6 + index) |
| Largest module | 1,885 lines | 759 lines |
| Average module | 1,885 lines | ~314 lines |

## Dependencies

### External
- `electron` - IPC communication
- `fs` - File system operations
- `child_process` - Process management
- `path` - Path utilities

### Internal
- `../../shared/constants` - IPC channels, paths
- `../../shared/types` - TypeScript types
- `../../agent` - Agent management
- `../../project-store` - Project state
- `../../file-watcher` - File watching
- `../../task-log-service` - Log service
- `../../title-generator` - AI title generation
- `../../python-env-manager` - Python environment
- `../../auto-claude-updater` - Source paths
- `../../rate-limit-detector` - Profile environment

## Architecture Notes

### Worktree Architecture
Each case spec has its own isolated worktree at `.worktrees/{spec-name}/`:
- Enables safe parallel development
- Each case spec has dedicated branch: `auto-claude/{spec-name}`
- Branches stay local until user explicitly pushes
- User reviews in worktree before merging to main

### Status Management
Cases maintain status in `investigation_plan.json`:
- UI statuses: `backlog`, `in_progress`, `ai_review`, `human_review`, `done`
- Python statuses: `pending`, `in_progress`, `review`, `completed`
- Status mapping handled by project-store

### Recovery System
Intelligent stuck case recovery:
- Analyzes subtask completion status
- Resets interrupted subtasks to pending
- Preserves completed work for resumption
- Auto-restart option available

## Future Enhancements

Potential improvements:
- Extract more shared utilities
- Add comprehensive unit tests
- Create handler factory patterns
- Implement middleware for common operations
- Add detailed error handling utilities
