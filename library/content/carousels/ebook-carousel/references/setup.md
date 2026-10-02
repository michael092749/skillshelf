# First-run setup and portability

The entire installed skill directory is self-contained documentation and Python
helpers. The host supplies live tools; cloning or installing this directory does
not install Exa, Metricool, image generation, a wiki or reference images.

## Required inputs

Use the user's prompt and existing project docs first. Resolve the publisher's
catalogue URL, allowed merchant hostnames, audience/language, topic priorities and
brand/style direction before selecting an idea. Ask one concise question if the
publisher or audience cannot be inferred. A public catalogue is evidence of an
offer, not proof that the user owns its brand or assets; use only authorized
branding/reference images. No particular publisher or social account is assumed.

For a new workspace, after the brief is known, create only the working files this
production needs: README.md with folder map, content-tracker.csv with columns
`id,title,format,platforms,status,project_path,next_action`, brand/style-guide.md
with the agreed brief, research/README.md, and the numbered carousels/ project.
Read any existing workspace instructions first. Missing publication logs mean
history is unknown; do not create fictional posts. A wiki and reference character
are optional. Preserve existing numbering and conventions when provided.

Record allowed merchant hostnames in run.json `merchant_hosts`; both product and
CTA URLs must use HTTPS on those hosts. Record the actual brand, audience and
palette used. The example `publisher.example` in artifacts.md is a schema example,
not a real verified offer. Include checkout hosts only if relevant and verified;
this workflow never buys products or tests a payment.

## Tool capabilities

| Capability | Needed for | If absent |
| --- | --- | --- |
| Live Exa MCP search/fetch | Required research stage | Save draft and identify missing connection |
| Built-in GPT Image and image viewer | Required creative generation and visual inspection | Save draft; do not silently substitute a paid API |
| Local filesystem and Python | Persist artifacts and validate | Identify limitation; do not claim files exist |
| Pillow | Export normalization and JPEG inspection | Install requirements in a project tooling venv |
| Metricool MCP and configured accounts | Optional account analytics | Record unavailable and continue cold-start |
| Subagent tools | Parallel specialist work | Execute roles sequentially and disclose |
| Existing wiki/query skill | Optional historical evidence | Use ordinary project research |

Discover tool names/schemas at runtime. If the host includes imagegen instructions,
read them; otherwise this bundle's visuals.md supplies the prompt and inspection
contract, subject to the live image tool's own instructions. Built-in image access
is a host capability, not a Python package or API key bundled here. A Claude-only
host may install the skill but cannot complete generation unless a compatible
explicitly authorized image capability is supplied.

Exa can be configured using the catalog's integrations/exa recipe and MCP
installer if not already connected. Verify tools with a read-only request. Keep
credentials in environment variables or the host's secret store. Metricool has no
bundled server recipe here; use an existing trusted connection or the documented
cold-start branch. Do not guess endpoint URLs or save account credentials.

## Python environment

Requires Python 3.11+ and Pillow. From the installed skill's actual directory:

```bash
python3.11 -m venv /path/to/project/.venv-carousel
/path/to/project/.venv-carousel/bin/python -m pip install -r /path/to/ebook-carousel/requirements.txt
/path/to/project/.venv-carousel/bin/python -m unittest discover -s /path/to/ebook-carousel/scripts -p 'test_*.py'
```

Use an existing compatible environment when available. If venv/pip is missing,
report the missing prerequisite or use an available environment manager. Generation
is never needed for these tests. Run normalize_slides.py --help for the export CLI.

## Scope and origin

This is the portable edition of a project-authored carousel workflow. It retains
the parallel handoffs, low-view triage, exact export sizing, image reviews and
flowchart, while replacing private workspace paths/account defaults with supplied
inputs. Import hashes are in import-provenance.json. No production research,
account metrics, character art, credentials or generated slides are bundled.
