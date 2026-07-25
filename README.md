# Make-Ware Unraid templates

The monorepo for every [make-ware](https://makeware.io) app published on the Unraid
**Community Applications** store — free, open-source, self-hosted web applications.

Each app lives in its own folder with its Docker template (`*.xml`), icon, screenshots, and
README. Install any of them from the **Apps** tab in Unraid.

## Apps

| App | Description | Image | Source |
| --- | --- | --- | --- |
| **[VideoWare](video-ware/README.md)** | Self-hosted video editor pairing a browser-based timeline editor with a scriptable CLI (`vw`). Upload footage, search it by what's said or seen, cut clips, compose multi-track timelines, and render — by hand, by script, or by an AI agent. All from one container. | `dastron/video-ware:latest` | [make-ware/video-ware](https://github.com/make-ware/video-ware) |

More apps are on the way — each is added here as its own folder.

## Installing

1. In Unraid, open the **Apps** tab (Community Applications).
2. Search for the app name (e.g. **VideoWare**) and click **Install**.
3. Follow the per-app README for configuration details.

### Manual template install (without CA)

In the Unraid **Docker** tab → **Add Container** → **Template** field, paste the app's
template URL, for example:

```
https://raw.githubusercontent.com/make-ware/unraid-templates/main/video-ware/video-ware.xml
```

## Repository layout

```
unraid-templates/
├── ca_profile.xml              # CA repository profile (maintainer page)
├── profile.jpeg                # Maintainer / repository icon
├── LICENSE
├── README.md                   # This file
├── scripts/
│   └── generate-changes.py     # Regenerates each template's <Changes> block from its CHANGELOG.md
└── video-ware/                 # VideoWare app
    ├── video-ware.xml          # Docker app template
    ├── icon.png                # App icon
    ├── images/                 # Screenshots shown in Community Applications
    ├── CHANGELOG.md            # Upstream changelog (feeds the template's <Changes> block)
    └── README.md               # App documentation
```

Each application is built and published from its own repository — for example,
[make-ware/video-ware](https://github.com/make-ware/video-ware). This repo holds only the
Unraid Community Applications metadata (templates, icons, screenshots, and docs).

## Adding a new app

1. Create a folder named after the app (kebab-case).
2. Add `<app>.xml` (the Docker template), `icon.png`, an `images/` folder of screenshots,
   a `CHANGELOG.md`, and a `README.md`.
3. Point the template's `TemplateURL`, `Icon`, and `Screenshot` fields at the raw GitHub
   URLs under `main/<app>/…`.
4. Register the app in `scripts/generate-changes.py` and run it to fill the template's
   `<Changes>` block from the changelog.
5. Add a row to the **Apps** table above.
