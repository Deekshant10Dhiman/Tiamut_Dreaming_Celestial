# Tiamut Validator (Vercel)

Flag-checking site for the **Tiamut, the Dreaming Celestial** reverse engineering challenge.
Players submit the trace-tag printed by `./tiamut` when the dream ends in `AWAKE`. If it matches, the site returns the flag.

Python standard library only. No dependencies, no `requirements.txt`.

## Layout

```
.
├── api/
│   └── index.py     # the whole app (Vercel Python serverless function)
├── vercel.json      # routes every path to api/index.py
└── README.md
```

## Configuration

Both values are hardcoded at the top of `api/index.py`:

| Constant | Value |
|----------|-------|
| `TAG`    | `6571e95b` |
| `FLAG`   | `GDG{tiamut_is_awake_now_you_face_arishem}` |

`TAG` is the trace-tag of the AWAKE run (the output of `./tiamut 7E4A91 1D0C5B B3A6F2 2C99E7`).
If you rebuild the challenge ROM, regenerate the binary, run it with the new waking word, and update `TAG` to match.

## Deploy

**Vercel CLI**

```bash
npm i -g vercel
cd tiamut_vercel
vercel --prod
```

**GitHub**

1. Push this folder to a repository.
2. In Vercel, choose *Add New → Project* and import the repository.
3. Leave the framework preset as *Other* and deploy.

## Usage

**Browser:** open the site, paste the tag, press *Speak*.

**curl (form):**

```bash
curl -X POST https://<your-app>.vercel.app/ -d "tag=6571e95b"
```

**curl (JSON):**

```bash
curl -X POST https://<your-app>.vercel.app/ \
  -H "Content-Type: application/json" \
  -d '{"tag": "6571e95b"}'
```

**Query string:** `https://<your-app>.vercel.app/?tag=6571e95b&json`

### Responses

| Case | Browser | JSON |
|------|---------|------|
| Correct tag | page shows the flag | `200 {"result":"AWAKE","flag":"GDG{...}"}` |
| Wrong tag   | "Tiamut sleeps on." | `403 {"result":"DORMANT"}` |

Input is trimmed and case-insensitive, and an optional `0x` prefix is accepted.
Tags are compared in constant time.

## Run locally

```bash
cd tiamut_vercel
python3 test_local.py          # starts a local server and runs the checks
```

or, with Vercel's dev server:

```bash
vercel dev
```

## Notes

- There is no rate limiting. The tag is 8 hex digits (about 4 billion possibilities), so guessing is impractical, but add a limit (for example Vercel's firewall rules) if you expect abuse.
- The tag is only secret because players don't have it until they solve the challenge. Anyone who runs `./tiamut` with the correct four words will see it.
- Update `CHALLENGE.txt` in the player files to point at this site's URL. It currently references the older word-checking server.
