# AWS Route 53 & DNS — Complete Case Study Documentation

> **Complete Case Study** — DNS Fundamentals · Route 53 · Routing Policies · Practical Tasks

---

## Table of Contents

1. [How the Internet Finds Your Website](#how-the-internet-finds-your-website)
2. [Introduction to DNS](#introduction-to-dns)
3. [DNS Service Providers](#dns-service-providers)
4. [AWS Route 53](#aws-route-53)
5. [Route 53 Core Components](#route-53-core-components)
6. [DNS Record Types](#dns-record-types)
7. [Alias Records](#alias-records)
8. [Route 53 Routing Policies](#route-53-routing-policies)
9. [Route 53 Health Checks](#route-53-health-checks)
10. [TASKS — Hands-On Route 53 Labs](#tasks--hands-on-route-53-labs)
11. [Key Takeaways](#key-takeaways)

---

# How the Internet Finds Your Website

Every time you type a website address into a browser, a complex chain of lookups happens invisibly within milliseconds. Understanding this chain — DNS — is the foundation for everything Route 53 does.

## What Happens When a Client Hits a Domain

When you type `www.example.com` and press Enter, your device does not know the IP address of that server. It needs to ask. The Domain Name System (DNS) is the global distributed database that maps human-readable names to machine-readable IP addresses. Here is the full journey step by step:

**ARCHITECTURE — Full DNS Resolution Flow**

```text
Client Browser
      │
      │ 1. Check Browser Cache
      │    (is example.com already cached? TTL still valid?)
      │
      │ 2. Check OS / hosts file
      │    (/etc/hosts, Windows hosts file)
      │
      ▼
Recursive Resolver  ←──── (ISP DNS / 8.8.8.8 / 1.1.1.1)
      │
      │ 3. Check Resolver Cache
      │    (has it resolved this recently?)
      │
      │ 4. Ask Root DNS Server
      │    "Who handles .com?"
      ▼
Root DNS Server  (13 root server clusters worldwide)
      │
      │ "Go ask the .com TLD server"
      │ Returns address of .com TLD nameserver
      ▼
TLD DNS Server  (.com / .org / .net / .io etc.)
      │
      │ "Go ask the Authoritative NS for example.com"
      │ Returns the Authoritative Name Server records
      ▼
Authoritative Name Server  (Route 53 / Cloudflare / etc.)
      │
      │ "www.example.com → 54.12.34.56"
      │ Returns the actual A Record / IP address
      ▼
Recursive Resolver  (caches result for TTL duration)
      │
      ▼
Client Browser
      │
      │ 5. TCP/TLS connection established to 54.12.34.56
      │ 6. HTTP request sent
      ▼
Web Server  →  Response  →  Page loads

Result also cached in: Browser Cache + OS Cache + Resolver Cache (based on TTL)
```

### What is a Nameserver?

A **nameserver** is a server that stores DNS records and answers DNS queries. When you register a domain and create a hosted zone, Route 53 assigns you 4 nameservers. These are the servers that the rest of the internet will ask when looking up your domain.

Nameservers form a hierarchy: **Root Nameservers** → **TLD Nameservers** → **Authoritative Nameservers**. Each layer delegates responsibility to the next layer until the actual record is found.

**ARCHITECTURE — Nameserver Hierarchy**

```text
ROOT SERVERS  (.)  ← 13 globally distributed clusters, managed by ICANN
     │
     ├── .com  TLD Servers  (managed by Verisign)
     │      │
     │      └── example.com  Authoritative NS  (managed by Route 53)
     │               │
     │               ├── www.example.com  →  54.12.34.56   (A Record)
     │               ├── api.example.com  →  54.12.34.99   (A Record)
     │               └── mail.example.com →  mail.google   (MX Record)
     │
     ├── .org  TLD Servers
     ├── .net  TLD Servers
     └── .io   TLD Servers
```

### DNS Delegation — How Your Domain Points to Route 53

When you buy a domain from GoDaddy or Namecheap, their nameservers are used by default. To use Route 53 as your DNS provider, you delegate authority by updating the nameservers at your registrar to point to Route 53's nameservers.

**ARCHITECTURE — DNS Delegation Flow**

```text
Domain Registrar (GoDaddy / Namecheap)
     │
     │  You update NS records here to point to Route 53
     ▼
Route 53 Nameservers
     ns-123.awsdns-45.com
     ns-678.awsdns-12.net
     ns-901.awsdns-34.org
     ns-234.awsdns-56.co.uk
     │
     │  Route 53 now answers all DNS queries for your domain
     ▼
DNS Queries from the internet → Route 53 Hosted Zone → DNS Records → IP Address
```

---

# Introduction to DNS

## What is DNS?

DNS (Domain Name System) translates human-friendly domain names into machine-readable IP addresses.

Example:

```text
www.google.com  →  172.217.18.36
```

DNS acts like the **internet's phone book**, allowing users to access websites using names instead of remembering IP addresses.

## Why DNS is Important

Without DNS, users would need to remember IP addresses for every website.

DNS provides:

- Easy-to-remember website names
- Stable access even if server IPs change
- Scalability for millions of websites
- Load distribution through multiple A records (Round Robin DNS)
- Security and spam protection through TXT / SPF / DKIM records

## DNS Hierarchy

DNS uses a hierarchical naming structure:

```text
.
└── .com
    └── example.com
        ├── www.example.com
        └── api.example.com
```

## How DNS Resolution Works

### DNS Resolution Steps

When you enter `www.example.com` in a browser:

1. **Browser Cache Check** — Browser checks if the domain IP is already cached locally.
2. **OS Cache Check** — Operating system checks its DNS cache (and the local hosts file).
3. **Query Recursive Resolver** — Device sends the request to a recursive resolver (ISP, Google DNS `8.8.8.8`, Cloudflare `1.1.1.1`).
4. **Root DNS Server** — Resolver asks the Root Server for `.com` information. Root Server points to the `.com` TLD server.
5. **TLD DNS Server** — Resolver asks the TLD server for `example.com`. TLD server returns the Authoritative Name Server.
6. **Authoritative Name Server** — Returns the actual IP address of `www.example.com`.
7. **Browser Connects to Server** — Browser receives the IP and loads the website.
8. **Caching** — The result is cached for future requests based on TTL.

### Key DNS Components

| Component | Purpose |
| --- | --- |
| **Recursive Resolver** | Performs the full DNS lookup on behalf of the client. Caches results. |
| **Root Server** | Directs requests to TLD servers. 13 root server clusters worldwide. |
| **TLD Server** | Handles domains like .com, .org, .net. Knows which NS is authoritative. |
| **Authoritative Server** | Stores the actual DNS records for a domain. Final answer source. |
| **DNS Cache** | Speeds up future lookups by storing recent results based on TTL. |

### Important DNS Terms

| Term | Description |
| --- | --- |
| **Domain Name** | Human-readable website name (e.g. example.com) |
| **IP Address** | Numerical server address (e.g. 54.12.34.56 for IPv4) |
| **TTL** | Time To Live — how long DNS records stay cached before re-querying |
| **FQDN** | Fully Qualified Domain Name — complete domain name (www.example.com.) |
| **TLD** | Top-Level Domain — the last segment of a domain name (.com, .org, .io) |
| **Zone File** | Text file containing all DNS records for a hosted zone |
| **Propagation** | The time it takes for DNS changes to spread across global servers |
| **Delegation** | Assigning DNS authority for a subdomain to a different nameserver |

---

# DNS Service Providers

## Popular DNS Providers

| Provider | Type | Features |
| --- | --- | --- |
| **GoDaddy** | Registrar + DNS Hosting | Beginner-friendly, popular domain provider |
| **Namecheap** | Registrar + DNS Hosting | Affordable pricing, free Whois privacy |
| **Cloudflare** | DNS Hosting + CDN | Fast DNS, DDoS protection, free tier, proxy mode |
| **AWS Route 53** | Registrar + DNS Hosting | AWS integration, advanced routing policies, health checks |
| **Google Cloud DNS** | DNS Hosting | Low latency, global anycast network |

## Domain Registrar vs DNS Hosting

### Domain Registrar

Lets you purchase and own a domain name and maintains domain ownership records.

Examples:

- GoDaddy
- Namecheap
- Route 53

### DNS Hosting Provider

Hosts DNS records for your domain and responds to DNS queries from the internet.

Examples:

- Cloudflare
- Route 53
- Google Cloud DNS

### Simple Analogy

- **Domain Registrar** → Registers your house address with the city
- **DNS Hosting Provider** → Delivers mail to your house once the address is known

You can buy a domain from **GoDaddy** and use **Route 53** or **Cloudflare** for DNS hosting. The registrar and the DNS host do not have to be the same company — you simply point your registrar's NS records to whichever DNS host you prefer.

---

# AWS Route 53

## What is Route 53?

Amazon Route 53 is a **highly available, scalable, fully managed, and authoritative DNS service** provided by AWS.

> Authoritative DNS means you can directly manage and update DNS records for your domain. Route 53's answer is the final, definitive answer — it is not a cached or forwarded response.

Route 53 also acts as:

- A **Domain Registrar** — purchase and manage domains directly through AWS
- A **DNS Routing Service** — routes traffic using intelligent policies
- A **Health Checking Service** — monitors endpoints and reroutes on failure

## Main Features

| Feature | Description |
| --- | --- |
| **Domain Registration** | Purchase and manage domains through AWS. Integrates instantly with hosted zones. |
| **DNS Routing** | Routes traffic to resources like EC2, S3, ALB, CloudFront, API Gateway |
| **Health Checks** | Monitors endpoints and routes traffic only to healthy resources |
| **High Availability** | AWS provides a 100% availability SLA — the only AWS service with a full uptime guarantee |
| **Traffic Flow** | Visual editor for complex multi-policy routing configurations |
| **DNSSEC** | DNS Security Extensions — protects against spoofing and cache poisoning attacks |
| **Private DNS** | Internal DNS resolution within VPCs without exposing records to the public internet |

## Why is it Called Route 53?

The name has two meanings:

- **Route** → Routes internet/DNS traffic to the correct destination
- **53** → DNS uses **port 53** for queries and responses

Port reference:

```text
HTTP  → Port 80
HTTPS → Port 443
DNS   → Port 53   ← Route 53 is named after this
```

---

# Route 53 Core Components

## Hosted Zones

A **Hosted Zone** is a container for DNS records of a domain. It is the equivalent of a DNS zone file — it holds all the records that define how traffic is routed for that domain and its subdomains.

Example hosted zones:

- `example.com`
- `api.example.com` (subdomain delegation)

Route 53 automatically creates two records in every new hosted zone:

- **NS Record** → Route 53 name servers assigned to your zone
- **SOA Record** → Administrative metadata about the zone

### Public Hosted Zone

Used for routing traffic from the **public internet**. DNS records in a public hosted zone are visible to and resolvable by anyone on the internet.

**ARCHITECTURE — Public Hosted Zone**

```text
Internet User
      │
      ▼
Public DNS Query  →  Route 53 Public Hosted Zone (example.com)
      │
      ├── www.example.com  →  ALB DNS name  (Alias Record)
      ├── api.example.com  →  EC2 IP  (A Record)
      └── mail.example.com →  mail server  (MX Record)
```

### Private Hosted Zone

Used for routing traffic **inside VPCs only**. Records in a private hosted zone are only resolvable from EC2 instances and services running inside the associated VPC. They are completely invisible from the public internet.

**ARCHITECTURE — Private Hosted Zone**

```text
VPC  (10.0.0.0/16)
      │
      │  Internal DNS query from EC2 App Server
      ▼
Route 53 Private Hosted Zone (internal.example.com)
      │
      ├── db.internal.example.com  →  10.0.1.50  (RDS Private IP)
      ├── cache.internal.example.com → 10.0.1.60  (ElastiCache)
      └── app.internal.example.com  → 10.0.2.10  (Internal ALB)

NOTE: These records are NOT visible from the public internet
```

> Public zones work on the internet. Private zones work only inside AWS VPCs.

## Name Servers (NS)

Name Servers host DNS records and answer DNS queries. Route 53 assigns 4 name servers to each hosted zone for redundancy and global availability.

```text
ns-123.awsdns-45.com
ns-678.awsdns-12.net
ns-901.awsdns-34.org
ns-234.awsdns-56.co.uk
```

AWS uses **anycast routing** for its nameservers, meaning queries are automatically answered by the geographically nearest Route 53 infrastructure for lowest latency.

## DNS Delegation

To use Route 53 DNS for a domain purchased elsewhere:

1. Buy domain from registrar (GoDaddy, Namecheap)
2. Create Hosted Zone in Route 53
3. Copy the 4 Route 53 NS records
4. Update nameservers at your registrar to the Route 53 NS values

```text
GoDaddy Domain
      │
      ▼
Update Nameservers → Route 53 NS Records
      │
      ▼
Route 53 Name Servers  (all DNS queries now handled by Route 53)
      │
      ▼
Route 53 Hosted Zone  →  Returns correct record  →  Client gets IP
```

## SOA Record

SOA = **Start of Authority**. Contains administrative details about the hosted zone. The SOA record specifies:

- **Primary Name Server** — the main authoritative NS for the zone
- **Administrator Contact** — the email of the zone administrator
- **Serial Number** — the version number of the zone (increments on each change)
- **Refresh Interval** — how often secondary NS servers check for zone updates
- **Retry Interval** — how long secondary NS waits before retrying a failed refresh
- **Expire Duration** — how long secondary NS will serve stale data if primary is unreachable
- **Default TTL** — the default Time To Live used for DNS caching

> The SOA record is usually managed automatically by Route 53.

## TTL (Time To Live)

TTL defines how long DNS records stay cached in resolvers and browsers before they must re-query the authoritative nameserver.

| TTL Type | Effect | When to Use |
| --- | --- | --- |
| **High TTL** (e.g. 86400 = 24 hr) | Less DNS traffic, slower propagation of changes | Stable production records |
| **Low TTL** (e.g. 60 sec) | Faster updates, more DNS queries, higher cost | Before migrations, during failover testing |
| **Zero TTL** | No caching — always queries authoritative NS | Rapid change scenarios (not recommended long-term) |

> Alias records do not allow manual TTL configuration — AWS manages TTL automatically.

---

# DNS Record Types

```text
A Record       → Domain    → IPv4 Address
AAAA Record    → Domain    → IPv6 Address
CNAME          → Domain    → Another Domain
MX Record      → Domain    → Mail Server
TXT Record     → Text Metadata / Domain Verification / Email Security
NS Record      → Authoritative Name Servers
PTR Record     → IP Address → Domain  (Reverse DNS)
SRV Record     → Service Host + Port
SOA Record     → Zone administrative information
Alias Record   → Domain    → AWS Resource  (Route 53 specific)
```

## A Record

Maps a domain name to an **IPv4 address**. The most common DNS record type.

```text
example.com  →  54.12.34.56
```

You can have multiple A records for the same domain pointing to different IPs. DNS resolvers will return all IPs and clients typically use round-robin to pick one.

## AAAA Record

Maps a domain name to an **IPv6 address**.

```text
example.com  →  2001:db8::1
```

As IPv6 adoption grows, AAAA records are increasingly important. Many modern applications configure both A and AAAA records for dual-stack support.

## CNAME Record

Maps one domain name to **another domain name** (not directly to an IP).

```text
www.example.com  →  example.com
```

| Feature | Details |
| --- | --- |
| **Limitation** | Cannot be used for the root/apex domain (example.com) — only subdomains |
| **Resolution** | Resolver follows the chain until an A/AAAA record is found |
| **Common Use** | Subdomains like www.example.com, blog.example.com, shop.example.com |
| **Chaining** | CNAME can point to another CNAME, but avoid deep chains (latency) |

## MX Record

Defines **mail servers** for a domain. MX records have a priority value — lower number = higher priority.

```text
example.com  →  Priority 1  →  aspmx.l.google.com
example.com  →  Priority 5  →  alt1.aspmx.l.google.com
```

> When someone sends an email to user@example.com, the MX record tells the internet which mail server should receive that email.

## TXT Record

Stores **text-based information** for a domain. Used for:

- **Domain Verification** — proves domain ownership to Google Workspace, Microsoft 365, etc.
- **SPF (Sender Policy Framework)** — specifies which mail servers can send on behalf of your domain
- **DKIM (DomainKeys Identified Mail)** — cryptographic email signature verification
- **DMARC** — policy for handling emails that fail SPF or DKIM checks

```text
# SPF Record — allow Google mail servers
v=spf1 include:_spf.google.com ~all

# Domain verification example
google-site-verification=abc123def456
```

## NS Record

Defines the **authoritative name servers** for a domain or subdomain. Automatically created by Route 53 when you create a hosted zone. NS records can also be used for subdomain delegation — pointing a subdomain to a completely different set of nameservers.

## PTR Record

Used for **reverse DNS lookup** — mapping an IP address back to its associated domain name. Commonly used in email server verification (to prove a mail server's IP belongs to the claimed domain), logging, and network troubleshooting.

```text
54.12.34.56  →  example.com
```

PTR records live in special zones under `.in-addr.arpa` (IPv4) or `.ip6.arpa` (IPv6). For AWS resources, you need to contact AWS support or use your ISP to set PTR records.

## SRV Record

Defines the **hostname and port number** for specific services, helping clients automatically discover where a service is running without hard-coding addresses.

Commonly used in:

- VoIP (Voice over IP) services
- SIP (Session Initiation Protocol)
- XMPP (Extensible Messaging)
- Gaming services
- Microsoft Teams / Skype for Business

```text
_sip._tcp.example.com  10  60  5060  sip.example.com
    │         │    │    │     └─ Target host
    │         │    │    └───── Port number
    │         │    └────────── Weight
    │         └─────────────── Priority
    └───────────────────────── Service.Protocol
```

---

# Alias Records

Alias records are a **Route 53 extension** to standard DNS. They map domain names directly to AWS resources and solve a key limitation of CNAME records — they work at the apex/root domain.

Alias records can target:

- Load Balancers (ALB, NLB, CLB)
- CloudFront distributions
- API Gateway endpoints
- S3 Static Websites
- Global Accelerator
- Another Route 53 record in the same hosted zone

Features:

- Works at root domain (`example.com`) — unlike CNAME
- Automatically tracks AWS IP changes — no manual updates needed
- No extra DNS query — resolved internally in one step
- Free of charge for queries targeting AWS resources
- Native health check support

```text
example.com  →  my-alb-1234567890.us-east-1.elb.amazonaws.com  (Alias)
```

## CNAME vs Alias Comparison

| Feature | CNAME | Alias |
| --- | --- | --- |
| Root Domain Support | No — subdomains only | Yes — works at apex |
| AWS Native Integration | Partial | Full native integration |
| Extra DNS Lookup | Yes — adds latency | No — resolved internally |
| Automatic AWS IP Updates | No — manual updates needed | Yes — automatic |
| Cost for AWS Targets | Standard query charges | Free for AWS targets |
| TTL Control | Manual | Managed by AWS automatically |
| Health Check Support | Limited | Full support |

---

# Route 53 Routing Policies

> Routing Policies define how Route 53 responds to DNS queries. DNS itself does NOT route traffic like a Load Balancer — it only decides which IP or resource name to return in the DNS response. The client then connects directly to that resource.

## Routing Policies Overview

| Policy | Routes Based On | Health Checks | Common Use |
| --- | --- | --- | --- |
| **Simple** | Single resource | Limited | Basic single-server websites |
| **Weighted** | Assigned weights | Yes | A/B testing, gradual rollout |
| **Latency** | Lowest network latency | Yes | Global low-latency applications |
| **Failover** | Primary / Secondary health | Required | Disaster recovery |
| **Geolocation** | User country / continent | Yes | Localization & compliance |
| **Geoproximity** | Geography + configurable bias | Yes | Fine-grained traffic shaping |
| **Multi-Value** | Multiple healthy IPs | Yes | Basic load distribution |
| **IP-Based** | Client IP / CIDR range | Yes | ISP or network-based routing |

## Simple Routing

Returns a single resource for a domain. The simplest routing policy.

```text
example.com  →  54.12.34.56
```

**ARCHITECTURE — Simple Routing**

```text
User → DNS Query → Route 53 → Returns 54.12.34.56 → User connects to EC2

If multiple IPs configured:
Route 53 returns ALL IPs → Browser picks one randomly (round-robin)
```

Features:

- Simplest routing policy
- Can return multiple IPs — browser chooses randomly
- No health-check based failover
- Best for small or simple single-server applications

Use Case: Personal blog hosted on one EC2 instance

## Weighted Routing

Splits traffic between multiple resources using assigned weights.

```text
Server A → Weight 80   →  80% of traffic
Server B → Weight 20   →  20% of traffic
```

**ARCHITECTURE — Weighted Routing**

```text
User Request
     │
     ▼
Route 53 Weighted Policy
     │
     ├── 80% ──→ Server A (Production v1)
     │               IP: 54.12.34.56
     │
     └── 20% ──→ Server B (New v2 being tested)
                     IP: 54.12.34.99
```

Features:

- Supports gradual deployments and A/B testing
- Blue-Green deployments — shift traffic incrementally
- Weight range: `0–255`
- Weight `0` stops traffic to a resource without deleting the record
- If all weights are `0`, traffic is distributed equally among all records

Use Case: Testing a new application version with a limited percentage of users

## Latency Routing

Routes users to the AWS region with the **lowest network latency**. This is measured between the end user's network and the AWS region — not purely geographic distance.

```text
India User  → Mumbai Region    (ap-south-1)   ← lowest latency path
US User     → Virginia Region  (us-east-1)
EU User     → Ireland Region   (eu-west-1)
```

**ARCHITECTURE — Latency Routing**

```text
User in India
     │
     ▼
Route 53 Latency Check
     │
     ├── ap-south-1  (Mumbai)   ← 18ms   ← WINNER
     ├── us-east-1   (Virginia) ← 210ms
     └── eu-west-1   (Ireland)  ← 120ms
     │
     ▼
User directed to Mumbai EC2 / ALB
```

Features:

- Optimizes global application performance
- Based on actual latency measurements, not geographic proximity
- Can integrate with health checks

> Germany users may be directed to US-East if that region has lower latency than EU regions.

Use Case: Global applications requiring fast response times for users worldwide

## Failover Routing

Routes traffic to a **primary resource** and automatically switches to a **secondary backup** if the primary becomes unhealthy. Requires health checks.

**ARCHITECTURE — Failover Routing**

```text
Normal State:
User → Route 53 → Primary Server (54.12.34.56) ← Active, Healthy
                   Secondary Server (54.99.88.77)  ← Standby

Failover State (Primary unhealthy):
User → Route 53 → Primary Server (54.12.34.56) ← UNHEALTHY ✗
               └─→ Secondary Server (54.99.88.77) ← NOW ACTIVE ✓

Route 53 Health Checker detects failure within ~30 seconds
DNS TTL determines how quickly clients switch over
```

Features:

- Requires health checks on the primary record
- Automatic disaster recovery — no manual intervention
- Active-Passive setup (primary serves all traffic normally)
- Secondary can be in a different region for maximum resilience

Use Case: High availability applications with backup disaster recovery regions

## Geolocation Routing

Routes traffic based on the **geographic location** of the user, determined by their IP address. Unlike Latency Routing, this is purely location-based regardless of speed.

Supported levels:

- Continent (e.g. Europe, Asia, North America)
- Country (e.g. Germany, India, United States)
- US State (granular US-only routing)

```text
Germany Users → German Server  (GDPR compliance)
India Users   → India Server   (local language, pricing)
Default       → Global Server  (catches all other countries)
```

**ARCHITECTURE — Geolocation Routing**

```text
Route 53
     │
     ├── Country: DE (Germany)  ──→ eu-central-1 (Frankfurt)
     ├── Country: IN (India)    ──→ ap-south-1 (Mumbai)
     ├── Country: US (United States) ──→ us-east-1 (N. Virginia)
     └── Default Record         ──→ us-east-1 (catches everyone else)

IMPORTANT: Always configure a Default record.
Without it, users from unlisted countries get NXDOMAIN (no DNS response).
```

Features:

- Supports localization (language, currency, pricing)
- Useful for legal and compliance requirements (GDPR, data residency)
- Default record strongly recommended to handle unlisted locations

Use Case: Region-specific pricing, language, or media content restrictions

## Geoproximity Routing

Routes traffic based on user location AND resource location, with a configurable **bias** that expands or shrinks the geographic region served by each resource. Requires **Route 53 Traffic Flow**.

Bias values:

- `+1 to +99` → Expands the effective traffic region (attracts more users)
- `-1 to -99` → Shrinks the effective traffic region (repels users to other endpoints)

```text
US-East Bias +50  →  Receives traffic from a larger geographic area than normal
```

**ARCHITECTURE — Geoproximity Routing with Bias**

```text
Without Bias:
US Users  → US-East
EU Users  → EU-West
(split at geographic midpoint)

With US-East Bias +50:
US Users  → US-East
Most EU Users → US-East  ← bias expands the US-East coverage area
Far EU Users  → EU-West

Useful when one region has more capacity or lower cost
```

Use Case: Intentionally directing more users to a preferred or higher-capacity region

## Multi-Value Routing

Returns **multiple healthy IP addresses** for a single DNS query. The client receives up to 8 healthy IPs and picks one — providing basic client-side load distribution.

```text
Healthy:
54.12.34.56  ✓
54.12.34.99  ✓
54.12.34.11  ✓

Unhealthy:
54.12.34.22  ✗  ← Route 53 will NOT return this IP
```

**ARCHITECTURE — Multi-Value Routing**

```text
Route 53 Multi-Value Query Response:
[
  54.12.34.56,  ← healthy
  54.12.34.99,  ← healthy
  54.12.34.11,  ← healthy
  54.12.34.22   ← EXCLUDED (unhealthy)
]

Client picks one IP randomly and connects directly

NOTE: Multi-Value is NOT a replacement for an Elastic Load Balancer.
ELB handles connection-level load balancing, health checks, SSL termination.
Multi-Value only controls which IPs the DNS response includes.
```

Features:

- Returns up to 8 healthy records per query
- Supports health checks — automatically excludes unhealthy endpoints
- Basic client-side load distribution
- Not a replacement for ELB — DNS does not balance existing connections

Use Case: Multiple EC2 instances serving the same application with basic redundancy

## IP-Based Routing

Routes traffic based on the **client's IP address or CIDR range**. You define CIDR blocks and map each block to a specific endpoint.

```text
203.0.113.0/24   →  Server A  (Corporate office network)
198.51.100.0/24  →  Server B  (ISP or branch office network)
Everything else  →  Default Server
```

**ARCHITECTURE — IP-Based Routing**

```text
Client IP: 203.0.113.50
     │
     ▼
Route 53 CIDR Block Lookup
     │
     │  203.0.113.50 matches 203.0.113.0/24
     ▼
Server A  (optimized endpoint for this network)
```

Features:

- ISP or network-specific routing for optimized performance
- CIDR-based IP-to-endpoint mapping
- Useful for enterprise branch office routing
- Can direct known bot or crawler IPs to specific handling

Use Case: Directing branch offices or specific ISP users to optimized endpoints

---

# Route 53 Health Checks

Route 53 Health Checks continuously monitor application endpoints and automatically stop routing traffic to unhealthy resources. They are the backbone of Route 53's high availability features.

> Think of Health Checks as an automated monitoring and failover system for your infrastructure. They run 24/7 from multiple AWS locations worldwide.

## Types of Health Checks

### 1. Endpoint Health Check

Monitors a specific IP address, domain, or URL using **HTTP, HTTPS, or TCP** protocols. Route 53 sends requests from health checker locations around the world and evaluates the response.

```text
https://example.com/health  →  Expected: HTTP 200 OK
```

You can also configure Route 53 to check for specific text in the response body.

### 2. Calculated Health Check

Combines multiple individual health checks into a single logical result using **AND, OR, or NOT** conditions. Useful for expressing complex health logic.

Example:

- Healthy only if **2 out of 3** child checks pass
- Unhealthy if ANY of 5 database checks fails
- Healthy only if BOTH the web tier AND the database tier are healthy

### 3. CloudWatch Alarm Health Check

Uses a **CloudWatch Alarm** state instead of directly checking an endpoint. The health check is considered healthy when the alarm is in OK state and unhealthy when the alarm is in ALARM state.

> Route 53 health checkers are public AWS infrastructure and cannot directly reach resources inside private VPCs. Use CloudWatch Alarm Health Checks for private resources by publishing custom metrics from your VPC to CloudWatch.

## Health Check Configuration

| Setting | Example | Notes |
| --- | --- | --- |
| **Protocol** | HTTPS | HTTP, HTTPS, or TCP |
| **Port** | 443 | Standard or custom port |
| **Path** | `/health` | Endpoint that returns 200 when healthy |
| **Check Interval** | 30 sec | 10 sec also available (higher cost) |
| **Failure Threshold** | 3 failed checks | Consecutive failures before marking unhealthy |
| **Success Threshold** | 1 success | Consecutive successes before marking healthy again |
| **Regions** | Multiple | Choose which AWS regions run health checks from |

## Key Health Check Behavior

- Around **15 global AWS health checkers** monitor endpoints continuously from different regions
- Only `2xx` and `3xx` HTTP responses are considered healthy
- Response time threshold: default 4 seconds for standard, 2 seconds for fast checks
- String matching: Route 53 can check the first 5,120 bytes of the response body
- CloudWatch integration: health check status is published as CloudWatch metrics
- SNS Notifications: trigger alerts via SNS when health status changes

## Health Check + Failover Flow

**ARCHITECTURE — Health Check Failover**

```text
Route 53 Health Checkers (15 global locations)
     │
     │  Every 30 seconds: GET https://example.com/health
     ▼
Primary Server  →  HTTP 200  →  HEALTHY ✓
     │
     │  [If primary returns errors 3 times in a row]
     ▼
Primary Server  →  Connection Timeout  →  UNHEALTHY ✗
     │
     │  Route 53 stops returning Primary IP
     ▼
Secondary Server  →  Route 53 now returns Secondary IP
     │
     │  Clients get Secondary IP on next DNS query
     ▼
Traffic automatically rerouted  →  Failover complete

When Primary recovers:
Route 53 detects healthy response → Resumes sending traffic to Primary
```

---

# TASKS — Hands-On Route 53 Labs

## Task 1 — Host a Website Using Simple Routing

### Objective

- Launch an EC2 instance
- Install a web server
- Configure a custom domain
- Point the domain to EC2 using Route 53
- Access the website publicly

### Architecture

**ARCHITECTURE — Simple Routing — Task 1**

```text
Internet User
     │
     ▼
www.yourdomain.com
     │
     ▼  (DNS Query)
Route 53 Hosted Zone
     │  A Record: yourdomain.com → 54.12.34.56
     ▼
EC2 Instance (Apache / Nginx)
IP: 54.12.34.56  |  Port: 80  |  Public Subnet
     │
     ▼
Response: Hello from AWS Route 53!
```

### Step 1 — Purchase a Domain

**GoDaddy / Namecheap:**

- Purchase a domain
- Route 53 will manage DNS after configuration

**Route 53 (directly):**

- Open AWS Console → Route 53
- Register Domain
- Hosted zone is created automatically after purchase

### Step 2 — Launch EC2 Instance

| Setting | Value |
| --- | --- |
| AMI | Amazon Linux 2023 |
| Instance Type | t2.micro |
| Public IP | Enabled |
| Security Group | Allow SSH (22) & HTTP (80) |

Launch steps:

- Open EC2 → Launch Instance
- Create or select key pair
- Launch instance
- Note the Public IP address

```text
Example Public IP: 54.12.34.56
```

### Step 3 — Install Apache2 Web Server (Ubuntu)

Connect to EC2:

```text
ssh -i your-key.pem ubuntu@54.12.34.56
```

Install Apache2:

```text
sudo apt update -y
sudo apt install apache2 -y

sudo systemctl start apache2
sudo systemctl enable apache2
```

Create sample webpage:

```text
sudo bash -c 'cat > /var/www/html/index.html << EOF
<h1>Hello from AWS Route 53!</h1>
EOF'
```

Verify in browser:

```text
http://54.12.34.56
```

### Step 4 — Create Route 53 Hosted Zone

- Open Route 53
- Hosted Zones → Create Hosted Zone

| Field | Value |
| --- | --- |
| Domain Name | yourdomain.com |
| Type | Public Hosted Zone |

Copy the 4 generated NS records. Example:

```text
ns-123.awsdns-45.com
ns-678.awsdns-12.net
ns-901.awsdns-34.org
ns-234.awsdns-56.co.uk
```

### Step 5 — Update Nameservers at Registrar

**GoDaddy:**

- My Products → DNS
- Nameservers → Change → Custom
- Paste the 4 Route 53 NS records

**Namecheap:**

- Domain List → Manage
- Nameservers → Custom DNS
- Paste the 4 Route 53 NS records

DNS propagation typically takes a few minutes to up to 48 hours.

### Step 6 — Create A Record in Route 53

- Route 53 → Hosted Zone → yourdomain.com
- Create Record

| Field | Value |
| --- | --- |
| Record Name | www (or leave blank for root) |
| Record Type | A |
| Routing Policy | Simple |
| Value | EC2 Public IP (54.12.34.56) |
| TTL | 300 |

### Step 7 — Validate DNS Resolution

```text
# Check DNS propagation
nslookup yourdomain.com
dig yourdomain.com

# Expected output
;; ANSWER SECTION:
yourdomain.com.  300  IN  A  54.12.34.56
```

Open in browser:

```text
http://yourdomain.com
```

---

## Routing Policies — Practice Tasks

### Weighted Routing

**Purpose:** Split traffic between servers for A/B testing or gradual deployments.

| Server | Weight | Traffic % |
| --- | --- | --- |
| Server 1 (Production) | 80 | 80% of traffic |
| Server 2 (New Version) | 20 | 20% of traffic |

Configuration:

| Field | Value |
| --- | --- |
| Record Type | A |
| Routing Policy | Weighted |
| Record ID | Unique name per record (e.g. server-1, server-2) |
| Weight | 80 or 20 |

Test weighted distribution:

```text
# Run 10 DNS lookups and observe IP distribution
for i in {1..10}; do
  dig +short yourdomain.com
done
```

**ARCHITECTURE — Weighted Routing Task**

```text
DNS Query → Route 53 Weighted Policy
     │
     ├── 80% → Server 1 IP (Production)
     └── 20% → Server 2 IP (New version being tested)
```

### Latency Routing

**Purpose:** Route users to the lowest-latency AWS region.

| Region Code | Location |
| --- | --- |
| ap-south-1 | Mumbai, India |
| us-east-1 | N. Virginia, USA |
| eu-west-1 | Ireland, EU |

Configuration:

| Field | Value |
| --- | --- |
| Record Type | A |
| Routing Policy | Latency |
| Region | Select the AWS region where your resource is deployed |

Create one Latency record per region pointing to that region's server/ALB.

**ARCHITECTURE — Latency Routing Task**

```text
User in India → Route 53 measures latency:
  ap-south-1:  18ms  ← LOWEST
  us-east-1:   210ms
  eu-west-1:   120ms
Result: User routed to Mumbai server
```

### Failover Routing

**Purpose:** Disaster recovery with automatic failover to backup server.

Step 1 — Create Health Check:

| Field | Value |
| --- | --- |
| Protocol | HTTP |
| Port | 80 |
| Path | /health |
| Failure Threshold | 3 |

Step 2 — Primary Record:

| Field | Value |
| --- | --- |
| Failover Type | Primary |
| Value | Primary Server IP |
| Health Check | Attach the health check created above |

Step 3 — Secondary Record:

| Field | Value |
| --- | --- |
| Failover Type | Secondary |
| Value | Backup Server IP |
| Health Check | Optional (recommended) |

Test failover — stop the web server on the primary:

```text
# Stop primary server
sudo systemctl stop httpd

# Watch Route 53 health check go unhealthy (~30-90 seconds)
# Then DNS will start returning the secondary IP
dig +short yourdomain.com

# Restore primary
sudo systemctl start httpd
```

**ARCHITECTURE — Failover Routing Task**

```text
Normal:   Route 53 → Primary (Healthy ✓) → Traffic flows here
Failure:  Route 53 → Primary (Unhealthy ✗) → Traffic → Secondary ✓
```

### Geolocation Routing

**Purpose:** Route traffic based on user's country or continent.

| Location | Server | Use Case |
| --- | --- | --- |
| India | India Server IP | Local language and pricing |
| USA | US Server IP | English content, US pricing |
| Default | Global Server IP | Catch-all for all other countries |

Configuration:

| Field | Value |
| --- | --- |
| Record Type | A |
| Routing Policy | Geolocation |
| Location | Select Continent, Country, or US State |

> Always create a Default geolocation record. Without it, users from unlisted countries will get NXDOMAIN errors.

**ARCHITECTURE — Geolocation Routing Task**

```text
Route 53 Geolocation
  IN (India)  → India EC2
  US (USA)    → US EC2
  Default     → Global EC2  (catches everyone else)
```

### Multi-Value Routing

**Purpose:** Return multiple healthy IP addresses for basic client-side load distribution.

| Field | Value |
| --- | --- |
| Record Type | A |
| Routing Policy | Multivalue Answer |
| Health Check | Enabled — attach one per IP |
| Value | One IP per record (create multiple records) |

Create one record per server IP with health checks. Route 53 returns all healthy IPs.

**ARCHITECTURE — Multi-Value Routing Task**

```text
Route 53 Multi-Value Response:
  54.12.34.56  ✓  (healthy, included in response)
  54.12.34.99  ✓  (healthy, included in response)
  54.12.34.11  ✗  (unhealthy, excluded from response)

Client receives 2 IPs and picks one to connect to
```

---

## Route 53 Record Types — Exploration

Explore different Route 53 DNS record types and their use cases:

- **A Record** → Maps domain to IPv4 address
- **AAAA Record** → Maps domain to IPv6 address
- **CNAME Record** → Maps one domain to another domain
- **MX Record** → Configures email routing for the domain
- **TXT Record** → Used for domain verification and email security (SPF, DKIM, DMARC)
- **NS Record** → Defines the authoritative nameservers for the domain
- **SOA Record** → Stores DNS zone administrative information
- **PTR Record** → Used for reverse DNS lookup (IP → domain)
- **Alias Record** → Points root domain to AWS resources like ALB or CloudFront

Explore and configure each record type in Route 53 to understand their practical use cases in real-world AWS architectures.

---

# Key Takeaways

- **DNS** is the global system that maps domain names to IP addresses through a hierarchical lookup chain
- **Nameservers** are the authoritative source of DNS records — Route 53 assigns 4 NS per hosted zone
- **Route 53** provides DNS management, intelligent routing, domain registration, and health monitoring in one service
- **Hosted Zones** are containers for DNS records — Public for internet, Private for VPC-internal use
- **Alias Records** are preferred over CNAME for AWS resources — they work at root domain and are free
- **Routing Policies** control which resource IP is returned — Simple, Weighted, Latency, Failover, Geolocation, Geoproximity, Multi-Value, IP-Based
- **Health Checks** continuously monitor endpoints and trigger automatic failover when resources become unhealthy
- **TTL** controls how long DNS responses are cached — lower TTL allows faster updates but increases query volume
- **DNS propagation** takes time — always plan changes in advance and lower TTL before major migrations
- **Route 53 has a 100% availability SLA** — it is the only AWS service with a full uptime guarantee

## Explore Routing Policies

- Simple Routing — Single resource, basic use cases
- Weighted Routing — Traffic splitting, A/B testing, Blue-Green deployments
- Latency Routing — Global applications, lowest-latency regional routing
- Failover Routing — Disaster recovery, Active-Passive high availability
- Geolocation Routing — Compliance, localization, region-specific content
- Geoproximity Routing — Fine-grained traffic shaping with bias configuration
- Multi-Value Routing — Basic redundancy across multiple healthy endpoints
- IP-Based Routing — Enterprise networks, ISP-specific or CIDR-based routing

Each policy has its own strengths. Real-world architectures often combine multiple policies using Route 53 Traffic Flow for complex, multi-condition routing logic.

---

> *DNS is the first step of every internet request. Master Route 53 and you control where traffic goes.*
