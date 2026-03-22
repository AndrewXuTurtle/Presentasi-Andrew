# TEAM-RUNBOOK.md

## Boss Rules for Cheap Execution

- Start with the smallest capable approach.
- Use subagents only for multi-step or parallelizable work.
- Keep subagent prompts crisp; include only the exact files/context they need.
- If one worker can finish the job, do not spawn three.
- Avoid browser usage unless the task truly requires an interactive page.
- Avoid repeated status checks; wait for completion events when possible.
- If work stalls, Watcher either steers once or kills and retries with a better prompt.
- Final user communication always comes from Boss.

## Worker Prompt Skeleton
- Goal
- Constraints
- Allowed scope
- Deliverable format
- Stop condition

## Watcher Checklist
- Is the worker still aligned with the requested outcome?
- Is the worker making progress or looping?
- Has context grown too much for the value being produced?
- Can the task be cut into a smaller retry?
- Is a final report ready for Andrew?
