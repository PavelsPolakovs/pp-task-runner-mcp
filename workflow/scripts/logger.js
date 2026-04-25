#!/usr/bin/env node
/**
 * Workflow logger — appends structured log entries and builds task markdown files.
 *
 * Logs are stored in .a-local-workflow/workflow/tmp/workflow-log.json
 *
 * Usage:
 *   node logger.js log "<message>"          → append a log entry (rendered as blockquote italic)
 *   node logger.js list                     → print all log entries to stdout
 *   node logger.js build [task-name]        → write tmp/<task-name>.md from collected logs
 *   node logger.js clear                    → delete all stored log entries
 */

'use strict';

const fs   = require('fs');
const path = require('path');

const LOG_FILE = path.resolve(__dirname, '../tmp/workflow-log.json');
const TMP_DIR  = path.dirname(LOG_FILE);

// ── helpers ──────────────────────────────────────────────────────────────────

function loadLogs() {
  try {
    return JSON.parse(fs.readFileSync(LOG_FILE, 'utf8'));
  } catch {
    return [];
  }
}

function saveLogs(entries) {
  fs.mkdirSync(TMP_DIR, { recursive: true });
  fs.writeFileSync(LOG_FILE, JSON.stringify(entries, null, 2) + '\n', 'utf8');
}

/**
 * Returns a human-readable timestamp: 2026-04-24 10:30:00
 */
function now() {
  const d = new Date();
  const pad = n => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ` +
         `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

/**
 * Strips the markdown italic-blockquote wrapper applied when logging messages
 * like > _"..."_ so the plain text is stored and can be re-formatted on output.
 */
function stripWrapper(msg) {
  return msg.trim().replace(/^>\s*_?"?(.+?)"?_?$/, '$1').trim();
}

/**
 * Formats a single entry for terminal output:
 *   [2026-04-24 10:30:00] Issue `My Task` created successfully (#12, type::feature, workflow::new).
 */
function formatForTerminal(entry) {
  return `\x1b[90m[${entry.timestamp}]\x1b[0m ${entry.message}`;
}

/**
 * Formats a single entry as a markdown blockquote line:
 *   > _"Issue `My Task` created successfully (#12, type::feature, workflow::new)."_
 */
function formatForMarkdown(entry) {
  const text = entry.message.replace(/^"|"$/g, '');
  return `> _"${text}"_`;
}

// ── commands ──────────────────────────────────────────────────────────────────

const [,, cmd, ...args] = process.argv;

switch (cmd) {
  case 'log': {
    if (args.length === 0) {
      process.stderr.write('Usage: node logger.js log "<message>"\n');
      process.exit(1);
    }
    const raw     = args.join(' ');
    const message = stripWrapper(raw);
    const entries = loadLogs();
    const entry   = { timestamp: now(), message };
    entries.push(entry);
    saveLogs(entries);
    process.stdout.write(`\x1b[32m✔\x1b[0m Logged: ${formatForTerminal(entry)}\n`);
    break;
  }

  case 'list': {
    const entries = loadLogs();
    if (entries.length === 0) {
      process.stdout.write('ℹ️  No log entries yet.\n');
      break;
    }
    process.stdout.write('\n📋 Workflow Log\n' + '─'.repeat(60) + '\n');
    entries.forEach((e, i) => {
      process.stdout.write(`  ${String(i + 1).padStart(2)}. ${formatForTerminal(e)}\n`);
    });
    process.stdout.write('─'.repeat(60) + '\n\n');
    break;
  }

  case 'build': {
    const entries = loadLogs();
    if (entries.length === 0) {
      process.stderr.write('⚠️  No log entries to build from.\n');
      process.exit(1);
    }

    // Derive task name: explicit arg, or slug from first log message
    let taskName = args.join(' ').trim();
    if (!taskName) {
      taskName = entries[0].message
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '')
        .slice(0, 60);
    }

    const fileName = `${taskName}.md`;
    const outPath  = path.join(TMP_DIR, fileName);

    const header = `# Workflow Log — ${taskName}\n\n` +
                   `_Generated on ${now()}_\n\n` +
                   '---\n\n';

    const body = entries
      .map((e, i) => `### Entry ${i + 1} — ${e.timestamp}\n\n${formatForMarkdown(e)}\n`)
      .join('\n');

    fs.mkdirSync(TMP_DIR, { recursive: true });
    fs.writeFileSync(outPath, header + body, 'utf8');
    process.stdout.write(`\x1b[32m✔\x1b[0m Built: \x1b[36m${outPath}\x1b[0m  (${entries.length} entr${entries.length === 1 ? 'y' : 'ies'})\n`);
    break;
  }

  case 'clear': {
    try { fs.unlinkSync(LOG_FILE); } catch { /* already gone */ }
    process.stdout.write('🗑️  Log cleared.\n');
    break;
  }

  default: {
    process.stderr.write(
      'Usage: node logger.js log "<message>" | list | build [task-name] | clear\n'
    );
    process.exit(1);
  }
}

