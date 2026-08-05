import { closeSync, lstatSync, openSync, writeSync } from 'node:fs';
import { randomUUID } from 'node:crypto';
import { dirname, resolve } from 'node:path';
import { mkdirSync, chmodSync } from 'node:fs';
import { canonicalJson, fail } from './strict_json.mjs';

export const AUDIT_CONTRACT = 'principia-atlas-hosted-audit-event/0.1';
export const METRICS_CONTRACT = 'principia-atlas-hosted-metrics/0.1';
const EVENT = /^[a-z][a-z0-9_.-]{1,79}$/;
const INSTANCE = /^[A-Za-z0-9._-]{1,80}$/;
const FORBIDDEN_FIELD = /(authorization|cookie|secret|token|subject|session_id|assertion_id|\bsid\b|\bjti\b)/i;

function safeValue(value, label) {
  if (value === null || typeof value === 'boolean' || typeof value === 'string') {
    if (typeof value === 'string' && Buffer.byteLength(value) > 1024) fail(`${label} exceeds resource limit`);
    return value;
  }
  if (typeof value === 'number' && Number.isSafeInteger(value)) return value;
  if (Array.isArray(value)) {
    if (value.length > 32) fail(`${label} exceeds resource limit`);
    return value.map((item, index) => safeValue(item, `${label}[${index}]`));
  }
  fail(`${label} is invalid`);
}

function auditFields(fields) {
  if (!fields || typeof fields !== 'object' || Array.isArray(fields)) fail('audit fields are invalid');
  const output = {};
  for (const key of Object.keys(fields).sort()) {
    if (!/^[a-z][a-z0-9_]{0,63}$/.test(key) || FORBIDDEN_FIELD.test(key)) fail('audit field name is invalid');
    output[key] = safeValue(fields[key], `audit field ${key}`);
  }
  return output;
}

function auditDescriptor(kind, path = null) {
  return Object.freeze({ contract: AUDIT_CONTRACT, kind, path });
}

export function createNullAuditLogger() {
  return Object.freeze({ descriptor: auditDescriptor('null'), event() {}, close() {} });
}

export function createAuditLogger({ path = null, instanceId = 'local', now = () => Math.floor(Date.now() / 1000) } = {}) {
  if (!INSTANCE.test(instanceId)) fail('audit instance identifier is invalid');
  let descriptor;
  let fd;
  if (path === null) {
    descriptor = auditDescriptor('stdout');
    fd = 1;
  } else {
    if (typeof path !== 'string' || path.length === 0) fail('audit path is invalid');
    const target = resolve(path);
    const parent = dirname(target);
    mkdirSync(parent, { recursive: true, mode: 0o700 });
    try {
      const stats = lstatSync(target);
      if (stats.isSymbolicLink() || !stats.isFile()) fail('audit log must be a regular file');
    } catch (error) {
      if (error?.code !== 'ENOENT') throw error;
    }
    fd = openSync(target, 'a', 0o600);
    chmodSync(target, 0o600);
    descriptor = auditDescriptor('file', target);
  }
  let sequence = 0;
  let closed = false;
  return {
    descriptor,
    event(event, fields = {}) {
      if (closed) fail('audit logger is closed');
      if (!EVENT.test(event)) fail('audit event name is invalid');
      const timestamp = now();
      if (!Number.isSafeInteger(timestamp) || timestamp < 0) fail('audit timestamp is invalid');
      sequence += 1;
      const record = {
        contract: AUDIT_CONTRACT,
        event,
        instance_id: instanceId,
        sequence,
        timestamp,
        ...auditFields(fields),
      };
      writeSync(fd, canonicalJson(record));
      return Object.freeze(record);
    },
    close() {
      if (closed) return;
      closed = true;
      if (descriptor.kind === 'file') closeSync(fd);
    },
  };
}

function counterKey(name, label) {
  return `${name}\u0000${label}`;
}

export function createMetricsRegistry({ startedAtMs = Date.now() } = {}) {
  if (!Number.isSafeInteger(startedAtMs) || startedAtMs < 0) fail('metrics start time is invalid');
  const counters = new Map();
  let activeRequests = 0;
  let ready = false;
  const increment = (name, label = '', amount = 1) => {
    if (!Number.isSafeInteger(amount) || amount < 0) fail('metrics increment is invalid');
    const key = counterKey(name, label);
    counters.set(key, (counters.get(key) ?? 0) + amount);
  };
  return {
    contract: METRICS_CONTRACT,
    beginRequest() { activeRequests += 1; },
    endRequest(status, bytes = 0) {
      if (activeRequests > 0) activeRequests -= 1;
      const group = Number.isInteger(status) && status >= 100 && status <= 599 ? `${Math.floor(status / 100)}xx` : 'other';
      increment('http_requests', group);
      if (Number.isSafeInteger(bytes) && bytes > 0) increment('response_bytes', '', bytes);
    },
    auth(outcome) {
      if (!['success', 'invalid', 'rate_limited', 'revoked'].includes(outcome)) fail('metrics auth outcome is invalid');
      increment('auth_exchanges', outcome);
    },
    release(bytes) {
      increment('release_responses');
      if (Number.isSafeInteger(bytes) && bytes > 0) increment('release_bytes', '', bytes);
    },
    setReady(value) { ready = value === true; },
    snapshot(nowMs = Date.now()) {
      if (!Number.isSafeInteger(nowMs) || nowMs < startedAtMs) fail('metrics time is invalid');
      return Object.freeze({
        contract: METRICS_CONTRACT,
        active_requests: activeRequests,
        ready,
        uptime_seconds: Math.floor((nowMs - startedAtMs) / 1000),
      });
    },
    render(nowMs = Date.now()) {
      const snapshot = this.snapshot(nowMs);
      const lines = [
        '# HELP principia_atlas_up Process liveness.',
        '# TYPE principia_atlas_up gauge',
        'principia_atlas_up 1',
        '# HELP principia_atlas_ready Shared-state readiness.',
        '# TYPE principia_atlas_ready gauge',
        `principia_atlas_ready ${snapshot.ready ? 1 : 0}`,
        '# HELP principia_atlas_active_requests In-flight HTTP requests.',
        '# TYPE principia_atlas_active_requests gauge',
        `principia_atlas_active_requests ${snapshot.active_requests}`,
        '# HELP principia_atlas_process_uptime_seconds Process uptime.',
        '# TYPE principia_atlas_process_uptime_seconds gauge',
        `principia_atlas_process_uptime_seconds ${snapshot.uptime_seconds}`,
      ];
      const metric = (name, help, labels) => {
        lines.push(`# HELP principia_atlas_${name}_total ${help}`, `# TYPE principia_atlas_${name}_total counter`);
        for (const label of labels) {
          const value = counters.get(counterKey(name, label)) ?? 0;
          lines.push(label ? `principia_atlas_${name}_total{${label.includes('xx') || label === 'other' ? 'class' : 'outcome'}="${label}"} ${value}` : `principia_atlas_${name}_total ${value}`);
        }
      };
      metric('http_requests', 'HTTP responses by status class.', ['2xx', '3xx', '4xx', '5xx', 'other']);
      metric('auth_exchanges', 'Authentication exchange outcomes.', ['success', 'invalid', 'rate_limited', 'revoked']);
      metric('response_bytes', 'HTTP response bytes.', ['']);
      metric('release_responses', 'Hosted release responses.', ['']);
      metric('release_bytes', 'Hosted release response bytes.', ['']);
      return `${lines.join('\n')}\n`;
    },
  };
}

export function newRequestId() {
  return randomUUID();
}
