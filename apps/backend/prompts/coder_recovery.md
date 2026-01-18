# RECOVERY AWARENESS ADDITIONS FOR EVIDENCE ANALYZER

## Add to STEP 1 (After loading context):

```bash
# 10. CHECK ANALYSIS ATTEMPT HISTORY (Recovery Context)
echo -e "\n=== RECOVERY CONTEXT ==="
if [ -f memory/attempt_history.json ]; then
  echo "Analysis Attempt History (for retry awareness):"
  cat memory/attempt_history.json

  # Show stuck tasks if any
  stuck_count=$(cat memory/attempt_history.json | jq '.stuck_tasks | length' 2>/dev/null || echo 0)
  if [ "$stuck_count" -gt 0 ]; then
    echo -e "\n⚠️  WARNING: Some analysis tasks are stuck and need different approaches!"
    cat memory/attempt_history.json | jq '.stuck_tasks'
  fi
else
  echo "No attempt history yet (all analysis tasks are first attempts)"
fi
echo "=== END RECOVERY CONTEXT ==="
```

## Add to STEP 5 (Before 5.1):

### 5.0: Check Recovery History for This analysis task (CRITICAL - DO THIS FIRST)

```bash
# Check if this analysis task was attempted before
TASK_ID="your-task-id"  # Replace with actual task ID from investigation_plan.json

echo "=== CHECKING ATTEMPT HISTORY FOR $TASK_ID ==="

if [ -f memory/attempt_history.json ]; then
  # Check if this task has attempts
  task_data=$(cat memory/attempt_history.json | jq ".tasks[\"$TASK_ID\"]" 2>/dev/null)

  if [ "$task_data" != "null" ]; then
    echo "⚠️⚠️⚠️ THIS ANALYSIS TASK HAS BEEN ATTEMPTED BEFORE! ⚠️⚠️⚠️"
    echo ""
    echo "Previous attempts:"
    cat memory/attempt_history.json | jq ".tasks[\"$TASK_ID\"].attempts[]"
    echo ""
    echo "CRITICAL REQUIREMENT: You MUST try a DIFFERENT analysis approach!"
    echo "Review what was tried above and explicitly choose a different strategy."
    echo ""

    # Show count
    attempt_count=$(cat memory/attempt_history.json | jq ".tasks[\"$TASK_ID\"].attempts | length" 2>/dev/null || echo 0)
    echo "This is attempt #$((attempt_count + 1))"

    if [ "$attempt_count" -ge 2 ]; then
      echo ""
      echo "⚠️  HIGH RISK: Multiple attempts already. Consider:"
      echo "  - Using a different forensic tool"
      echo "  - Analyzing a different artifact type"
      echo "  - Consulting DFIQ for alternative approaches"
      echo "  - Checking if evidence has the required data"
    fi
  else
    echo "✓ First attempt at this analysis task - no recovery context needed"
  fi
else
  echo "✓ No attempt history file - this is a fresh start"
fi

echo "=== END ATTEMPT HISTORY CHECK ==="
echo ""
```

**WHAT THIS MEANS:**

- If you see previous attempts, you are RETRYING this analysis task
- Previous attempts FAILED for a reason
- You MUST read what was tried and explicitly choose something different
- Repeating the same approach will trigger circular analysis detection

## Add to STEP 6 (After marking in_progress):

### Record Your Analysis Approach (Recovery Tracking)

**IMPORTANT: Before you run any analysis, document your approach.**

```python
# Record your analysis approach for recovery tracking
import json
from pathlib import Path
from datetime import datetime

task_id = "your-task-id"  # Your current analysis task ID
approach_description = """
Describe your analysis approach here in 2-3 sentences:
- What forensic tool are you using?
- What evidence files are you analyzing?
- What artifacts/IOCs are you hunting?

Example: "Using Volatility3 windows.netscan plugin to extract network connections
from memory dump. Will search results for known IOC IPs from iocs/all_iocs.txt.
Outputting to ./outputs/phase-1/netscan_results.json."
"""

# This will be used to detect circular analysis
approach_file = Path("memory/current_approach.txt")
approach_file.parent.mkdir(parents=True, exist_ok=True)

with open(approach_file, "a") as f:
    f.write(f"\n--- {task_id} at {datetime.now().isoformat()} ---\n")
    f.write(approach_description.strip())
    f.write("\n")

print(f"Analysis approach recorded for {task_id}")
```

**Why this matters:**

- If your analysis attempt fails, the recovery system will read this
- It helps detect if next attempt tries the same tool/approach (circular analysis)
- It creates a record of what was analyzed for chain of custody

## Add to STEP 7 (After verification section):

### If Analysis Verification Fails - Recovery Process

