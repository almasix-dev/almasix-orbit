import assert from 'node:assert/strict';
import { test } from 'node:test';

import worker, {
	authorizeUrl,
	cookieHeader,
	exchangeOauthCode,
	handleGithubRequest,
	hmacHex,
	oauthConfigured,
	parseOwnerRepo,
	readCookie,
	safeReturnPath,
	signState,
	starGithubRepo,
	TOKEN_COOKIE,
	utf8ToBase64Url,
	verifyState,
} from './github-star.mjs';

const env = {
	GITHUB_OAUTH_CLIENT_ID: 'client-id',
	GITHUB_OAUTH_CLIENT_SECRET: 'super-secret',
	GITHUB_OAUTH_SCOPE: 'public_repo',
};

function request(path, { method = 'GET', cookie, origin = 'https://orbit.almasix.com' } = {}) {
	const headers = {};
	if (cookie) headers.Cookie = cookie;
	return new Request(`${origin}${path}`, { method, headers });
}

test('parseOwnerRepo and safeReturnPath', () => {
	assert.equal(parseOwnerRepo(null), null);
	assert.equal(parseOwnerRepo('acme/kit'), 'acme/kit');
	assert.equal(parseOwnerRepo('https://github.com/acme/kit'), 'acme/kit');
	assert.equal(parseOwnerRepo('https://github.com/acme/kit.git'), 'acme/kit');
	assert.equal(parseOwnerRepo(''), null);
	assert.equal(parseOwnerRepo('https://example.com/x'), null);
	assert.equal(safeReturnPath('/plugins/orbit-branding/'), '/plugins/orbit-branding/');
	assert.equal(safeReturnPath('/main/plugins/orbit-branding/'), '/main/plugins/orbit-branding/');
	assert.equal(safeReturnPath('/plugins'), '/plugins/');
	assert.equal(safeReturnPath('https://evil.example/'), '/plugins/');
	assert.equal(safeReturnPath('/plugins/../etc'), '/plugins/');
	assert.equal(safeReturnPath('/getting-started/'), '/plugins/');
	assert.equal(safeReturnPath('/main/getting-started/'), '/main/plugins/');
});

test('cookies and hmac state', async () => {
	assert.equal(readCookie(null, 'x'), null);
	assert.equal(readCookie('a=1; orbit_gh=tok%2Ben', 'orbit_gh'), 'tok+en');
	assert.match(cookieHeader('n', 'v', { maxAge: 9, httpOnly: false }), /SameSite=Lax/);
	assert.match(cookieHeader('n', 'v', { httpOnly: true }), /HttpOnly/);
	const token = await signState(
		{ repo: 'acme/kit', returnPath: '/plugins/kit/', n: 'nonce', exp: Date.now() + 60_000 },
		env.GITHUB_OAUTH_CLIENT_SECRET,
	);
	const verified = await verifyState(token, env.GITHUB_OAUTH_CLIENT_SECRET);
	assert.equal(verified.repo, 'acme/kit');
	assert.equal(await verifyState('', 'secret'), null);
	assert.equal(await verifyState('%%%', 'secret'), null);
	assert.equal(await verifyState(utf8ToBase64Url('{"no":"sig"}'), 'secret'), null);
	const badSig = await signState({ repo: 'acme/kit', n: 'n' }, 'other-secret');
	assert.equal(await verifyState(badSig, env.GITHUB_OAUTH_CLIENT_SECRET), null);
	const expired = await signState(
		{ repo: 'acme/kit', n: 'n', exp: Date.now() - 1 },
		env.GITHUB_OAUTH_CLIENT_SECRET,
	);
	assert.equal(await verifyState(expired, env.GITHUB_OAUTH_CLIENT_SECRET), null);
	const brokenBody = utf8ToBase64Url(JSON.stringify({ body: '{', sig: await hmacHex('s', '{') }));
	assert.equal(await verifyState(brokenBody, 's'), null);
	assert.equal(await verifyState(await signState({ repo: 'nope' }, 's'), 's'), null);
	assert.equal(oauthConfigured({}), false);
	assert.equal(oauthConfigured(env), true);
});

test('star and token exchange helpers', async () => {
	const ok = await starGithubRepo('acme/kit', 't', async () => new Response(null, { status: 204 }));
	assert.deepEqual(ok, { ok: true, already: false });
	const already = await starGithubRepo('acme/kit', 't', async () => new Response(null, { status: 304 }));
	assert.equal(already.already, true);
	const fail = await starGithubRepo('acme/kit', 't', async () => new Response('nope', { status: 403 }));
	assert.equal(fail.ok, false);
	assert.equal(
		await exchangeOauthCode('c', env, 'https://orbit.almasix.com', async () => new Response('x', { status: 500 })),
		null,
	);
	assert.equal(
		await exchangeOauthCode('c', env, 'https://orbit.almasix.com', async () =>
			new Response(JSON.stringify({}), { status: 200, headers: { 'Content-Type': 'application/json' } }),
		),
		null,
	);
	assert.equal(
		await exchangeOauthCode('c', env, 'https://orbit.almasix.com', async () =>
			new Response('not-json', { status: 200, headers: { 'Content-Type': 'text/plain' } }),
		),
		null,
	);
	assert.equal(
		await exchangeOauthCode('c', env, 'https://orbit.almasix.com', async () =>
			new Response(JSON.stringify({ access_token: 'gho' }), {
				status: 200,
				headers: { 'Content-Type': 'application/json' },
			}),
		),
		'gho',
	);
	const withScope = authorizeUrl(env, 'st', 'https://orbit.almasix.com');
	assert.match(withScope, /scope=public_repo/);
	const noScope = authorizeUrl({ ...env, GITHUB_OAUTH_SCOPE: '' }, 'st', 'https://orbit.almasix.com');
	assert.equal(noScope.includes('scope='), false);
});

