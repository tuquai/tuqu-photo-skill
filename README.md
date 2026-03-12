# Tuqu Photo API Skill

A local skill package for working with the Tuqu Dream Weaver photo and billing APIs, with a Python helper for consistent request handling.

## Quick Start

Set the environment variables used by the skill and helper:

```bash
export TUQU_BASE_URL=https://photo.tuqu.ai
export TUQU_BILLING_BASE_URL=https://billing.tuqu.ai/dream-weaver
export TUQU_USER_KEY=your_user_key
export TUQU_API_KEY=your_api_key
export TUQU_SERVICE_KEY=your_service_key
```

Run the bundled helper from the skill directory:

```bash
python3 tuqu-photo-api/scripts/tuqu_request.py GET /api/catalog --query type=all
python3 tuqu-photo-api/scripts/tuqu_request.py POST /api/enhance-prompt \
  --json '{"category":"portrait","prompt":"soft editorial portrait with window light"}'
python3 tuqu-photo-api/scripts/tuqu_request.py POST /api/v2/generate-image \
  --json '{"prompt":"cinematic portrait in warm sunset light"}'
python3 tuqu-photo-api/scripts/tuqu_request.py POST /api/billing/balance
```

The helper auto-selects the correct host and authentication mode for the supported endpoints.

## Features

- Covers Tuqu photo generation, preset application, prompt enhancement, catalog lookup, character management, history, balance, and recharge flows
- Encodes the host and auth rules that are easy to get wrong when calling the APIs manually
- Includes endpoint-level reference docs and workflow recipes for common tasks
- Ships a small Python request helper for repeatable local testing

## Repository Layout

```text
tuqu-photo-api/
  SKILL.md                  Main skill instructions
  references/
    endpoints.md            Endpoint request and response details
    workflows.md            Task-oriented API workflows
  scripts/
    tuqu_request.py         Local request helper
dist/
  tuqu-photo-api.skill      Generated skill artifact
```

## Configuration

| Variable | Required For | Notes |
| --- | --- | --- |
| `TUQU_BASE_URL` | Photo, catalog, history, and balance APIs | Defaults to `https://photo.tuqu.ai` |
| `TUQU_BILLING_BASE_URL` | Recharge APIs | Defaults to `https://billing.tuqu.ai/dream-weaver` |
| `TUQU_USER_KEY` | `/api/v2/*`, `/api/billing/balance` | Sent in the JSON body as `userKey` |
| `TUQU_API_KEY` | `/api/characters`, `/api/history` | Sent as `x-api-key` |
| `TUQU_SERVICE_KEY` | Recharge endpoints | Sent as `Authorization: Bearer <serviceKey>` |

`serviceKey` and `userKey` refer to the same underlying credential, but the APIs expect them in different places depending on the endpoint.

## Common Tasks

- Discover presets and styles: `GET /api/catalog`
- Improve a prompt before generation: `POST /api/enhance-prompt`
- Generate from text or reference images: `POST /api/v2/generate-image`
- Generate from a preset: `GET /api/catalog` then `POST /api/v2/apply-preset`
- Generate with saved characters: `/api/characters` then `POST /api/v2/generate-for-character`
- Check credits: `POST /api/billing/balance`
- Start a recharge flow: `GET /api/v1/recharge/plans`, then `POST /api/v1/recharge/wechat` or `POST /api/v1/recharge/stripe`

## Documentation

- [Skill instructions](./tuqu-photo-api/SKILL.md)
- [Endpoint reference](./tuqu-photo-api/references/endpoints.md)
- [Workflow recipes](./tuqu-photo-api/references/workflows.md)

## Development Notes

- Use `tuqu-photo-api/scripts/tuqu_request.py` instead of ad-hoc `curl` when possible.
- Keep the endpoint/auth rules in `SKILL.md` aligned with the helper logic in `scripts/tuqu_request.py`.
- Treat `dist/` as generated output.

## License

No license file is currently included in this repository.
