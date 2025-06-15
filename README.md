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
    <img width="500" src="./assets/dinosaurs-hadrosaurid.png" alt="Dinosaur mascot" />
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
  - [Query Examples](#query-examples)
    - [**A** Record Query:](#a-record-query)
    - [**CNAME** Record Query:](#cname-record-query)
    - [**NS** Record Query:](#ns-record-query)
- [`Catalog.toml` Example](#catalogtoml-example)

## Overview

**DinoDNS** is a lightweight, developer-friendly DNS server designed for custom domain resolution, dynamic record handling, and log-friendly observability.

> Based on the specifications defined in [RFC 1035 – Domain Names: Implementation and Specification](https://www.rfc-editor.org/rfc/rfc1035).

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

### Query Examples

You can interact with DinoDNS using _standard_ DNS tools like `nslookup`:

#### **A** Record Query:

```bash
nslookup jurassic.org. 127.0.0.1
```

Output:

```
Server:         127.0.0.1
Address:        127.0.0.1#53

Name:   jurassic.org
Address: 192.168.1.1
```

#### **CNAME** Record Query:

```bash
nslookup -type=CNAME jurassic.org. 127.0.0.1
```

Output:

```
Server:         127.0.0.1
Address:        127.0.0.1#53

jurassic.org    canonical name = www.jurassic.org.
```

#### **NS** Record Query:

```bash
dig NS jurassic.org. @127.0.0.1 +noadflag
```

> The Z field defined in [RFC 1035](https://www.rfc-editor.org/rfc/pdfrfc/rfc1035.txt.pdf) was later redefined by [RFC 2535](https://www.rfc-editor.org/rfc/rfc2535.html) introducing "DNS Security Extensions". The original 3 reserved bits are now interpreted as Z, AD (Authenticated Data), and CD (Checking Disabled).
> By default, dig sets the AD bit to 1, which results in a `Z=2` value if interpreted using the original RFC 1035 format. This causes compatibility issues with strict implementations like DinoDNS, which expect `Z=0`.
> To remain compliant with RFC 1035, disable the AD bit using the `+noadflag` option.

Output:

```
; <<>> DiG 9.10.6 <<>> NS jurassic.org. @127.0.0.1 +noadflag
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 53094
;; flags: qr aa rd; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1
;; WARNING: recursion requested but not available

;; QUESTION SECTION:
;jurassic.org.                  IN      NS

;; ANSWER SECTION:
jurassic.org.           3600    IN      NS      ns1.jurassic.org.

;; ADDITIONAL SECTION:
jurassic.org.           3600    IN      A       192.168.1.1

;; Query time: 0 msec
;; SERVER: 127.0.0.1#53(127.0.0.1)
;; WHEN: Mon Jun 16 01:18:13 CEST 2025
;; MSG SIZE  rcvd: 100
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
type = "NS"
nsdname = "ns1.jurassic.org."

[[zones.records]]
domain-name = "ns1"
ttl = 3600
class = "IN"
type = "A"
host-address = "192.168.1.1"

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
type = "NS"
nsdname = "ns1.cretaceous.org."

[[zones.records]]
domain-name = "@"
ttl = 3600
class = "IN"
type = "A"
host-address = "127.0.0.1"

[[zones.records]]
domain-name = "ns1"
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
