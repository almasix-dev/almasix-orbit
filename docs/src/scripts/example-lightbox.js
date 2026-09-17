/**
 * Lightbox for Orbit example screenshots (/examples/{light|dark}/…).
 *
 * Inlined into <head> by astro.config.mjs — must be self-contained.
 * Click (or Enter/Space on the focused control) opens the image full-size.
 */
(() => {
	const SELECTOR = '.sl-markdown-content img[src*="/examples/"]';

	/** @type {HTMLDialogElement | null} */
	let dialog = null;
	/** @type {HTMLImageElement | null} */
	let dialogImg = null;
	/** @type {HTMLElement | null} */
	let dialogCaption = null;
	/** @type {HTMLElement | null} */
	let lastFocus = null;

	const ensure = () => {
		if (dialog) return dialog;
		dialog = document.createElement('dialog');
		dialog.className = 'or-lightbox';
		dialog.setAttribute('aria-label', 'Screenshot preview');
		dialog.innerHTML = `
			<form method="dialog" class="or-lightbox__chrome">
				<button type="submit" class="or-lightbox__close" aria-label="Close">
					<span aria-hidden="true">×</span>
				</button>
			</form>
			<figure class="or-lightbox__figure">
				<img class="or-lightbox__img" alt="" />
				<figcaption class="or-lightbox__caption"></figcaption>
			</figure>
		`;
		document.body.appendChild(dialog);
		dialogImg = dialog.querySelector('.or-lightbox__img');
		dialogCaption = dialog.querySelector('.or-lightbox__caption');

		dialog.addEventListener('click', (event) => {
			if (event.target === dialog) dialog.close();
		});
		dialog.addEventListener('close', () => {
			document.documentElement.classList.remove('or-lightbox-open');
			if (dialogImg) {
				dialogImg.removeAttribute('src');
				dialogImg.alt = '';
			}
			if (dialogCaption) dialogCaption.textContent = '';
			if (lastFocus instanceof HTMLElement) lastFocus.focus({ preventScroll: true });
			lastFocus = null;
		});
		return dialog;
	};

	const open = (img) => {
		if (!(img instanceof HTMLImageElement)) return;
		const box = ensure();
		if (!dialogImg || !dialogCaption) return;
		lastFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
		dialogImg.src = img.currentSrc || img.src;
		dialogImg.alt = img.alt || 'Screenshot';
		dialogCaption.textContent = img.alt || '';
		document.documentElement.classList.add('or-lightbox-open');
		if (typeof box.showModal === 'function') box.showModal();
		else box.setAttribute('open', '');
		box.querySelector('.or-lightbox__close')?.focus({ preventScroll: true });
	};

	const decorate = (root = document) => {
		for (const img of root.querySelectorAll(SELECTOR)) {
			if (!(img instanceof HTMLImageElement) || img.dataset.lightbox === '1') continue;
			img.dataset.lightbox = '1';
			img.classList.add('or-lightbox-trigger');
			img.setAttribute('tabindex', '0');
			img.setAttribute('role', 'button');
			img.setAttribute('aria-label', `View larger: ${img.alt || 'screenshot'}`);
			img.setAttribute('title', 'Click to enlarge');
		}
	};

	document.addEventListener('click', (event) => {
		const target = event.target;
		if (!(target instanceof Element)) return;
		const img = target.closest(SELECTOR);
		if (!(img instanceof HTMLImageElement)) return;
		if (getComputedStyle(img).display === 'none') return;
		event.preventDefault();
		open(img);
	});

	document.addEventListener('keydown', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLImageElement)) return;
		if (!target.matches(SELECTOR)) return;
		if (event.key !== 'Enter' && event.key !== ' ') return;
		event.preventDefault();
		open(target);
	});

	document.addEventListener('DOMContentLoaded', () => decorate());
	document.addEventListener('astro:page-load', () => decorate());
})();
