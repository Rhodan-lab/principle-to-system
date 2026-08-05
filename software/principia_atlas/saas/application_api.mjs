import { createHash, createHmac, timingSafeEqual } from 'node:crypto';

import {
  SAAS_PROGRESS_RESULT_CONTRACT,
  SAAS_SESSION_CONTRACT,
  validateIdempotencyInput,
  validateProgressRequest,
} from './domain.mjs';
import { canonicalJson, fail, parseStrictJson } from '../hosted/strict_json.mjs';

export const SAAS_APPLICATION_API_CONTRACT = 'principia-atlas-saas-application-api/0.1';
const DEFAULT_MAX_BODY_BYTES = 16 * 1024;
const DEFAULT_IDEMPOTENCY_TTL_SECONDS = 24 * 60 * 60;
const CSRF_DOMAIN = 'principia-atlas-saas-csrf/0.1';
const IDEMPOTENCY_OPERATION = 'progress.write';

class ApiError extends Error {
  constructor(status, code, headers = {}) {
    super(code);
    this.status = status;
    this.code = code;
    this.headers = headers;
  }
}

function header(request, name) {
  const value = request?.headers?.[name.toLowerCase()];
  if (Array.isArray(value)) return value.length === 1 ? value[0] : null;
  return typeof value === 'string' ? value : null;
}

function apiResponse(status, body, headers = {}) {
  return Object.freeze({ status, body: Object.freeze(body), headers: Object.freeze({ ...headers }) });
}

function validateSession(session) {
  if (!session || typeof session !== 'object'
    || typeof session.sid !== 'string' || session.sid.length < 16 || session.sid.length > 256
    || typeof session.sub !== 'string'
    || typeof session.tenant_id !== 'string'
    || !Number.isSafeInteger(session.exp)) fail('SaaS application session is invalid');
  return session;
}

function csrfForSession(secret, session) {
  return createHmac('sha256', secret)
    .update(CSRF_DOMAIN)
    .update('\0')
    .update(session.sid)
    .update('\0')
    .update(session.tenant_id)
    .update('\0')
    .update(String(session.exp))
    .digest('base64url');
}

function csrfMatches(actual, expected) {
  if (typeof actual !== 'string' || !/^[A-Za-z0-9_-]{43}$/.test(actual)) return false;
  const left = Buffer.from(actual, 'utf8');
  const right = Buffer.from(expected, 'utf8');
  return left.length === right.length && timingSafeEqual(left, right);
}

