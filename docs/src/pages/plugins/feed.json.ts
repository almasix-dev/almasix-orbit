import type { APIRoute } from 'astro';
import { getMarketplacePlugins, pluginToFeedItem } from '../../data/marketplace';

/** Machine-readable catalog of every published listing. */
export const GET: APIRoute = async () => {
	const plugins = await getMarketplacePlugins();
	const body = {
		generated_at: new Date().toISOString(),
		count: plugins.length,
		plugins: plugins.map(pluginToFeedItem),
	};
	return new Response(JSON.stringify(body, null, 2), {
		headers: {
			'Content-Type': 'application/json; charset=utf-8',
			'Cache-Control': 'public, max-age=300',
		},
	});
};
