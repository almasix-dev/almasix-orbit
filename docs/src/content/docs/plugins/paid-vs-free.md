---
title: Paid vs free
description: How commercial and free Orbit plugins are listed, distributed, and reviewed — pricing, licensing, and what buyers should expect.
---

The marketplace lists both kinds of plugin side by side, and visitors can filter by price. What changes between them is distribution and review, not visibility.

## The short version

| | Free | Paid |
|---|------|------|
| Distribution | Public PyPI package | Your store, your installer or private index |
| Registry field | `price: free` + `package` | `price: { amount, currency }` + `checkout_url` |
| Source | Public repository expected | Private repository allowed |
| Card CTA | Install command and “View source” | “Buy for $79” linking to your checkout |
| Review | Public code review | Same checks, plus a private source review |
| Money | — | Handled entirely by you |

Orbit does not process payments, hold funds, issue licenses, or take a commission. A paid listing is a well-presented link to your own store.

## Listing a free plugin

Publish to PyPI, then set:

```yaml
price: free
package: acme-orbit-audit-log
repository: https://github.com/your-handle/acme-orbit-audit-log
```

The listing renders `pip install acme-orbit-audit-log` and links to your source. A free plugin without a PyPI package must at least give a public `repository` so people can install it from a checkout.

## Listing a paid plugin

Set an amount, a currency, and the page where a buyer completes the purchase:

```yaml
price:
  amount: 79
  currency: USD
checkout_url: https://store.example.com/acme-audit-log-pro
```

Prices are shown exactly as listed, in your currency. Keep the registry value in sync with your store — a listing whose price no longer matches its checkout gets unlisted until it is corrected.

You can sell through any service that can take payment and deliver a wheel or a private index credential. Common choices are a hosted store front, a private PyPI index, or a licensed download after purchase. Whatever you use, the buyer must be able to complete a purchase and get the package from the URL you list.

### What we ask of commercial authors

- **Private source review.** Before a paid listing is approved, give a maintainer read access to the private repository, or send a copy of the wheel. We check the same things as a public plugin: packaging hygiene, no namespace stomping, no hidden network calls, no obfuscated code. We do not redistribute what we review.
- **A clear license.** State what a purchase buys: how many projects or developers, whether updates are included, and for how long.
- **Working support channel.** An email address or issue tracker the buyer can reach.
- **Honest requirements.** List the Orbit versions you support and any external services the plugin needs.
- **Refund policy.** Publish one on your store. Refund disputes are between you and the buyer.

### What we will not list

- Plugins where the checkout link does not work, requires an account to see a price, or leads to a general marketing site rather than a purchase page.
- “Free” listings that install a trial and then demand payment to keep working. If money is required, price it.
- Plugins that phone home with telemetry the buyer did not agree to, or that enforce licensing by contacting a server on every request without saying so on the listing.
- Paid plugins whose author will not allow a source review.

## Free and paid editions of the same plugin

Ship two entries: a free `acme-audit-log` and a paid `acme-audit-log-pro`. Each needs its own YAML file, thumbnail, and description, and each should say plainly what the other does or does not include. Do not use the free listing as an advert with no working functionality.

## Sponsoring

Free plugins can add a `sponsor_url` to their author profile. It renders on the author page, so a plugin can stay free while still being funded.

## Buying safely

If you are on the buying side, remember that a plugin runs with full access to your application:

- Prefer plugins whose source you can read, or whose author you can identify.
- Check that `orbit_versions` covers the release you run.
- Only listings marked **Official** are maintained by Almasix. Everything else is third-party and unreviewed for security by us, apart from the one-time packaging review described above.
- Payment problems go to the author’s store. Security problems can also come to [our advisories page](https://github.com/almasix-dev/almasix-orbit/security/advisories/new).

## Related

- [Using a plugin](/plugins/using/) — install after you buy or `pip install`
- [Get listed](/plugins/get-listed/) — submission steps and fields
- [Listing guidelines](/plugins/guidelines/) — the review checklist
- [Browse the marketplace](/plugins/) — see how listings render
