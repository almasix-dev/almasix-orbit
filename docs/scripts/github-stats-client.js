(function () {
	var dash = function (text) {
		var value = String(text || '').trim();
		return value === '—' || value === '-' || value === '–';
	};
	var format = function (n) {
		if (n >= 1000000) {
			var millions = n / 1000000;
			return (millions >= 10 ? Math.round(millions) : String(millions.toFixed(1)).replace(/\.0$/, '')) + 'M';
		}
		if (n >= 1000) {
			var kilos = n / 1000;
			return (kilos >= 10 ? Math.round(kilos) : String(kilos.toFixed(1)).replace(/\.0$/, '')) + 'k';
		}
		return String(n);
	};
	var repoFromHref = function (href) {
		var match = String(href || '').match(/^https:\/\/github\.com\/([\w.-]+)\/([\w.-]+)/i);
		if (!match) return null;
		return match[1] + '/' + match[2].replace(/\.git$/, '');
	};
	var chip = document.querySelector('.gh-chip');
	var starLink = chip && chip.querySelector('[title="GitHub stars"]');
	var starSpan = chip && chip.querySelector('[title="GitHub stars"] span');
	var forkSpan = chip && chip.querySelector('[title="GitHub forks"] span');
	var cards = document.querySelectorAll('[data-plugin]');
	var buttons = document.querySelectorAll('[data-star-repo]');
	var repos = Object.create(null);
	var want = function (repo) {
		if (repo) repos[repo] = true;
	};
	if (
		chip &&
		(dash(starSpan && starSpan.textContent) ||
			dash(forkSpan && forkSpan.textContent) ||
			!chip.querySelector('.gh-chip__release'))
	) {
		want(repoFromHref(starLink && starLink.getAttribute('href')));
	}
	for (var i = 0; i < cards.length; i++) {
		var card = cards[i];
		var strong = card.querySelector('[title="GitHub stars"] strong');
		var rawStars = card.getAttribute('data-stars');
		if (rawStars && !dash(strong && strong.textContent)) continue;
		var search = (card.getAttribute('data-search') || '').match(
			/https:\/\/github\.com\/[\w.-]+\/[\w.-]+/i,
		);
		var link = card.querySelector('a[title="GitHub repository"]');
		want(repoFromHref(search && search[0]) || repoFromHref(link && link.getAttribute('href')));
	}
	for (var j = 0; j < buttons.length; j++) {
		var count = buttons[j].querySelector('[data-star-count]');
		if (dash(count && count.textContent) || !buttons[j].getAttribute('data-star-base')) {
			want(buttons[j].getAttribute('data-star-repo'));
		}
	}
	var names = Object.keys(repos);
	if (!names.length) return;

	var headers = {
		Accept: 'application/vnd.github+json',
		'User-Agent': 'almasix-orbit-docs',
	};
	var shieldNumber = function (payload) {
		var raw = String((payload && (payload.value || payload.message)) || '').replace(/,/g, '');
		if (/^\d+$/.test(raw)) return Number(raw);
		return null;
	};
	var load = function (repo) {
		return fetch('https://api.github.com/repos/' + repo, { headers: headers })
			.then(function (response) {
				if (!response.ok) throw new Error('github');
				return response.json();
			})
			.then(function (data) {
				return {
					stars: typeof data.stargazers_count === 'number' ? data.stargazers_count : null,
					forks: typeof data.forks_count === 'number' ? data.forks_count : null,
					release: null,
				};
			})
			.catch(function () {
				return Promise.all([
					fetch('https://img.shields.io/github/stars/' + repo + '.json').then(function (response) {
						return response.json();
					}),
					fetch('https://img.shields.io/github/forks/' + repo + '.json').then(function (response) {
						return response.json();
					}),
				])
					.then(function (pair) {
						return { stars: shieldNumber(pair[0]), forks: shieldNumber(pair[1]), release: null };
					})
					.catch(function () {
						return { stars: null, forks: null, release: null };
					});
			})
			.then(function (stats) {
				return fetch('https://api.github.com/repos/' + repo + '/releases/latest', { headers: headers })
					.then(function (response) {
						if (!response.ok) return stats;
						return response.json().then(function (release) {
							stats.release = release && release.tag_name ? release.tag_name : null;
							return stats;
						});
					})
					.catch(function () {
						return stats;
					});
			});
	};

	names.forEach(function (repo) {
		load(repo).then(function (stats) {
			if (!stats) return;
			if (chip && repoFromHref(starLink && starLink.getAttribute('href')) === repo) {
				if (starSpan && dash(starSpan.textContent) && stats.stars != null) {
					starSpan.textContent = format(stats.stars);
				}
				if (forkSpan && dash(forkSpan.textContent) && stats.forks != null) {
					forkSpan.textContent = format(stats.forks);
				}
				if (stats.release && chip && !chip.querySelector('.gh-chip__release')) {
					var anchor = document.createElement('a');
					anchor.className = 'gh-chip__part gh-chip__release';
					var scoped = chip.querySelector('.gh-chip__part');
					if (scoped) {
						scoped.classList.forEach(function (name) {
							if (name.indexOf('astro-') === 0) anchor.classList.add(name);
						});
					}
					anchor.href = 'https://github.com/' + repo + '/releases';
					anchor.textContent = stats.release;
					chip.insertBefore(anchor, chip.firstChild);
				}
			}
			for (var c = 0; c < cards.length; c++) {
				var item = cards[c];
				var found = (item.getAttribute('data-search') || '').match(
					/https:\/\/github\.com\/[\w.-]+\/[\w.-]+/i,
				);
				var repoLink = item.querySelector('a[title="GitHub repository"]');
				var cardRepo =
					repoFromHref(found && found[0]) || repoFromHref(repoLink && repoLink.getAttribute('href'));
				if (cardRepo !== repo || stats.stars == null) continue;
				if (!item.getAttribute('data-stars')) item.setAttribute('data-stars', String(stats.stars));
				var starStrong = item.querySelector('[title="GitHub stars"] strong');
				if (starStrong && dash(starStrong.textContent)) starStrong.textContent = format(stats.stars);
			}
			for (var b = 0; b < buttons.length; b++) {
				if (buttons[b].getAttribute('data-star-repo') !== repo || stats.stars == null) continue;
				if (!buttons[b].getAttribute('data-star-base')) {
					buttons[b].setAttribute('data-star-base', String(stats.stars));
				}
				var label = buttons[b].querySelector('[data-star-count]');
				if (label && dash(label.textContent)) label.textContent = format(stats.stars);
				var slug = buttons[b].getAttribute('data-star-slug');
				if (!slug) continue;
				var pageCount = document.querySelector('[data-star-count-page="' + CSS.escape(slug) + '"]');
				if (pageCount && dash(pageCount.textContent)) pageCount.textContent = format(stats.stars);
			}
		});
	});
})();
