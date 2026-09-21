import type { APIRoute } from 'astro';
import { articleToFeedItem, getMarketplaceArticles } from '../../data/marketplace';

/** Machine-readable catalog of every published marketplace article. */
export const GET: APIRoute = async () => {
	const articles = await getMarketplaceArticles();
	const body = {
		generated_at: new Date().toISOString(),
		count: articles.length,
		articles: articles.map(articleToFeedItem),
	};
	return new Response(JSON.stringify(body, null, 2), {
		headers: {
			'Content-Type': 'application/json; charset=utf-8',
			'Cache-Control': 'public, max-age=300',
		},
	});
};
