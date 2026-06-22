# Make-Ware Unraid templates

The monorepo for every [make-ware](https://makeware.io) app published on the Unraid
**Community Applications** store — free, open-source, self-hosted web applications.

Each app lives in its own folder with its Docker template (`*.xml`), icon, screenshots, and
README. Install any of them from the **Apps** tab in Unraid.

## Apps

| App | Description | Image | Source |
| --- | --- | --- | --- |
| **[VideoWare](video-ware/README.md)** | Self-hosted, browser-based video editor. Upload media, create clips, edit timelines, and collaborate in real time — all from one container. | `dastron/video-ware:latest` | [make-ware/video-ware](https://github.com/make-ware/video-ware) |

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
├── ca_profile.xml          # CA repository profile (maintainer page)
├── profile.jpeg            # Maintainer / repository icon
├── LICENSE
├── README.md               # This file
└── video-ware/             # VideoWare app
    ├── video-ware.xml      # Docker app template
    ├── icon.png            # App icon
    ├── images/             # Screenshots shown in Community Applications
    └── README.md           # App documentation
```

Each application is built and published from its own repository — for example,
[make-ware/video-ware](https://github.com/make-ware/video-ware). This repo holds only the
Unraid Community Applications metadata (templates, icons, screenshots, and docs).

## Adding a new app

1. Create a folder named after the app (kebab-case).
2. Add `<app>.xml` (the Docker template), `icon.png`, an `images/` folder of screenshots,
   and a `README.md`.
3. Point the template's `TemplateURL`, `Icon`, and `Screenshot` fields at the raw GitHub
   URLs under `main/<app>/…`.
4. Add a row to the **Apps** table above.
