/**
 * GitHub star-on-behalf-of-visitor for the marketplace.
 *
 * Static pages cannot PUT /user/starred. A Worker exchanges GitHub OAuth and
 * stars as the signed-in user. Without OAuth secrets the API returns 501 so
 * the button can open GitHub instead.
 */

function parseGithubRepo(url) {
	if (!url || typeof url !== 'string') return null;
	const match = url.match(/^https:\/\/github\.com\/([\w.-]+)\/([\w.-]+?)(?:\.git)?(?:\/|#|\?|$)/i);
	return match ? `${match[1]}/${match[2]}` : null;
}

export const TOKEN_COOKIE = 'orbit_gh';
export const STATE_COOKIE = 'orbit_gh_state';
const STATE_TTL_MS = 10 * 60 * 1000;
const TOKEN_MAX_AGE = 3600;

export function parseOwnerRepo(input) {
	if (!input || typeof input !== 'string') return null;
	const trimmed = input.trim();
	const fromUrl = parseGithubRepo(trimmed);
	if (fromUrl) return fromUrl;
	if (/^[\w.-]+\/[\w.-]+$/.test(trimmed)) return trimmed;
	return null;
}

/** Same-origin return paths only — marketplace listings. */
export function safeReturnPath(path) {
	const raw = String(path ?? '').split('?')[0];
	const normalized = raw.startsWith('/') ? raw : `/${raw}`;
	if (normalized === '/plugins' || normalized === '/plugins/') return '/plugins/';
	if (!normalized.startsWith('/plugins/')) return '/plugins/';
	if (
		normalized.includes('\\') ||
		normalized.includes('//') ||
		normalized.includes('://') ||
		normalized.includes('..')
	) {
		return '/plugins/';
	}
	return normalized;
}

export function json(body, status = 200, headers = {}) {
	return new Response(JSON.stringify(body), {
		status,
		headers: {
			'Content-Type': 'application/json; charset=utf-8',
			'Cache-Control': 'no-store',
			...headers,
		},
	});
}

export function readCookie(header, name) {
	if (!header) return null;
	const parts = String(header).split(/;\s*/);
	const prefix = `${name}=`;
	for (const part of parts) {
		if (part.startsWith(prefix)) return decodeURIComponent(part.slice(prefix.length));
	}
	return null;
}

export function cookieHeader(name, value, { maxAge, httpOnly = true } = {}) {
	const bits = [
		`${name}=${encodeURIComponent(value)}`,
		'Path=/',
		'SameSite=Lax',
		'Secure',
	];
	if (httpOnly) bits.push('HttpOnly');
	if (maxAge != null) bits.push(`Max-Age=${maxAge}`);
	return bits.join('; ');
}

export function clearCookie(name) {
	return cookieHeader(name, '', { maxAge: 0 });
}

export function bytesToBase64Url(bytes) {
	let binary = '';
	for (const byte of bytes) binary += String.fromCharCode(byte);
	return btoa(binary).replaceAll('+', '-').replaceAll('/', '_').replace(/=+$/u, '');
}

export function base64UrlToUtf8(token) {
	const padded = token.replace(/-/g, '+').replace(/_/g, '/');
	const pad = padded.length % 4 === 0 ? '' : '='.repeat(4 - (padded.length % 4));
	const binary = atob(padded + pad);
	const bytes = Uint8Array.from(binary, (ch) => ch.charCodeAt(0));
	return new TextDecoder().decode(bytes);
}

export function utf8ToBase64Url(text) {
	return bytesToBase64Url(new TextEncoder().encode(text));
}

export async function hmacHex(secret, message) {
	const key = await crypto.subtle.importKey(
		'raw',
		new TextEncoder().encode(secret),
		{ name: 'HMAC', hash: 'SHA-256' },
		false,
		['sign'],
	);
	const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(message));
	return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

export async function signState(payload, secret) {
	const body = JSON.stringify(payload);
	const sig = await hmacHex(secret, body);
	return utf8ToBase64Url(JSON.stringify({ body, sig }));
}

export async function verifyState(token, secret) {
	if (!token || !secret) return null;
	let parsed;
	try {
		parsed = JSON.parse(base64UrlToUtf8(String(token)));
	} catch {
		return null;
	}
	if (!parsed?.body || !parsed?.sig) return null;
	const expected = await hmacHex(secret, parsed.body);
	if (expected !== parsed.sig) return null;
	let payload;
	try {
		payload = JSON.parse(parsed.body);
	} catch {
		return null;
	}
	if (payload.exp && Date.now() > payload.exp) return null;
	const repo = parseOwnerRepo(payload.repo);
	if (!repo) return null;
	return { ...payload, repo, returnPath: safeReturnPath(payload.returnPath) };
}

export function oauthConfigured(env) {
	return Boolean(env?.GITHUB_OAUTH_CLIENT_ID && env?.GITHUB_OAUTH_CLIENT_SECRET);
}

function githubHeaders(token) {
	return {
		Accept: 'application/vnd.github+json',
		Authorization: `Bearer ${token}`,
		'User-Agent': 'almasix-orbit-docs',
		'X-GitHub-Api-Version': '2022-11-28',
	};
}

export async function starGithubRepo(repo, token, doFetch = fetch) {
	const response = await doFetch(`https://api.github.com/user/starred/${repo}`, {
		method: 'PUT',
		headers: {
			...githubHeaders(token),
			'Content-Length': '0',
		},
	});
	if (response.status === 204 || response.status === 304) {
		return { ok: true, already: response.status === 304 };
	}
	const detail = await response.text().catch(() => '');
	return { ok: false, status: response.status, detail };
}

export async function exchangeOauthCode(code, env, origin, doFetch = fetch) {
	const response = await doFetch('https://github.com/login/oauth/access_token', {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			client_id: env.GITHUB_OAUTH_CLIENT_ID,
			client_secret: env.GITHUB_OAUTH_CLIENT_SECRET,
			code,
			redirect_uri: `${origin}/api/github/oauth/callback`,
		}),
	});
	if (!response.ok) return null;
	const data = await response.json().catch(() => null);
	const token = data?.access_token;
	return typeof token === 'string' && token ? token : null;
}

