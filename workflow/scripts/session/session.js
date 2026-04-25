#!/usr/bin/env node
/**
 * Session manager for the agent workflow.
 *
 * Stores data in .a-local-workflow/workflow/tmp/session.json
 * so context survives agent hand-offs within the same working session.
 *
 * Usage:
 *   node session.js get                  → prints full session JSON to stdout
 *   node session.js get <key>            → prints value of <key> to stdout
 *   node session.js set <key> <value>    → writes/updates a key in the session
 *   node session.js unset <key>          → removes a single key from the session
 *   node session.js delete               → removes the session file entirely
 *   node session.js init                 → creates a fresh empty session (overwrites)
 */

const fs   = require('fs');
const path = require('path');

const SESSION_FILE = path.resolve(__dirname, '../../tmp/session.json');

function load() {
  try {
    return JSON.parse(fs.readFileSync(SESSION_FILE, 'utf8'));
  } catch {
    return {};
  }
}

function save(data) {
  fs.mkdirSync(path.dirname(SESSION_FILE), { recursive: true });
  fs.writeFileSync(SESSION_FILE, JSON.stringify(data, null, 2) + '\n', 'utf8');
}

const [,, cmd, key, ...rest] = process.argv;
const value = rest.join(' ');

switch (cmd) {
  case 'get': {
    const data = load();
    if (key) {
      const v = data[key];
      process.stdout.write(v !== undefined ? String(v) + '\n' : '');
    } else {
      process.stdout.write(JSON.stringify(data, null, 2) + '\n');
    }
    break;
  }
  case 'set': {
    if (!key) { process.stderr.write('set requires a key\n'); process.exit(1); }
    const data = load();
    data[key] = value;
    save(data);
    break;
  }
  case 'unset': {
    if (!key) { process.stderr.write('unset requires a key\n'); process.exit(1); }
    const data = load();
    delete data[key];
    save(data);
    process.stdout.write(`Key "${key}" removed.\n`);
    break;
  }
  case 'delete': {
    try { fs.unlinkSync(SESSION_FILE); } catch { /* already gone */ }
    process.stdout.write('Session deleted.\n');
    break;
  }
  case 'init': {
    save({ startedAt: new Date().toISOString() });
    process.stdout.write('Session initialised.\n');
    break;
  }
  default: {
    process.stderr.write('Usage: node session.js get|set|unset|delete|init [key] [value]\n');
    process.exit(1);
  }
}

