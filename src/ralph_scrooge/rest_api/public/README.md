# URL aliases

In case you have noticed that there are some URLs in `v0.10` hierarchy which
doesn't have their own modules/views in `v0_10` folder (e.g., `api-token-auth`
`pricing-service-usages`, `team-time-division`) - that's intentional, as they
are simply aliases to `v0.9` views (see `ralph_scrooge.urls`).
