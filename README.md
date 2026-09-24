# WORMNODES local website

Local editable WORMNODES experience with a generated comic identity, apple-node packages, AAPLB checkout previews, staking language and yield information.

## Run

```bash
python server.py --host 127.0.0.1 --port 4177
```

Open: http://127.0.0.1:4177/

## Production

- Website: https://wormnodes.vercel.app/
- Repository: https://github.com/NachoLLMJS/wormnodes
- Official X account: https://x.com/WormNodes

## Generated brand assets

- `site/assets/media/wormnodes-logo.png` — yellow/orange generated WORMNODES logo
- `site/assets/media/wormnodes-favicon.png` — apple favicon
- `site/assets/media/node-pack-royal.png` — generated Royal apple-node package
- `site/assets/media/node-pack-fuji.png` — generated Fuji apple-node package
- `site/assets/media/node-pack-golden.png` — generated Golden package with golden apples
- `site/assets/media/hero-worm-apple.png` — pink worm holding the matching red apple
- `site/assets/media/wormnodes-scenes/` — five 1500 × 1000 WORMNODES illustrations covering node activation, staking, yield harvesting, lock periods and node tiers
- `source-assets/WORMNODES-banner-1500x500.png` — the 1500 × 500 social banner master

All production package and wordmark images are real image files; they are not HTML drawings.

## Editable files

- `site/index.html` — rendered homepage
- `site/editable/wormnodes.css` — WORMNODES colors, node cards and modal styles
- `site/editable/wormnodes.js` — node modal and AAPLB checkout-preview behavior
- `apply_wormnodes_rebrand.py` — reapplies the WORMNODES transformation
- `prepare_generated_brand_assets.py` — prepares generated transparent brand assets

## Payment status

The AAPLB checkout is intentionally fail-closed. It displays the selected node and AAPLB amount, but it does not claim or submit a transaction until an AAPLB contract address, chain, treasury destination and wallet flow are provided.
