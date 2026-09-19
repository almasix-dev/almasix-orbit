/**
 * Resolve a sidebar link's group breadcrumb for prev/next labels.
 * e.g. Tables · Columns · Overview
 */

export type SidebarLinkLike = {
	type: 'link';
	label: string;
	href: string;
};

export type SidebarGroupLike = {
	type: 'group';
	label: string;
	entries: SidebarEntryLike[];
};

export type SidebarEntryLike = SidebarLinkLike | SidebarGroupLike;

function isGroup(entry: SidebarEntryLike): entry is SidebarGroupLike {
	return entry.type === 'group';
}

function normalizeHref(href: string): string {
	try {
		const path = href.includes('://') ? new URL(href).pathname : href;
		return path.replace(/\/+$/, '') || '/';
	} catch {
		return href.replace(/\/+$/, '') || '/';
	}
}

function walk(
	entries: SidebarEntryLike[],
	target: string,
	ancestors: string[],
): string[] | null {
	for (const entry of entries) {
		if (isGroup(entry)) {
			const found = walk(entry.entries, target, [...ancestors, entry.label]);
			if (found) return found;
			continue;
		}
		if (normalizeHref(entry.href) === target) {
			return [...ancestors, entry.label];
		}
	}
	return null;
}

/** Return "Tables · Columns · Overview" or the bare label if not found. */
export function sidebarPathLabel(
	sidebar: SidebarEntryLike[] | undefined,
	href: string | undefined,
	fallbackLabel: string,
): string {
	if (!sidebar?.length || !href) return fallbackLabel;
	const path = walk(sidebar, normalizeHref(href), []);
	if (!path?.length) return fallbackLabel;
	return path.join(' · ');
}
