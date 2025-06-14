<h1 align="center">DinoDNS</h1>

<p align="center">
    <em>Lightweight DNS Server. Built to Resolve, Ready to Forward.</em>
</p>
<p align="center">
    <img src="https://img.shields.io/badge/-TOML-brown" />
    <img src="https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/Made_with_%E2%9D%A4_by-Sylvain_Pierrot-blueviolet?style=flat-square" />
</p>
<p align="center">
    <img width="400" src="./assets/dinosaurs-hadrosaurid.png" alt="Dinosaur mascot" />
</p>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
  - [Why DinoDNS?](#why-dinodns)
- [Getting started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Testing](#testing)
- [`Catalog.toml` Example](#catalogtoml-example)

## Overview

**DinoDNS** is a lightweight, developer-friendly DNS server designed for custom domain resolution, dynamic record handling, and log-friendly observability.

### Why DinoDNS?

DinoDNS was built to offer a DNS server that’s:

- 🧩 **Configurable Zones**: Define DNS zones and records effortlessly using simple TOML files.
- ⚙️ **DNS Message Handling**: Parse, serialize, and respond to DNS queries with full protocol compliance.
- 📊 **Log-friendly**: Structured logs in `logfmt` format for easy integration with Promtail, Grafana, or any log pipeline.
- 🧪 **Ideal for local labs & testing**: No system-level DNS config required; just run and resolve.

---

## Getting started

### Prerequisites

This project requires the following dependencies:

- Python **≥ 3.13.3**
- [`uv`](https://github.com/astral-sh/uv) (recommended) or classic `pip`

### Installation

Using [`uv`](https://github.com/astral-sh/uv):

```bash
uv build --wheel
uv pip install dist/dinodns-*.whl
```

### Usage

Run the project with:

- After [Installation](#installation) section:

```bash
dinodns Catalog.toml
```

- Or, using [`uv`](https://github.com/astral-sh/uv):

```bash
uv run -m dinodns.main Catalog.toml
```

### Testing

Once DinoDNS is runnning, Run the following command:

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
