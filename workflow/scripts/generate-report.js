#!/usr/bin/env node
/**
 * Generates a task completion report from the current session data.
 *
 * Reads session.json, builds a markdown report, and writes it to:
 *   .a-local-workflow/workflow/tmp/<task-title-slug>.md
 *
 * Usage:
 *   node generate-report.js
 *
 * Output:
 *   Prints the path of the saved report file to stdout.
 */

const fs   = require('fs');
const path = require('path');

const SESSION_FILE = path.resolve(__dirname, '../tmp/session.json');
const TMP_DIR      = path.resolve(__dirname, '../tmp');

function loadSession() {
  try {
    return JSON.parse(fs.readFileSync(SESSION_FILE, 'utf8'));
  } catch {
    process.stderr.write('No session file found. Nothing to report.\n');
    process.exit(1);
  }
}

function slugify(str) {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 50);
}

function formatDate() {
  return new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC';
}

function parseField(value) {
  if (typeof value === 'string') {
    try { return JSON.parse(value); } catch { return {}; }
  }
  return value || {};
}

const session  = loadSession();
const task     = parseField(session.task);
const mr       = parseField(session.mr);
const branch   = session.branch || '';

const title    = task.title || 'untitled';
const slug     = slugify(title);
const filename = `${slug}.md`;
const filepath = path.join(TMP_DIR, filename);

const issueLink  = task.link  ? `[#${task.iid}](${task.link})`   : task.iid || '—';
const mrLink     = mr.url     ? `[!${mr.iid}](${mr.url})`        : '—';
const branchText = branch     ? `\`${branch}\``                   : '—';

const report = `# ${title}

> Generated: ${formatDate()}

## Summary

| Field   | Value |
|---------|-------|
| Issue   | ${issueLink} |
| Branch  | ${branchText} |
| MR      | ${mrLink} |
| Status  | Merged and closed |

## Session snapshot

\`\`\`json
${JSON.stringify(session, null, 2)}
\`\`\`
`;

fs.mkdirSync(TMP_DIR, { recursive: true });
fs.writeFileSync(filepath, report, 'utf8');
process.stdout.write(`Report saved: .a-local-workflow/workflow/tmp/${filename}\n`);