export function authorizeUrl(env, state, origin) {
	const url = new URL('https://github.com/login/oauth/authorize');
	url.searchParams.set('client_id', env.GITHUB_OAUTH_CLIENT_ID);
	url.searchParams.set('redirect_uri', `${origin}/api/github/oauth/callback`);
	url.searchParams.set('state', state);
	const scope = env.GITHUB_OAUTH_SCOPE;
	if (scope) url.searchParams.set('scope', scope);
	return url.toString();
}

function apiPath(pathname) {
	return (pathname ?? '/').replace(/\/+$/, '') || '/';
}

export async function handleGithubRequest(request, env, deps = {}) {
	const doFetch = deps.fetch ?? fetch;
	const url = new URL(request.url);
	const path = apiPath(url.pathname);
	const origin = url.origin;

	if (!oauthConfigured(env)) {
		return json({ error: 'oauth_unconfigured', fallback: true }, 501);
	}

	if (path === '/api/github/oauth/start' && request.method === 'GET') {
		const repo = parseOwnerRepo(url.searchParams.get('repo') ?? '');
		if (!repo) return json({ error: 'invalid_repo' }, 400);
		const returnPath = safeReturnPath(url.searchParams.get('return') ?? '/plugins/');
		const nonce = crypto.randomUUID();
		const state = await signState(
			{ repo, returnPath, n: nonce, exp: Date.now() + STATE_TTL_MS },
			env.GITHUB_OAUTH_CLIENT_SECRET,
		);
		return new Response(null, {
			status: 302,
			headers: {
				Location: authorizeUrl(env, state, origin),
				'Set-Cookie': cookieHeader(STATE_COOKIE, nonce, { maxAge: 600 }),
				'Cache-Control': 'no-store',
			},
		});
	}

	if (path === '/api/github/oauth/callback' && request.method === 'GET') {
		const error = url.searchParams.get('error');
		const code = url.searchParams.get('code') ?? '';
		const stateToken = url.searchParams.get('state') ?? '';
		const payload = await verifyState(stateToken, env.GITHUB_OAUTH_CLIENT_SECRET);
		const nonce = readCookie(request.headers.get('Cookie'), STATE_COOKIE);
		const returnPath = payload ? payload.returnPath : '/plugins/';
		const fail = (reason) =>
			new Response(null, {
				status: 302,
				headers: {
					Location: `${returnPath}${returnPath.includes('?') ? '&' : '?'}star=${reason}`,
					'Set-Cookie': clearCookie(STATE_COOKIE),
					'Cache-Control': 'no-store',
				},
			});
		if (error || !code || !payload || !nonce || nonce !== payload.n) {
			return fail('denied');
		}
		const token = await exchangeOauthCode(code, env, origin, doFetch);
		if (!token) return fail('token');
		const starred = await starGithubRepo(payload.repo, token, doFetch);
		if (!starred.ok) return fail('api');
		const headers = new Headers({
			Location: `${returnPath}${returnPath.includes('?') ? '&' : '?'}starred=1`,
			'Cache-Control': 'no-store',
		});
		headers.append('Set-Cookie', cookieHeader(TOKEN_COOKIE, token, { maxAge: TOKEN_MAX_AGE }));
		headers.append('Set-Cookie', clearCookie(STATE_COOKIE));
		return new Response(null, { status: 302, headers });
	}

	if (path === '/api/github/star' && (request.method === 'POST' || request.method === 'GET')) {
		const repo = parseOwnerRepo(url.searchParams.get('repo') ?? '');
		if (!repo) return json({ error: 'invalid_repo' }, 400);
		const token = readCookie(request.headers.get('Cookie'), TOKEN_COOKIE);
		const returnPath = safeReturnPath(url.searchParams.get('return') ?? '/plugins/');
		if (!token) {
			const authorize = `${origin}/api/github/oauth/start?repo=${encodeURIComponent(repo)}&return=${encodeURIComponent(returnPath)}`;
			return json({ error: 'authorize', authorize }, 401);
		}
		const starred = await starGithubRepo(repo, token, doFetch);
		if (!starred.ok) {
			if (starred.status === 401) {
				const authorize = `${origin}/api/github/oauth/start?repo=${encodeURIComponent(repo)}&return=${encodeURIComponent(returnPath)}`;
				return json({ error: 'authorize', authorize }, 401, {
					'Set-Cookie': clearCookie(TOKEN_COOKIE),
				});
			}
			return json({ error: 'github', status: starred.status }, 502);
		}
		return json({ starred: true, already: Boolean(starred.already) });
	}

	return json({ error: 'not_found' }, 404);
}

export default {
	async fetch(request, env) {
		const path = apiPath(new URL(request.url).pathname);
		if (path !== '/api/github' && !path.startsWith('/api/github/')) {
			if (env?.ASSETS) return env.ASSETS.fetch(request);
			return new Response('Not found', { status: 404 });
		}
		return handleGithubRequest(request, env);
	},
};
