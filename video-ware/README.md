# VideoWare for Unraid

Unraid Community Applications template for **VideoWare** — a free, open-source, self-hosted
video editor that runs in your browser. Upload media, get fast previews (thumbnails &
sprites), edit and render clips on a timeline, and collaborate with other users on the same
project in real time — all from one container. Optionally enable Video Intelligence to unlock
universal search across your media (entirely optional).

> **One container, one port, one data path.** This template runs the *monolithic*
> VideoWare image, which bundles the web app, database, background worker, and its job
> broker together. There are no sidecar containers to set up and no external Redis or
> database to manage.

---

## Features

- **Runs in your browser** — nothing to install on the client
- **Real-time collaboration** — multiple users editing the same project at once
- **Upload media** with progress tracking and validation
- **Fast previews** — thumbnails and hover sprites generated in the background
- **Clip editing & timeline rendering** — compose and export final videos
- **FFmpeg-powered** transcoding and rendering, built in
- **Universal search** *(optional)* — enable Video Intelligence to find clips by what's actually in them
- **Flexible storage** — local appdata by default, or any S3-compatible bucket
- **Built-in auth & API** via PocketBase, with a realtime database and admin UI
- **Free & open source**

## What's inside the container

The monolithic image is fully self-contained. A single container runs:

| Service        | Role                                                          |
| -------------- | ------------------------------------------------------------- |
| **Next.js**    | The web application (upload, browse, edit, render)            |
| **PocketBase** | Database, auth, realtime updates, and REST API                |
| **Worker**     | NestJS + FFmpeg background processor (transcode, sprites, render, labels) |
| **Redis**      | Internal BullMQ job broker — `localhost` only, never exposed  |
| **Nginx**      | Reverse proxy fronting everything on a single port            |

You only ever map **one port** and **one volume**.

---

## Installation (Community Applications)

1. In Unraid, open the **Apps** tab (Community Applications).
2. Search for **VideoWare** and click **Install**.
3. Set a strong **Admin Password** (and optionally change the **Admin Email**). The
   PocketBase superuser is created automatically on first boot from these values —
   leaving the password blank/default skips superuser creation.
4. Adjust the **WebUI Port** and **App Data** path if you like (defaults are fine for
   most setups).
5. Click **Apply** and wait for the container to start.

When it's up, click the container's **WebUI** button, or browse to:

- **Web app:** `http://<UNRAID-IP>:<PORT>/`
- **PocketBase admin:** `http://<UNRAID-IP>:<PORT>/_/`
- **PocketBase API:** `http://<UNRAID-IP>:<PORT>/api/`

> First boot takes a few moments while the database initializes. If the web app shows a
> connection error, give it ~30 seconds and refresh.

### Manual template install (without CA)

If you aren't using Community Applications, you can add the template directly. In the
Unraid **Docker** tab → **Add Container** → **Template** field, paste:

```
https://raw.githubusercontent.com/make-ware/unraid-templates/main/video-ware/video-ware.xml
```

---

## Configuration

These map to the fields shown in the Unraid template:

| Setting            | Variable / Target          | Default                          | Notes                                                                 |
| ------------------ | -------------------------- | -------------------------------- | --------------------------------------------------------------------- |
| **WebUI Port**     | container port `80`        | `8888`                           | Host port for the web app, API, and admin (all proxied by nginx).     |
| **App Data**       | `/data`                    | `/mnt/user/appdata/video-ware`   | Persistent storage — database, uploaded media, and the Redis queue.   |
| **Admin Email**    | `POCKETBASE_ADMIN_EMAIL`   | `admin@example.com`              | Email for the auto-created PocketBase superuser.                      |
| **Admin Password** | `POCKETBASE_ADMIN_PASSWORD`| _(required)_                     | **Must be set.** Password for the superuser.                          |
| **Storage Type**   | `STORAGE_TYPE`             | `local`                          | `local` (files under `/data`) or `s3`. *(advanced)*                   |
| **Log Level**      | `LOG_LEVEL`                | `warn`                           | `error`, `warn`, `info`, `debug`, or `verbose`. *(advanced)*          |

### Optional: S3-compatible storage

Set **Storage Type** to `s3` and add these variables (Add another Path, Port, Variable…):

| Variable                      | Required | Notes                                                          |
| ----------------------------- | -------- | -------------------------------------------------------------- |
| `STORAGE_S3_BUCKET`           | Yes      | Bucket name                                                    |
| `STORAGE_S3_REGION`           | Yes      | e.g. `us-east-1` (use `garage` for Garage)                     |
| `STORAGE_S3_ACCESS_KEY_ID`    | Yes      | Access key ID                                                  |
| `STORAGE_S3_SECRET_ACCESS_KEY`| Yes      | Secret access key                                              |
| `STORAGE_S3_ENDPOINT`         |          | Defaults to `https://s3.<region>.amazonaws.com`                |
| `STORAGE_S3_FORCE_PATH_STYLE` |          | `true` for MinIO/Garage-style endpoints                        |

### Optional: Video Intelligence & universal search (Google Cloud)

VideoWare is fully functional without this. If you want **universal search** — finding clips
by what's actually in them (objects, faces, people, spoken words, shot changes) — add
`GOOGLE_PROJECT_ID`, `GOOGLE_CLOUD_CREDENTIALS` (inline service-account JSON), and `GCS_BUCKET`
to enable Google Cloud Video Intelligence. This is entirely optional. See the project README
for details.

### Exposing via Cloudflare Tunnel (cloudflared)

VideoWare works behind a **Cloudflare Tunnel** (`cloudflared`), so you can expose it to the
internet without opening ports on your firewall. Cloudflare proxies a request body size limit
(100 MB on free plans), which normally blocks large media uploads — but VideoWare uploads files
in **multipart (chunked) uploads**, keeping each chunk under that limit.

---

## Data, backups & updates

All persistent state lives under the single **App Data** mount (`/data`):

```
/mnt/user/appdata/video-ware/
├── pb_data/    # PocketBase database
├── storage/    # Uploaded media and derivatives (when STORAGE_TYPE=local)
└── redis/      # BullMQ job queue (AOF persistence)
```

- **Back up:** include `/mnt/user/appdata/video-ware` in your appdata backup (e.g. the
  *CA Appdata Backup/Restore* plugin). That single folder is the whole app.
- **Update:** when a new image is published, Unraid's Docker tab shows an update — click
  **Apply Update**. Your data persists across updates.

---

## Support & links

- **Issues / support:** https://github.com/make-ware/video-ware/issues
- **Application source:** https://github.com/make-ware/video-ware
- **Container image:** `ghcr.io/make-ware/video-ware:latest`

## This repository

This repo holds only the Unraid Community Applications metadata. VideoWare lives in its own
folder:

```
unraid-templates/
├── ca_profile.xml            # CA repository profile
├── icon.png                  # Repository / maintainer icon
├── README.md                 # Repository overview
└── video-ware/
    ├── video-ware.xml        # Docker app template (monolithic image)
    ├── icon.png              # App icon
    ├── README.md             # This file
    └── images/               # Screenshots shown in Community Applications
```

The application itself is built and published from
[make-ware/video-ware](https://github.com/make-ware/video-ware).