```python
# If analysis verification failed, record the attempt
import json
from pathlib import Path
from datetime import datetime

task_id = "your-task-id"
approach = "What analysis you tried"  # From your approach.txt
error_message = "What went wrong"  # The actual error

# Load or create attempt history
history_file = Path("memory/attempt_history.json")
if history_file.exists():
    with open(history_file) as f:
        history = json.load(f)
else:
    history = {"tasks": {}, "stuck_tasks": [], "metadata": {}}

# Initialize task if needed
if task_id not in history["tasks"]:
    history["tasks"][task_id] = {"attempts": [], "status": "pending"}

# Get current session number from investigation-progress.txt
session_num = 1  # You can extract from investigation-progress.txt

# Record the failed attempt
attempt = {
    "session": session_num,
    "timestamp": datetime.now().isoformat(),
    "approach": approach,
    "tool_used": "volatility3",  # or chainsaw, zeek, etc.
    "success": False,
    "error": error_message,
    "evidence_source": "path/to/evidence"
}

history["tasks"][task_id]["attempts"].append(attempt)
history["tasks"][task_id]["status"] = "failed"
history["metadata"]["last_updated"] = datetime.now().isoformat()

# Save
with open(history_file, "w") as f:
    json.dump(history, f, indent=2)

print(f"Failed attempt recorded for {task_id}")

# Check if we should mark as stuck
attempt_count = len(history["tasks"][task_id]["attempts"])
if attempt_count >= 3:
    print(f"\n⚠️  WARNING: {attempt_count} attempts failed.")
    print("Consider marking as stuck if you can't find a different approach.")
    print("Consult DFIQ for alternative approaches to this investigative question.")
```

## Add NEW STEP between 9 and 10:

## STEP 9B: RECORD SUCCESSFUL ANALYSIS (If verification passed)

```python
# Record successful completion in attempt history
import json
from pathlib import Path
from datetime import datetime

task_id = "your-task-id"
approach = "What analysis you performed"  # From your approach.txt
findings_file = "./outputs/[phase]/findings.json"

# Load attempt history
history_file = Path("memory/attempt_history.json")
if history_file.exists():
    with open(history_file) as f:
        history = json.load(f)
else:
    history = {"tasks": {}, "stuck_tasks": [], "metadata": {}}

# Initialize task if needed
if task_id not in history["tasks"]:
    history["tasks"][task_id] = {"attempts": [], "status": "pending"}

# Get session number
session_num = 1  # Extract from investigation-progress.txt

# Record successful attempt
attempt = {
    "session": session_num,
    "timestamp": datetime.now().isoformat(),
    "approach": approach,
    "tool_used": "volatility3",  # or chainsaw, zeek, etc.
    "success": True,
    "error": None,
    "findings_file": findings_file
}

history["tasks"][task_id]["attempts"].append(attempt)
history["tasks"][task_id]["status"] = "completed"
history["metadata"]["last_updated"] = datetime.now().isoformat()

# Save
with open(history_file, "w") as f:
    json.dump(history, f, indent=2)

# Also record evidence integrity verification
print(f"✓ Analysis success recorded for {task_id}")
print(f"  Findings saved to: {findings_file}")
```

## KEY RECOVERY PRINCIPLES:

### The Analysis Recovery Loop

```
1. Start analysis task
2. Check attempt_history.json for this task
3. If previous attempts exist:
   a. READ what tool/approach was tried
   b. READ what failed
   c. Consult DFIQ for alternative approaches
   d. Choose DIFFERENT approach
4. Record your approach
5. Perform analysis
6. Validate findings
7. If SUCCESS: Record attempt, update findings, mark complete
8. If FAILURE: Record attempt with error, check if stuck (3+ attempts)
```

### When to Mark as Stuck

An analysis task should be marked as stuck if:

- 3+ attempts with different tools all failed
- Circular analysis detected (same approach tried multiple times)
- Evidence doesn't contain required data
- Tool/evidence compatibility issues

```python
# Mark analysis task as stuck
task_id = "your-task-id"
reason = "Why it's stuck"

history_file = Path("memory/attempt_history.json")
with open(history_file) as f:
    history = json.load(f)

stuck_entry = {
    "task_id": task_id,
    "reason": reason,
    "escalated_at": datetime.now().isoformat(),
    "attempt_count": len(history["tasks"][task_id]["attempts"]),
    "recommended_action": "Consult DFIQ or escalate to senior analyst"
}

history["stuck_tasks"].append(stuck_entry)
history["tasks"][task_id]["status"] = "stuck"

with open(history_file, "w") as f:
    json.dump(history, f, indent=2)

# Also update investigation_plan.json status to "blocked"
```

### DFIQ Integration for Recovery

When stuck, consult DFIQ for alternative approaches:

```python
# Load DFIQ knowledge base
from dfiq import DFIQ

dfiq = DFIQ(yaml_data_path='./dfiq')

# Find alternative approaches for your question
question_id = "Q1001"  # e.g., "What files were downloaded using a web browser?"
question = dfiq.components.get(question_id)

if question:
    print(f"Question: {question.name}")
    print(f"Approaches available: {len(question.approaches)}")
    for approach_id in question.approaches:
        approach = dfiq.components.get(approach_id)
        print(f"  - {approach.name}")
```
