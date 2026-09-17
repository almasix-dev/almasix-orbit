/**
 * Orbit landing term-code carousel — same behaviour as almasix-website hero slides.
 * Inlined into <head> / loaded by OrbitHero; must stay self-contained.
 */
(() => {
	const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	const SLIDE_MS = 3400;
	const HOLD_AFTER_TYPE_MS = 1400;
	const TYPE_BASE_MS = 16;
	const TYPE_SPACE_MS = 5;

	if (!reduce) {
		document.documentElement.classList.add('motion');
	}

	const boot = () => {
		const root = document.querySelector('[data-hero-slides]');
		if (!(root instanceof HTMLElement)) return;

		const slides = [...root.querySelectorAll('[data-slide]')];
		const dots = [...root.querySelectorAll('[data-goto]')];
		const progress = root.querySelector('.term-progress span');
		const pinBtn = root.querySelector('[data-pin]');
		let i = 0;
		let pinned = false;
		let held = false;
		let timer = 0;
		let typeGen = 0;
		let scheduleToken = 0;
		/** @type {Promise<void> | null} */
		let typingPromise = null;

		const isPlaying = () => !reduce && !pinned && !held && slides.length > 1;
		const isPaused = () => pinned || held;

		const collectTextNodes = (el) => {
			/** @type {Text[]} */
			const nodes = [];
			const walk = (node) => {
				if (node.nodeType === Node.TEXT_NODE) {
					if (node.nodeValue) nodes.push(/** @type {Text} */ (node));
				} else if (node.nodeType === Node.ELEMENT_NODE) {
					for (const child of node.childNodes) walk(child);
				}
			};
			walk(el);
			return nodes;
		};

		const restoreCodeBlocks = (slide) => {
			slide.querySelectorAll('.term-code code').forEach((code) => {
				if (code instanceof HTMLElement && code.dataset.fullHtml) {
					code.innerHTML = code.dataset.fullHtml;
				}
			});
		};

		const snapshotCodeBlocks = (slide) => {
			slide.querySelectorAll('.term-code code').forEach((code) => {
				if (code instanceof HTMLElement && !code.dataset.fullHtml) {
					code.dataset.fullHtml = code.innerHTML;
				}
			});
		};

		const sleep = (ms) =>
			new Promise((resolve) => {
				window.setTimeout(resolve, ms);
			});

		const waitWhilePaused = async (gen) => {
			while (isPaused() && gen === typeGen) {
				await sleep(80);
			}
		};

		const estimateTypeMs = (text) => {
			let total = 0;
			for (const ch of text) {
				total += /\s/.test(ch) ? TYPE_SPACE_MS : TYPE_BASE_MS;
			}
			return total;
		};

		const typeCodeSlide = async (slide, gen) => {
			const codeEls = [...slide.querySelectorAll('.term-code code')].filter(
				(el) => el instanceof HTMLElement,
			);
			if (!codeEls.length) return 0;

			slide.classList.add('is-code-typing');
			slide.classList.remove('is-typed');

			let typedMs = 0;
			for (const code of codeEls) {
				if (!(code instanceof HTMLElement)) continue;
				if (!code.dataset.fullHtml) code.dataset.fullHtml = code.innerHTML;
				code.innerHTML = code.dataset.fullHtml;
				const nodes = collectTextNodes(code);
				const originals = nodes.map((n) => n.nodeValue ?? '');
				nodes.forEach((n) => {
					n.nodeValue = '';
				});

				for (let ni = 0; ni < nodes.length; ni++) {
					const full = originals[ni];
					for (let ci = 0; ci < full.length; ci++) {
						if (gen !== typeGen) return typedMs;
						await waitWhilePaused(gen);
						if (gen !== typeGen) return typedMs;
						nodes[ni].nodeValue = full.slice(0, ci + 1);
						const delay = /\s/.test(full[ci]) ? TYPE_SPACE_MS : TYPE_BASE_MS;
						typedMs += delay;
						await sleep(delay);
					}
				}
			}

			if (gen === typeGen) slide.classList.add('is-typed');
			return typedMs;
		};

		const abortTyping = () => {
			typeGen += 1;
			typingPromise = null;
			slides.forEach((slide) => {
				slide.classList.remove('is-code-typing', 'is-typed');
				restoreCodeBlocks(slide);
			});
		};

		const syncChrome = () => {
			root.classList.toggle('is-held', held || pinned);
			root.classList.toggle('is-pinned', pinned);
			root.classList.toggle('is-playing', isPlaying());
			if (pinBtn instanceof HTMLButtonElement) {
				pinBtn.setAttribute('aria-pressed', pinned ? 'true' : 'false');
				pinBtn.textContent = pinned ? 'Pinned' : 'Pin step';
			}
			dots.forEach((dot, idx) => {
				dot.setAttribute('aria-selected', idx === i ? 'true' : 'false');
				dot.classList.toggle('is-active', idx === i);
			});
		};

		const setProgressMs = (ms) => {
			root.style.setProperty('--slide-ms', `${Math.max(ms, 600)}ms`);
		};

		const restartProgress = () => {
			if (!(progress instanceof HTMLElement)) return;
			progress.style.animation = 'none';
			void progress.offsetWidth;
			progress.style.animation = '';
		};

		const freezeProgress = () => {
			if (!(progress instanceof HTMLElement)) return;
			progress.style.animationPlayState = 'paused';
		};

		const stopTimer = () => {
			window.clearTimeout(timer);
			timer = 0;
		};

		const show = (n, { animate = true } = {}) => {
			abortTyping();
			i = ((n % slides.length) + slides.length) % slides.length;
			const active = slides[i];
			slides.forEach((el, idx) => {
				el.classList.toggle('is-active', idx === i);
				el.classList.remove('is-typing', 'is-code-typing', 'is-typed');
				if (idx !== i) restoreCodeBlocks(el);
			});

			snapshotCodeBlocks(active);
			const hasCode = Boolean(active.querySelector('.term-code'));
			const holdMs = Number(active.getAttribute('data-ms')) || SLIDE_MS;

			if (animate && !reduce) {
				void active.offsetWidth;
				active.classList.add('is-typing');
			}

			syncChrome();

			if (reduce || !animate) {
				setProgressMs(holdMs);
				if (isPlaying()) restartProgress();
				else freezeProgress();
				return;
			}

			if (hasCode) {
				const codeText = [...active.querySelectorAll('.term-code code')]
					.map((el) => el.textContent ?? '')
					.join('');
				const typeMs = estimateTypeMs(codeText);
				setProgressMs(typeMs + HOLD_AFTER_TYPE_MS);
				if (isPlaying()) restartProgress();
				else freezeProgress();

				const gen = typeGen;
				typingPromise = typeCodeSlide(active, gen).finally(() => {
					if (gen === typeGen) typingPromise = null;
				});
			} else {
				setProgressMs(holdMs);
				if (isPlaying()) restartProgress();
				else freezeProgress();
			}
		};

		const schedule = () => {
			stopTimer();
			const token = ++scheduleToken;
			syncChrome();
			if (!isPlaying()) {
				freezeProgress();
				return;
			}

			const active = slides[i];
			const hasCode = Boolean(active.querySelector('.term-code'));
			const holdMs = Number(active.getAttribute('data-ms')) || SLIDE_MS;

			const advance = () => {
				if (token !== scheduleToken) return;
				show(i + 1);
				schedule();
			};

			if (hasCode) {
				const pending = typingPromise ?? Promise.resolve();
				pending.then(async () => {
					if (token !== scheduleToken || !isPlaying()) return;
					await waitWhilePaused(typeGen);
					if (token !== scheduleToken || !isPlaying()) return;
					restartProgress();
					setProgressMs(HOLD_AFTER_TYPE_MS);
					timer = window.setTimeout(advance, HOLD_AFTER_TYPE_MS);
				});
			} else {
				restartProgress();
				timer = window.setTimeout(advance, holdMs);
			}
		};

		const hold = (on) => {
			held = on;
			syncChrome();
			if (isPaused()) {
				stopTimer();
				freezeProgress();
				return;
			}
			if (typingPromise) {
				restartProgress();
				return;
			}
			schedule();
		};

		const goTo = (n, { pin = false } = {}) => {
			if (pin) pinned = true;
			show(n);
			schedule();
		};

		slides.forEach(snapshotCodeBlocks);
		show(0);
		if (!reduce && slides.length > 1) schedule();

		root.addEventListener('mouseenter', () => hold(true));
		root.addEventListener('mouseleave', () => hold(false));
		root.addEventListener('focusin', () => hold(true));
		root.addEventListener('focusout', (event) => {
			if (!root.contains(/** @type {Node | null} */ (event.relatedTarget))) hold(false);
		});

		pinBtn?.addEventListener('click', () => {
			pinned = !pinned;
			schedule();
		});

		dots.forEach((dot) => {
			dot.addEventListener('click', () => {
				const n = Number(dot.getAttribute('data-goto'));
				if (Number.isFinite(n)) goTo(n, { pin: true });
			});
		});

		root.addEventListener('keydown', (event) => {
			if (event.key === 'ArrowRight') {
				event.preventDefault();
				goTo(i + 1, { pin: true });
			} else if (event.key === 'ArrowLeft') {
				event.preventDefault();
				goTo(i - 1, { pin: true });
			} else if (event.key === ' ' || event.key === 'Enter') {
				if (event.target === root) {
					event.preventDefault();
					pinned = !pinned;
					schedule();
				}
			}
		});
	};

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', boot);
	} else {
		boot();
	}
})();