test('handleGithubRequest oauth and star', async () => {
	const unconfigured = await handleGithubRequest(request('/api/github/star?repo=acme/kit', { method: 'POST' }), {});
	assert.equal(unconfigured.status, 501);

	const badRepo = await handleGithubRequest(request('/api/github/oauth/start?repo=nope'), env);
	assert.equal(badRepo.status, 400);

	const start = await handleGithubRequest(
		request('/api/github/oauth/start?repo=acme/kit&return=/plugins/kit/'),
		env,
	);
	assert.equal(start.status, 302);
	assert.match(start.headers.get('Location'), /github.com\/login\/oauth\/authorize/);
	const startCookie = start.headers.get('Set-Cookie');
	const nonce = readCookie(startCookie, 'orbit_gh_state');
	const state = new URL(start.headers.get('Location')).searchParams.get('state');

	const denied = await handleGithubRequest(
		request('/api/github/oauth/callback?error=access_denied&state=x'),
		env,
	);
	assert.equal(denied.status, 302);
	assert.match(denied.headers.get('Location'), /star=denied/);

	const mismatch = await handleGithubRequest(
		request(`/api/github/oauth/callback?code=abc&state=${state}`, { cookie: 'orbit_gh_state=other' }),
		env,
	);
	assert.match(mismatch.headers.get('Location'), /star=denied/);

	let calls = 0;
	const mock = async (url, init) => {
		calls += 1;
		if (String(url).includes('access_token')) {
			return new Response(JSON.stringify({ access_token: 'gho' }), { status: 200 });
		}
		assert.equal(init.method, 'PUT');
		return new Response(null, { status: 204 });
	};
	const success = await handleGithubRequest(
		request(`/api/github/oauth/callback?code=abc&state=${encodeURIComponent(state)}`, {
			cookie: `orbit_gh_state=${nonce}`,
		}),
		env,
		{ fetch: mock },
	);
	assert.equal(success.status, 302);
	assert.match(success.headers.get('Location'), /starred=1/);
	assert.equal(calls, 2);

	const tokenFail = await handleGithubRequest(
		request(`/api/github/oauth/callback?code=abc&state=${encodeURIComponent(state)}`, {
			cookie: `orbit_gh_state=${nonce}`,
		}),
		env,
		{ fetch: async () => new Response('no', { status: 400 }) },
	);
	assert.match(tokenFail.headers.get('Location'), /star=token/);

	const apiFail = await handleGithubRequest(
		request(`/api/github/oauth/callback?code=abc&state=${encodeURIComponent(state)}`, {
			cookie: `orbit_gh_state=${nonce}`,
		}),
		env,
		{
			fetch: async (url) => {
				if (String(url).includes('access_token')) {
					return new Response(JSON.stringify({ access_token: 'gho' }), { status: 200 });
				}
				return new Response('no', { status: 500 });
			},
		},
	);
	assert.match(apiFail.headers.get('Location'), /star=api/);

	const needAuth = await handleGithubRequest(
		request('/api/github/star?repo=acme/kit', { method: 'POST' }),
		env,
	);
	assert.equal(needAuth.status, 401);
	const needBody = await needAuth.json();
	assert.match(needBody.authorize, /oauth\/start/);

	const starred = await handleGithubRequest(
		request('/api/github/star?repo=acme/kit', { method: 'POST', cookie: `${TOKEN_COOKIE}=gho` }),
		env,
		{ fetch: async () => new Response(null, { status: 204 }) },
	);
	assert.equal(starred.status, 200);
	assert.equal((await starred.json()).starred, true);

	const already = await handleGithubRequest(
		request('/api/github/star?repo=acme/kit&return=/plugins/kit/', {
			method: 'GET',
			cookie: `${TOKEN_COOKIE}=gho`,
		}),
		env,
		{ fetch: async () => new Response(null, { status: 304 }) },
	);
	assert.equal((await already.json()).already, true);

	const expiredTok = await handleGithubRequest(
		request('/api/github/star?repo=acme/kit', { method: 'POST', cookie: `${TOKEN_COOKIE}=old` }),
		env,
		{ fetch: async () => new Response('no', { status: 401 }) },
	);
	assert.equal(expiredTok.status, 401);

	const githubDown = await handleGithubRequest(
		request('/api/github/star?repo=acme/kit', { method: 'POST', cookie: `${TOKEN_COOKIE}=gho` }),
		env,
		{ fetch: async () => new Response('no', { status: 500 }) },
	);
	assert.equal(githubDown.status, 502);

	const missingRepo = await handleGithubRequest(
		request('/api/github/star', { method: 'POST', cookie: `${TOKEN_COOKIE}=gho` }),
		env,
	);
	assert.equal(missingRepo.status, 400);

	assert.equal((await handleGithubRequest(request('/api/github/nope'), env)).status, 404);
});

test('worker fetch routes assets and github', async () => {
	const api = await worker.fetch(request('/api/github/star?repo=acme/kit', { method: 'POST' }), {});
	assert.equal(api.status, 501);
	const missing = await worker.fetch(request('/plugins/'), {});
	assert.equal(missing.status, 404);
	const assets = await worker.fetch(request('/plugins/'), {
		ASSETS: { fetch: async () => new Response('ok') },
	});
	assert.equal(await assets.text(), 'ok');
});
