#!/usr/bin/env node
/**
 * Prints the current session as a formatted list directly to stdout.
 * Skips the `startedAt` key.
 *
 * Usage:
 *   node session-data.js
 */

const fs   = require('fs');
const path = require('path');

const SESSION_FILE = path.resolve(__dirname, '../../tmp/session.json');

let data = {};
try {
  data = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf8'));
} catch {
  // no session file yet
}

// Drop internal key
const entries = Object.entries(data).filter(([k]) => k !== 'startedAt');

if (entries.length === 0) {
  process.stdout.write(
    'ℹ️  No session data yet. Start with Task Creation to create a GitLab issue, or GitLab Specialist to set up a branch.\n'
  );
  process.exit(0);
}

const lines = entries.map(([k, v]) => `  • ${k}: ${String(v)}`);

process.stdout.write('\n📋 Session\n' + lines.join('\n') + '\n\n');

