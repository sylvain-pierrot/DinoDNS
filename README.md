# DinoDNS

<div align="center">
    <img src="./assets/dinosaurs-hadrosaurid.png" alt="dinosaurs-hadrosaurid" />
</div>

DinoDNS is a minimalist and fun DNS server for dinosaurs 🦕. It allows you to define your own DNS zones using TOML configuration file.

---

## Requirements

- Python **≥ 3.13.3**
- [`uv`](https://github.com/astral-sh/uv) (recommended) or classic `pip`

## Getting started

### Installation

Build the package as a wheel:

```bash
uv build --wheel
```

Install it locally:

```bash
uv pip install dist/dinodns-*.whl
```

Then run the server:

```bash
dinodns Catalog.toml
```

### Run in development mode

To run the server directly from the source:

```bash
uv run -m dinodns.main Catalog.toml
```

You can then test with:

```bash
nslookup jurassic.org. 127.0.0.1
```

---

## `Catalog.toml` Example

```toml
[[zones]]
origin = "jurassic.org."

[[zones.records]]
domain-name = "@"
ttl = 3600
class = "IN"
type = "A"
host-address = "192.168.1.1"

[[zones.records]]
domain-name = "@"
ttl = 3600
class = "IN"
type = "CNAME"
cname = "www.jurassic.org."

[[zones]]
origin = "cretaceous.org."

[[zones.records]]
domain-name = "@"
ttl = 3600
class = "IN"
type = "A"
host-address = "127.0.0.1"

[[zones.records]]
domain-name = "@"
ttl = 3600
class = "IN"
type = "CNAME"
cname = "www.cretaceous.org."
```
