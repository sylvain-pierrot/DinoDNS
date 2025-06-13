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
dinodns Dinofile.toml
```

### Run in development mode

To run the server directly from the source:

```bash
uv run -m dinodns.main Dinofile.toml
```

You can then test with:

```bash
nslookup jurassic.org. 127.0.0.1
```

---

## Dinofile Example

```toml
[[zones]]
zone = "."
forward = ["1.1.1.1"]

[[zones]]
zone = "jurassic.org"
origin = "jurassic.org."
ttl = 3600
records = [
  { name = "www", type = "A", value = "192.168.1.1" },
  { name = "mail", type = "MX", value = "mail.jurassic.org." },
  { name = "ftp", type = "CNAME", value = "www.jurassic.org." },
  { name = "ns", type = "NS", value = "ns1.jurassic.org." }
]
```
