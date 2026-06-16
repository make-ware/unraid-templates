# make-ware Unraid templates

Unraid Community Applications templates for [make-ware](https://makeware.io) — free,
open-source, self-hosted web applications. Install them from the **Apps** tab in Unraid.

## Apps

- **[VideoWare](video-ware/README.md)** — self-hosted, browser-based video editor. Upload
  media, create clips, edit timelines, and collaborate in real time, all from one container.

## Repository layout

```
unraid-templates/
├── ca_profile.xml          # CA repository profile (maintainer page)
├── icon.png                # Repository / maintainer icon
├── README.md               # This file
└── video-ware/             # VideoWare app
    ├── video-ware.xml      # Docker app template
    ├── icon.png            # App icon
    ├── images/             # Screenshots
    └── README.md           # App documentation
```

Each application is built and published from its own repository — for example,
[make-ware/video-ware](https://github.com/make-ware/video-ware).
