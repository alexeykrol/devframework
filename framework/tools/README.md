# Framework Tools

## export-report.py
Creates a report bundle zip for sharing framework run artifacts.

Example:
```
python3 framework/tools/export-report.py --include-migration --include-task-logs
```

## publish-report.py
Publishes a report bundle to GitHub as a PR or issue.

Example:
```
export GITHUB_TOKEN=... 
python3 framework/tools/publish-report.py --repo alexeykrol/devframework --run-id <RUN_ID> --mode pr --host-id my-host
```
