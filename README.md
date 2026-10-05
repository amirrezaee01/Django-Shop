# Django Shop

A server-rendered Django storefront with product browsing, customer accounts, a session/database cart, checkout, Zarinpal sandbox payments, reviews, wishlists, and customer/admin dashboards.

## Requirements

- Docker and Docker Compose v2.24+ (recommended), or Python 3.10+
- PostgreSQL for the Compose setup

## Run with Docker Compose

```sh
docker compose up --build
```

The app is available at <http://localhost:8000>, PostgreSQL at `localhost:5432`, and smtp4dev at <http://localhost:5000>. Django migrations run automatically when the backend starts. `GET /health/` returns `{"status":"ok"}` when Django and its database connection are available; Compose uses it as the backend health check. Compose reads the repository-root `.env` for substitutions and passes that file to the backend. Start from `.env.example` with `Copy-Item .env.example .env` in PowerShell or `cp .env.example .env` in a POSIX shell. `.env` is ignored by Git. Values in the old `envs/dev/Django/.env` path are no longer read; move any local values you still need into the root `.env`.

Compose mounts `./core/media` into the backend, so checked-in media and uploaded development files remain visible on the host. PostgreSQL continues to use `./postgres/data`, preserving the original development database location.

If you used the interim `media-data` volume, it is not deleted, but the bind mount will not show its contents. Stop the stack without `-v`, copy those files into `core/media` (preserving existing files), and then restart. Do not remove the old volume until you have confirmed the copied files are present.

Create an administrator with:

```sh
docker compose exec backend python manage.py createsuperuser
```

Compose binds PostgreSQL to loopback and uses the original development defaults (`postgres` database/user/password) to remain compatible with an existing `./postgres/data` cluster created by the earlier Compose setup. These credentials are for local development only. For a fresh local install, you can replace them in `.env`; PostgreSQL initialization variables only apply when its data directory is empty, so changing them does not reconfigure an existing cluster. For a shared or public deployment, configure strong database credentials and explicit host authentication; do not use the development defaults. The sample `SECRET_KEY` and blank merchant ID are development placeholders. Configure a private Django key and a valid `MERCHANT_ID` before production use. Checkout reports a payment configuration error and keeps the cart when the merchant ID is absent.

### Recovering a database created with the interim named volume

The Compose file uses the original `./postgres/data` bind mount again. If you already ran the interim version that used the `postgres-data` named volume, Docker has not deleted that volume. Check `docker volume ls` for the project-prefixed volume name. To keep using it, change the `db` service mount to `postgres-data:/var/lib/postgresql/data` and declare the volume using its actual name:

```yaml
volumes:
  postgres-data:
    external: true
    name: <actual-volume-name-from-docker-volume-ls>
```

Back up the database before changing mounts. Do not run `docker compose down -v`. The named volume and `./postgres/data` are separate PostgreSQL data directories; do not copy one over the other or combine their files. Choose the database containing the data you need, and use PostgreSQL backup/restore tools if you need to consolidate databases.

## Run locally

```sh
python -m venv .venv
# Activate the environment, then:
python -m pip install -r requirements.txt
cd core
python manage.py migrate
python manage.py runserver
```

The default local database is SQLite. Django reads the repository-root `.env` (copy `.env.example` first) and process environment variables; process environment variables take precedence. Set `DEBUG=True` for local HTTP. The development email backend writes messages to the console. PostgreSQL can be selected with `DB_ENGINE=django.db.backends.postgresql` and `PGDB_NAME`, `PGDB_USER`, `PGDB_PASSWORD`, `PGDB_HOST`, and `PGDB_PORT` (use `PGDB_HOST=localhost` outside Compose).

## Configuration

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django signing key; required when `DEBUG=False` |
| `DEBUG` | Enable Django debug mode; defaults to `False` |
| `ALLOWED_HOSTS` | Comma-separated hostnames; defaults to `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins, including scheme |
| `SECURE_SSL_REDIRECT` | Redirect HTTP to HTTPS; defaults to enabled when `DEBUG=False` |
| `TRUST_X_FORWARDED_PROTO` | Trust `X-Forwarded-Proto: https` from a TLS-terminating proxy; defaults to `False` |
| `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD` | HSTS policy; disabled unless explicitly configured |
| `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` | Secure-cookie flags; default to enabled when `DEBUG=False` |
| `DB_ENGINE` | Django database backend; defaults to SQLite |
| `PGDB_NAME`, `PGDB_USER`, `PGDB_PASSWORD`, `PGDB_HOST`, `PGDB_PORT` | PostgreSQL connection settings |
| `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` | Outgoing email configuration |
| `MERCHANT_ID` | Zarinpal sandbox merchant ID |
| `PAYMENT_CALLBACK_URL` | Optional absolute callback URL for non-request payment clients; checkout derives its callback URL from the current request |
| `SHOW_DEBUGGER_TOOLBAR` | Enable the Django Debug Toolbar; defaults to `False` |

Environment files and secrets are intentionally not committed. Production deployments must provide a strong `SECRET_KEY`, allowed hosts, database credentials, secure email/payment configuration, and an HTTPS termination path. Behind a TLS-terminating proxy, set `TRUST_X_FORWARDED_PROTO=True` only when the trusted proxy overwrites/controls `X-Forwarded-Proto`; this lets Django recognize the original HTTPS request and avoids redirect loops. HSTS remains off by default: set a positive `SECURE_HSTS_SECONDS` only after HTTPS is confirmed, and enable subdomains/preload only when every covered hostname is HTTPS-ready.

## Development checks

From `core/` run:

```sh
python manage.py test
python manage.py check
python manage.py check --deploy
```

The deploy check reports settings that a real HTTPS production deployment must configure.

## Project structure

- `core/accounts`, `core/shop`, `core/cart`, `core/order`, and `core/payment` contain the storefront’s domain apps.
- `core/dashboard` contains customer and admin dashboard views.
- `core/templates` and `core/static` contain server-rendered UI assets; `core/media` contains development uploads and checked-in sample media.
- `docker-compose.yml` and `dockerfiles/dev/Django/Dockerfile` define the local container setup.
- `.github/workflows/ci.yml` runs Django checks, migration checks, and tests on pushes and pull requests.

## Development limitations

The payment integration targets Zarinpal’s sandbox and requires a configured merchant ID to create a payment request. The Compose stack is for development, not production: it uses Django’s development server, local sample credentials, and a bind-mounted media directory. Production deployments need a production WSGI/ASGI server, managed HTTPS/static/media serving, strong credentials, and deployment-specific security configuration.