function exactMutationOrigin(request) {
  const origin = header(request, 'origin');
  const host = header(request, 'host');
  if (!origin || !host) return false;
  try {
    const parsed = new URL(origin);
    return parsed.origin === origin && parsed.host === host && ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
}

function jsonContentType(request) {
  const value = header(request, 'content-type');
  return typeof value === 'string' && /^application\/json(?:\s*;\s*charset=utf-8)?$/i.test(value.trim());
}

async function readBoundedJson(request, maximumBytes) {
  const declared = header(request, 'content-length');
  if (declared !== null && (!/^\d+$/.test(declared) || Number(declared) > maximumBytes)) {
    throw new ApiError(413, 'request_too_large');
  }
  const chunks = [];
  let total = 0;
  for await (const chunk of request) {
    const raw = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    total += raw.length;
    if (total > maximumBytes) throw new ApiError(413, 'request_too_large');
    chunks.push(raw);
  }
  if (total === 0) throw new ApiError(400, 'request_body_required');
  try { return parseStrictJson(Buffer.concat(chunks, total), 'SaaS application request'); }
  catch { throw new ApiError(400, 'invalid_json'); }
}

function errorResponse(error) {
  if (error instanceof ApiError) return apiResponse(error.status, { error: error.code }, error.headers);
  const message = String(error?.message ?? error);
  if (/learner progress revision conflict/.test(message)) return apiResponse(409, { error: 'progress_revision_conflict' });
  if (/idempotency key conflict/.test(message)) return apiResponse(409, { error: 'idempotency_conflict' });
  if (/learner route is not entitled/.test(message)) return apiResponse(403, { error: 'route_not_entitled' });
  if (/not an active organization member|organization is not active/.test(message)) return apiResponse(403, { error: 'saas_membership_required' });
  if (/invalid|must be|size is|window is/.test(message)) return apiResponse(400, { error: 'invalid_request' });
  return apiResponse(503, { error: 'saas_state_unavailable' });
}

function validateControlPlane(controlPlane) {
  if (!controlPlane || typeof controlPlane.resolveSession !== 'function'
    || typeof controlPlane.dashboard !== 'function'
    || typeof controlPlane.recordProgressIdempotent !== 'function'
    || typeof controlPlane.health !== 'function') fail('SaaS application control plane is invalid');
  return controlPlane;
}

export function createSaasApplicationApi({
  controlPlane: controlPlaneInput,
  csrfSecret,
  audit = null,
  maxBodyBytes = DEFAULT_MAX_BODY_BYTES,
  idempotencyTtlSeconds = DEFAULT_IDEMPOTENCY_TTL_SECONDS,
} = {}) {
  const controlPlane = validateControlPlane(controlPlaneInput);
  const secret = Buffer.isBuffer(csrfSecret) ? Buffer.from(csrfSecret) : Buffer.from(String(csrfSecret ?? ''), 'utf8');
  if (secret.length < 32 || secret.length > 4096) fail('SaaS CSRF secret length is invalid');
  if (!Number.isSafeInteger(maxBodyBytes) || maxBodyBytes < 1024 || maxBodyBytes > 65536) fail('SaaS request body limit is invalid');
  if (!Number.isSafeInteger(idempotencyTtlSeconds) || idempotencyTtlSeconds < 60 || idempotencyTtlSeconds > 604800) fail('SaaS idempotency TTL is invalid');

  const event = (name, fields = {}) => {
    try { audit?.event?.(name, fields); } catch {}
  };

  const handle = async ({ request, url, session: sessionInput, nowSeconds, requestId = null }) => {
    if (!url?.pathname?.startsWith('/api/saas/')) return null;
    const session = validateSession(sessionInput);
    if (!Number.isSafeInteger(nowSeconds) || nowSeconds < 0) return apiResponse(500, { error: 'internal_error' });
    try {
      const resolved = await controlPlane.resolveSession(session.tenant_id, session.sub, nowSeconds);
      if (!resolved) {
        event('saas.session.reject', { request_id: requestId, tenant_id: session.tenant_id, outcome: 'membership_missing' });
        return apiResponse(403, { error: 'saas_membership_required' });
      }

      if (url.pathname === '/api/saas/me') {
        if (request.method !== 'GET') return apiResponse(405, { error: 'method_not_allowed' }, { Allow: 'GET' });
        return apiResponse(200, {
          contract: SAAS_SESSION_CONTRACT,
          organization: resolved.organization,
          membership: resolved.membership,
          csrf_token: csrfForSession(secret, session),
          session_expires_at: session.exp,
        });
      }

      if (url.pathname === '/api/saas/dashboard') {
        if (request.method !== 'GET') return apiResponse(405, { error: 'method_not_allowed' }, { Allow: 'GET' });
        return apiResponse(200, await controlPlane.dashboard(resolved.membership.id, nowSeconds));
      }

      const progressMatch = /^\/api\/saas\/progress\/([a-z0-9-]{2,64})\/([a-z_]{2,32})$/.exec(url.pathname);
      if (!progressMatch) return apiResponse(404, { error: 'not_found' });
      if (request.method !== 'PUT') return apiResponse(405, { error: 'method_not_allowed' }, { Allow: 'PUT' });
      if (!exactMutationOrigin(request)) throw new ApiError(403, 'origin_rejected');
      if (!jsonContentType(request)) throw new ApiError(415, 'content_type_rejected');
      const expectedCsrf = csrfForSession(secret, session);
      if (!csrfMatches(header(request, 'x-csrf-token'), expectedCsrf)) throw new ApiError(403, 'csrf_rejected');

      const body = await readBoundedJson(request, maxBodyBytes);
      const requestProgress = validateProgressRequest(body, progressMatch[1], progressMatch[2]);
      const requestDigest = createHash('sha256').update(canonicalJson({
        route_id: requestProgress.routeId,
        release_id: requestProgress.releaseId,
        stage: requestProgress.stage,
        status: requestProgress.status,
        expected_revision: requestProgress.expectedRevision,
      })).digest('hex');
      const idempotency = validateIdempotencyInput({
        operation: IDEMPOTENCY_OPERATION,
        key: header(request, 'idempotency-key'),
        request_sha256: requestDigest,
        ttl_seconds: idempotencyTtlSeconds,
      });
      const stored = await controlPlane.recordProgressIdempotent(
        resolved.membership.id,
        {
          organization_id: resolved.organization.id,
          member_id: resolved.membership.id,
          route_id: requestProgress.routeId,
          release_id: requestProgress.releaseId,
          stage: requestProgress.stage,
          status: requestProgress.status,
          expected_revision: requestProgress.expectedRevision,
        },
        idempotency,
        nowSeconds,
      );
      event('saas.progress.write', {
        request_id: requestId,
        tenant_id: session.tenant_id,
        route_id: requestProgress.routeId,
        stage: requestProgress.stage,
        replayed: stored.replayed,
      });
      return apiResponse(200, {
        contract: SAAS_PROGRESS_RESULT_CONTRACT,
        progress: stored.progress,
      }, { 'Idempotency-Replayed': stored.replayed ? 'true' : 'false' });
    } catch (error) {
      const output = errorResponse(error);
      event('saas.request.reject', { request_id: requestId, tenant_id: session.tenant_id, status: output.status, error: output.body.error });
      return output;
    }
  };

  return Object.freeze({
    descriptor: Object.freeze({
      contract: SAAS_APPLICATION_API_CONTRACT,
      max_body_bytes: maxBodyBytes,
      idempotency_ttl_seconds: idempotencyTtlSeconds,
      production_ready: false,
    }),
    handle,
    close() { secret.fill(0); },
  });
}
