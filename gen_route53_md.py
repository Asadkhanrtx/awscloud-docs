#!/usr/bin/env python3
"""Generate route53-case-study.md from the Route 53 / DNS case study content."""

lines = []

def h1(t): lines.append(f'# {t}'); lines.append('')
def h2(t): lines.append(f'## {t}'); lines.append('')
def h3(t): lines.append(f'### {t}'); lines.append('')
def h4(t): lines.append(f'#### {t}'); lines.append('')
def body(t): lines.append(t); lines.append('')
def bul(t, level=0): lines.append(('  ' * level) + f'- {t}')
def num(n, t): lines.append(f'{n}. {t}')
def div(): lines.append('---'); lines.append('')
def blockquote(t): lines.append(f'> {t}'); lines.append('')
def diagram_label(t): lines.append(f'**{t}**'); lines.append('')

def cod(text):
    lines.append('```text')
    lines.extend(text.splitlines())
    lines.append('```')
    lines.append('')

def tbl(headers, rows):
    lines.append('| ' + ' | '.join(headers) + ' |')
    lines.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
    for row in rows:
        lines.append('| ' + ' | '.join(str(c) for c in row) + ' |')
    lines.append('')

def step_num(n, title, desc=''):
    lines.append(f'**{n}. {title}**' + (f' — {desc}' if desc else ''))
    lines.append('')


# ── COVER ──────────────────────────────────────────────────────────────────────
lines.append('# AWS Route 53 & DNS — Complete Case Study Documentation')
lines.append('')
lines.append('> **Complete Case Study** — DNS Fundamentals · Route 53 · Routing Policies · Practical Tasks')
lines.append('')
div()

# ── TABLE OF CONTENTS ─────────────────────────────────────────────────────────
lines.append('## Table of Contents')
lines.append('')
lines.append('1. [How the Internet Finds Your Website](#how-the-internet-finds-your-website)')
lines.append('2. [Introduction to DNS](#introduction-to-dns)')
lines.append('3. [DNS Service Providers](#dns-service-providers)')
lines.append('4. [AWS Route 53](#aws-route-53)')
lines.append('5. [Route 53 Core Components](#route-53-core-components)')
lines.append('6. [DNS Record Types](#dns-record-types)')
lines.append('7. [Alias Records](#alias-records)')
lines.append('8. [Route 53 Routing Policies](#route-53-routing-policies)')
lines.append('9. [Route 53 Health Checks](#route-53-health-checks)')
lines.append('10. [TASKS — Hands-On Route 53 Labs](#tasks--hands-on-route-53-labs)')
lines.append('11. [Key Takeaways](#key-takeaways)')
lines.append('')
div()

# ── SECTION 0 — HOW THE INTERNET FINDS YOUR WEBSITE ──────────────────────────
h1('How the Internet Finds Your Website')
body(
    'Every time you type a website address into a browser, a complex chain of lookups happens '
    'invisibly within milliseconds. Understanding this chain — DNS — is the foundation for '
    'everything Route 53 does.'
)

h2('What Happens When a Client Hits a Domain')
body(
    'When you type `www.example.com` and press Enter, your device does not know the IP address '
    'of that server. It needs to ask. The Domain Name System (DNS) is the global distributed '
    'database that maps human-readable names to machine-readable IP addresses. Here is the full '
    'journey step by step:'
)

diagram_label('ARCHITECTURE — Full DNS Resolution Flow')
cod(
    'Client Browser\n'
    '      │\n'
    '      │ 1. Check Browser Cache\n'
    '      │    (is example.com already cached? TTL still valid?)\n'
    '      │\n'
    '      │ 2. Check OS / hosts file\n'
    '      │    (/etc/hosts, Windows hosts file)\n'
    '      │\n'
    '      ▼\n'
    'Recursive Resolver  ←──── (ISP DNS / 8.8.8.8 / 1.1.1.1)\n'
    '      │\n'
    '      │ 3. Check Resolver Cache\n'
    '      │    (has it resolved this recently?)\n'
    '      │\n'
    '      │ 4. Ask Root DNS Server\n'
    '      │    "Who handles .com?"\n'
    '      ▼\n'
    'Root DNS Server  (13 root server clusters worldwide)\n'
    '      │\n'
    '      │ "Go ask the .com TLD server"\n'
    '      │ Returns address of .com TLD nameserver\n'
    '      ▼\n'
    'TLD DNS Server  (.com / .org / .net / .io etc.)\n'
    '      │\n'
    '      │ "Go ask the Authoritative NS for example.com"\n'
    '      │ Returns the Authoritative Name Server records\n'
    '      ▼\n'
    'Authoritative Name Server  (Route 53 / Cloudflare / etc.)\n'
    '      │\n'
    '      │ "www.example.com → 54.12.34.56"\n'
    '      │ Returns the actual A Record / IP address\n'
    '      ▼\n'
    'Recursive Resolver  (caches result for TTL duration)\n'
    '      │\n'
    '      ▼\n'
    'Client Browser\n'
    '      │\n'
    '      │ 5. TCP/TLS connection established to 54.12.34.56\n'
    '      │ 6. HTTP request sent\n'
    '      ▼\n'
    'Web Server  →  Response  →  Page loads\n'
    '\n'
    'Result also cached in: Browser Cache + OS Cache + Resolver Cache (based on TTL)'
)

h3('What is a Nameserver?')
body(
    'A **nameserver** is a server that stores DNS records and answers DNS queries. When you '
    'register a domain and create a hosted zone, Route 53 assigns you 4 nameservers. These '
    'are the servers that the rest of the internet will ask when looking up your domain.'
)
body(
    'Nameservers form a hierarchy: **Root Nameservers** → **TLD Nameservers** → '
    '**Authoritative Nameservers**. Each layer delegates responsibility to the next layer '
    'until the actual record is found.'
)
diagram_label('ARCHITECTURE — Nameserver Hierarchy')
cod(
    'ROOT SERVERS  (.)  ← 13 globally distributed clusters, managed by ICANN\n'
    '     │\n'
    '     ├── .com  TLD Servers  (managed by Verisign)\n'
    '     │      │\n'
    '     │      └── example.com  Authoritative NS  (managed by Route 53)\n'
    '     │               │\n'
    '     │               ├── www.example.com  →  54.12.34.56   (A Record)\n'
    '     │               ├── api.example.com  →  54.12.34.99   (A Record)\n'
    '     │               └── mail.example.com →  mail.google   (MX Record)\n'
    '     │\n'
    '     ├── .org  TLD Servers\n'
    '     ├── .net  TLD Servers\n'
    '     └── .io   TLD Servers'
)

h3('DNS Delegation — How Your Domain Points to Route 53')
body(
    "When you buy a domain from GoDaddy or Namecheap, their nameservers are used by default. "
    "To use Route 53 as your DNS provider, you delegate authority by updating the nameservers "
    "at your registrar to point to Route 53's nameservers."
)
diagram_label('ARCHITECTURE — DNS Delegation Flow')
cod(
    'Domain Registrar (GoDaddy / Namecheap)\n'
    '     │\n'
    '     │  You update NS records here to point to Route 53\n'
    '     ▼\n'
    'Route 53 Nameservers\n'
    '     ns-123.awsdns-45.com\n'
    '     ns-678.awsdns-12.net\n'
    '     ns-901.awsdns-34.org\n'
    '     ns-234.awsdns-56.co.uk\n'
    '     │\n'
    '     │  Route 53 now answers all DNS queries for your domain\n'
    '     ▼\n'
    'DNS Queries from the internet → Route 53 Hosted Zone → DNS Records → IP Address'
)

# ── SECTION 1 — INTRODUCTION TO DNS ──────────────────────────────────────────
div()
h1('Introduction to DNS')

h2('What is DNS?')
body('DNS (Domain Name System) translates human-friendly domain names into machine-readable IP addresses.')
body('Example:')
cod('www.google.com  →  172.217.18.36')
body(
    "DNS acts like the **internet's phone book**, allowing users to access websites using names "
    "instead of remembering IP addresses."
)

h2('Why DNS is Important')
body('Without DNS, users would need to remember IP addresses for every website.')
body('DNS provides:')
bul('Easy-to-remember website names')
bul('Stable access even if server IPs change')
bul('Scalability for millions of websites')
bul('Load distribution through multiple A records (Round Robin DNS)')
bul('Security and spam protection through TXT / SPF / DKIM records')
lines.append('')

h2('DNS Hierarchy')
body('DNS uses a hierarchical naming structure:')
cod(
    '.\n'
    '└── .com\n'
    '    └── example.com\n'
    '        ├── www.example.com\n'
    '        └── api.example.com'
)

h2('How DNS Resolution Works')
h3('DNS Resolution Steps')
body('When you enter `www.example.com` in a browser:')

steps = [
    ('Browser Cache Check', 'Browser checks if the domain IP is already cached locally.'),
    ('OS Cache Check', 'Operating system checks its DNS cache (and the local hosts file).'),
    ('Query Recursive Resolver', 'Device sends the request to a recursive resolver (ISP, Google DNS `8.8.8.8`, Cloudflare `1.1.1.1`).'),
    ('Root DNS Server', 'Resolver asks the Root Server for `.com` information. Root Server points to the `.com` TLD server.'),
    ('TLD DNS Server', 'Resolver asks the TLD server for `example.com`. TLD server returns the Authoritative Name Server.'),
    ('Authoritative Name Server', 'Returns the actual IP address of `www.example.com`.'),
    ('Browser Connects to Server', 'Browser receives the IP and loads the website.'),
    ('Caching', 'The result is cached for future requests based on TTL.'),
]
for i, (title, desc) in enumerate(steps, 1):
    lines.append(f'{i}. **{title}** — {desc}')
lines.append('')

h3('Key DNS Components')
tbl(['Component', 'Purpose'], [
    ['**Recursive Resolver**', 'Performs the full DNS lookup on behalf of the client. Caches results.'],
    ['**Root Server**', 'Directs requests to TLD servers. 13 root server clusters worldwide.'],
    ['**TLD Server**', 'Handles domains like .com, .org, .net. Knows which NS is authoritative.'],
    ['**Authoritative Server**', 'Stores the actual DNS records for a domain. Final answer source.'],
    ['**DNS Cache**', 'Speeds up future lookups by storing recent results based on TTL.'],
])

h3('Important DNS Terms')
tbl(['Term', 'Description'], [
    ['**Domain Name**', 'Human-readable website name (e.g. example.com)'],
    ['**IP Address**', 'Numerical server address (e.g. 54.12.34.56 for IPv4)'],
    ['**TTL**', 'Time To Live — how long DNS records stay cached before re-querying'],
    ['**FQDN**', 'Fully Qualified Domain Name — complete domain name (www.example.com.)'],
    ['**TLD**', 'Top-Level Domain — the last segment of a domain name (.com, .org, .io)'],
    ['**Zone File**', 'Text file containing all DNS records for a hosted zone'],
    ['**Propagation**', 'The time it takes for DNS changes to spread across global servers'],
    ['**Delegation**', 'Assigning DNS authority for a subdomain to a different nameserver'],
])

# ── SECTION 2 — DNS SERVICE PROVIDERS ────────────────────────────────────────
div()
h1('DNS Service Providers')

h2('Popular DNS Providers')
tbl(['Provider', 'Type', 'Features'], [
    ['**GoDaddy**', 'Registrar + DNS Hosting', 'Beginner-friendly, popular domain provider'],
    ['**Namecheap**', 'Registrar + DNS Hosting', 'Affordable pricing, free Whois privacy'],
    ['**Cloudflare**', 'DNS Hosting + CDN', 'Fast DNS, DDoS protection, free tier, proxy mode'],
    ['**AWS Route 53**', 'Registrar + DNS Hosting', 'AWS integration, advanced routing policies, health checks'],
    ['**Google Cloud DNS**', 'DNS Hosting', 'Low latency, global anycast network'],
])

h2('Domain Registrar vs DNS Hosting')

h3('Domain Registrar')
body('Lets you purchase and own a domain name and maintains domain ownership records.')
body('Examples:')
bul('GoDaddy')
bul('Namecheap')
bul('Route 53')
lines.append('')

h3('DNS Hosting Provider')
body('Hosts DNS records for your domain and responds to DNS queries from the internet.')
body('Examples:')
bul('Cloudflare')
bul('Route 53')
bul('Google Cloud DNS')
lines.append('')

h3('Simple Analogy')
bul('**Domain Registrar** → Registers your house address with the city')
bul('**DNS Hosting Provider** → Delivers mail to your house once the address is known')
lines.append('')
body(
    "You can buy a domain from **GoDaddy** and use **Route 53** or **Cloudflare** for DNS hosting. "
    "The registrar and the DNS host do not have to be the same company — you simply point your "
    "registrar's NS records to whichever DNS host you prefer."
)

# ── SECTION 3 — AWS ROUTE 53 ──────────────────────────────────────────────────
div()
h1('AWS Route 53')

h2('What is Route 53?')
body(
    'Amazon Route 53 is a **highly available, scalable, fully managed, and authoritative DNS service** '
    'provided by AWS.'
)
blockquote(
    "Authoritative DNS means you can directly manage and update DNS records for your domain. "
    "Route 53's answer is the final, definitive answer — it is not a cached or forwarded response."
)
body('Route 53 also acts as:')
bul('A **Domain Registrar** — purchase and manage domains directly through AWS')
bul('A **DNS Routing Service** — routes traffic using intelligent policies')
bul('A **Health Checking Service** — monitors endpoints and reroutes on failure')
lines.append('')

h2('Main Features')
tbl(['Feature', 'Description'], [
    ['**Domain Registration**', 'Purchase and manage domains through AWS. Integrates instantly with hosted zones.'],
    ['**DNS Routing**', 'Routes traffic to resources like EC2, S3, ALB, CloudFront, API Gateway'],
    ['**Health Checks**', 'Monitors endpoints and routes traffic only to healthy resources'],
    ['**High Availability**', 'AWS provides a 100% availability SLA — the only AWS service with a full uptime guarantee'],
    ['**Traffic Flow**', 'Visual editor for complex multi-policy routing configurations'],
    ['**DNSSEC**', 'DNS Security Extensions — protects against spoofing and cache poisoning attacks'],
    ['**Private DNS**', 'Internal DNS resolution within VPCs without exposing records to the public internet'],
])

h2('Why is it Called Route 53?')
body('The name has two meanings:')
bul('**Route** → Routes internet/DNS traffic to the correct destination')
bul('**53** → DNS uses **port 53** for queries and responses')
lines.append('')
body('Port reference:')
cod(
    'HTTP  → Port 80\n'
    'HTTPS → Port 443\n'
    'DNS   → Port 53   ← Route 53 is named after this'
)

# ── SECTION 4 — ROUTE 53 CORE COMPONENTS ─────────────────────────────────────
div()
h1('Route 53 Core Components')

h2('Hosted Zones')
body(
    'A **Hosted Zone** is a container for DNS records of a domain. It is the equivalent of a DNS '
    'zone file — it holds all the records that define how traffic is routed for that domain and '
    'its subdomains.'
)
body('Example hosted zones:')
bul('`example.com`')
bul('`api.example.com` (subdomain delegation)')
lines.append('')
body('Route 53 automatically creates two records in every new hosted zone:')
bul('**NS Record** → Route 53 name servers assigned to your zone')
bul('**SOA Record** → Administrative metadata about the zone')
lines.append('')

h3('Public Hosted Zone')
body(
    'Used for routing traffic from the **public internet**. DNS records in a public hosted zone '
    'are visible to and resolvable by anyone on the internet.'
)
diagram_label('ARCHITECTURE — Public Hosted Zone')
cod(
    'Internet User\n'
    '      │\n'
    '      ▼\n'
    'Public DNS Query  →  Route 53 Public Hosted Zone (example.com)\n'
    '      │\n'
    '      ├── www.example.com  →  ALB DNS name  (Alias Record)\n'
    '      ├── api.example.com  →  EC2 IP  (A Record)\n'
    '      └── mail.example.com →  mail server  (MX Record)'
)

h3('Private Hosted Zone')
body(
    'Used for routing traffic **inside VPCs only**. Records in a private hosted zone are only '
    'resolvable from EC2 instances and services running inside the associated VPC. '
    'They are completely invisible from the public internet.'
)
diagram_label('ARCHITECTURE — Private Hosted Zone')
cod(
    'VPC  (10.0.0.0/16)\n'
    '      │\n'
    '      │  Internal DNS query from EC2 App Server\n'
    '      ▼\n'
    'Route 53 Private Hosted Zone (internal.example.com)\n'
    '      │\n'
    '      ├── db.internal.example.com  →  10.0.1.50  (RDS Private IP)\n'
    '      ├── cache.internal.example.com → 10.0.1.60  (ElastiCache)\n'
    '      └── app.internal.example.com  → 10.0.2.10  (Internal ALB)\n'
    '\n'
    'NOTE: These records are NOT visible from the public internet'
)
blockquote('Public zones work on the internet. Private zones work only inside AWS VPCs.')

h2('Name Servers (NS)')
body(
    'Name Servers host DNS records and answer DNS queries. Route 53 assigns 4 name servers to '
    'each hosted zone for redundancy and global availability.'
)
cod(
    'ns-123.awsdns-45.com\n'
    'ns-678.awsdns-12.net\n'
    'ns-901.awsdns-34.org\n'
    'ns-234.awsdns-56.co.uk'
)
body(
    'AWS uses **anycast routing** for its nameservers, meaning queries are automatically answered '
    'by the geographically nearest Route 53 infrastructure for lowest latency.'
)

h2('DNS Delegation')
body('To use Route 53 DNS for a domain purchased elsewhere:')
num(1, 'Buy domain from registrar (GoDaddy, Namecheap)')
num(2, 'Create Hosted Zone in Route 53')
num(3, 'Copy the 4 Route 53 NS records')
num(4, 'Update nameservers at your registrar to the Route 53 NS values')
lines.append('')
cod(
    'GoDaddy Domain\n'
    '      │\n'
    '      ▼\n'
    'Update Nameservers → Route 53 NS Records\n'
    '      │\n'
    '      ▼\n'
    'Route 53 Name Servers  (all DNS queries now handled by Route 53)\n'
    '      │\n'
    '      ▼\n'
    'Route 53 Hosted Zone  →  Returns correct record  →  Client gets IP'
)

h2('SOA Record')
body(
    'SOA = **Start of Authority**. Contains administrative details about the hosted zone. '
    'The SOA record specifies:'
)
bul('**Primary Name Server** — the main authoritative NS for the zone')
bul('**Administrator Contact** — the email of the zone administrator')
bul('**Serial Number** — the version number of the zone (increments on each change)')
bul('**Refresh Interval** — how often secondary NS servers check for zone updates')
bul('**Retry Interval** — how long secondary NS waits before retrying a failed refresh')
bul('**Expire Duration** — how long secondary NS will serve stale data if primary is unreachable')
bul('**Default TTL** — the default Time To Live used for DNS caching')
lines.append('')
blockquote('The SOA record is usually managed automatically by Route 53.')

h2('TTL (Time To Live)')
body(
    'TTL defines how long DNS records stay cached in resolvers and browsers before they must '
    're-query the authoritative nameserver.'
)
tbl(['TTL Type', 'Effect', 'When to Use'], [
    ['**High TTL** (e.g. 86400 = 24 hr)', 'Less DNS traffic, slower propagation of changes', 'Stable production records'],
    ['**Low TTL** (e.g. 60 sec)', 'Faster updates, more DNS queries, higher cost', 'Before migrations, during failover testing'],
    ['**Zero TTL**', 'No caching — always queries authoritative NS', 'Rapid change scenarios (not recommended long-term)'],
])
blockquote('Alias records do not allow manual TTL configuration — AWS manages TTL automatically.')

# ── SECTION 5 — DNS RECORD TYPES ─────────────────────────────────────────────
div()
h1('DNS Record Types')

cod(
    'A Record       → Domain    → IPv4 Address\n'
    'AAAA Record    → Domain    → IPv6 Address\n'
    'CNAME          → Domain    → Another Domain\n'
    'MX Record      → Domain    → Mail Server\n'
    'TXT Record     → Text Metadata / Domain Verification / Email Security\n'
    'NS Record      → Authoritative Name Servers\n'
    'PTR Record     → IP Address → Domain  (Reverse DNS)\n'
    'SRV Record     → Service Host + Port\n'
    'SOA Record     → Zone administrative information\n'
    'Alias Record   → Domain    → AWS Resource  (Route 53 specific)'
)

h2('A Record')
body('Maps a domain name to an **IPv4 address**. The most common DNS record type.')
cod('example.com  →  54.12.34.56')
body(
    'You can have multiple A records for the same domain pointing to different IPs. '
    'DNS resolvers will return all IPs and clients typically use round-robin to pick one.'
)

h2('AAAA Record')
body('Maps a domain name to an **IPv6 address**.')
cod('example.com  →  2001:db8::1')
body(
    'As IPv6 adoption grows, AAAA records are increasingly important. Many modern applications '
    'configure both A and AAAA records for dual-stack support.'
)

h2('CNAME Record')
body('Maps one domain name to **another domain name** (not directly to an IP).')
cod('www.example.com  →  example.com')
tbl(['Feature', 'Details'], [
    ['**Limitation**', 'Cannot be used for the root/apex domain (example.com) — only subdomains'],
    ['**Resolution**', 'Resolver follows the chain until an A/AAAA record is found'],
    ['**Common Use**', 'Subdomains like www.example.com, blog.example.com, shop.example.com'],
    ['**Chaining**', 'CNAME can point to another CNAME, but avoid deep chains (latency)'],
])

h2('MX Record')
body('Defines **mail servers** for a domain. MX records have a priority value — lower number = higher priority.')
cod('example.com  →  Priority 1  →  aspmx.l.google.com\nexample.com  →  Priority 5  →  alt1.aspmx.l.google.com')
blockquote(
    'When someone sends an email to user@example.com, the MX record tells the internet '
    'which mail server should receive that email.'
)

h2('TXT Record')
body('Stores **text-based information** for a domain. Used for:')
bul('**Domain Verification** — proves domain ownership to Google Workspace, Microsoft 365, etc.')
bul('**SPF (Sender Policy Framework)** — specifies which mail servers can send on behalf of your domain')
bul('**DKIM (DomainKeys Identified Mail)** — cryptographic email signature verification')
bul('**DMARC** — policy for handling emails that fail SPF or DKIM checks')
lines.append('')
cod(
    '# SPF Record — allow Google mail servers\n'
    'v=spf1 include:_spf.google.com ~all\n\n'
    '# Domain verification example\n'
    'google-site-verification=abc123def456'
)

h2('NS Record')
body(
    'Defines the **authoritative name servers** for a domain or subdomain. '
    'Automatically created by Route 53 when you create a hosted zone. '
    'NS records can also be used for subdomain delegation — pointing a subdomain to a '
    'completely different set of nameservers.'
)

h2('PTR Record')
body(
    "Used for **reverse DNS lookup** — mapping an IP address back to its associated domain name. "
    "Commonly used in email server verification (to prove a mail server's IP belongs to the claimed domain), "
    "logging, and network troubleshooting."
)
cod('54.12.34.56  →  example.com')
body(
    'PTR records live in special zones under `.in-addr.arpa` (IPv4) or `.ip6.arpa` (IPv6). '
    'For AWS resources, you need to contact AWS support or use your ISP to set PTR records.'
)

h2('SRV Record')
body(
    'Defines the **hostname and port number** for specific services, helping clients '
    'automatically discover where a service is running without hard-coding addresses.'
)
body('Commonly used in:')
bul('VoIP (Voice over IP) services')
bul('SIP (Session Initiation Protocol)')
bul('XMPP (Extensible Messaging)')
bul('Gaming services')
bul('Microsoft Teams / Skype for Business')
lines.append('')
cod(
    '_sip._tcp.example.com  10  60  5060  sip.example.com\n'
    '    │         │    │    │     └─ Target host\n'
    '    │         │    │    └───── Port number\n'
    '    │         │    └────────── Weight\n'
    '    │         └─────────────── Priority\n'
    '    └───────────────────────── Service.Protocol'
)

# ── SECTION 6 — ALIAS RECORDS ─────────────────────────────────────────────────
div()
h1('Alias Records')

body(
    'Alias records are a **Route 53 extension** to standard DNS. They map domain names directly '
    'to AWS resources and solve a key limitation of CNAME records — they work at the apex/root domain.'
)
body('Alias records can target:')
bul('Load Balancers (ALB, NLB, CLB)')
bul('CloudFront distributions')
bul('API Gateway endpoints')
bul('S3 Static Websites')
bul('Global Accelerator')
bul('Another Route 53 record in the same hosted zone')
lines.append('')
body('Features:')
bul('Works at root domain (`example.com`) — unlike CNAME')
bul('Automatically tracks AWS IP changes — no manual updates needed')
bul('No extra DNS query — resolved internally in one step')
bul('Free of charge for queries targeting AWS resources')
bul('Native health check support')
lines.append('')
cod('example.com  →  my-alb-1234567890.us-east-1.elb.amazonaws.com  (Alias)')

h2('CNAME vs Alias Comparison')
tbl(['Feature', 'CNAME', 'Alias'], [
    ['Root Domain Support', 'No — subdomains only', 'Yes — works at apex'],
    ['AWS Native Integration', 'Partial', 'Full native integration'],
    ['Extra DNS Lookup', 'Yes — adds latency', 'No — resolved internally'],
    ['Automatic AWS IP Updates', 'No — manual updates needed', 'Yes — automatic'],
    ['Cost for AWS Targets', 'Standard query charges', 'Free for AWS targets'],
    ['TTL Control', 'Manual', 'Managed by AWS automatically'],
    ['Health Check Support', 'Limited', 'Full support'],
])

# ── SECTION 7 — ROUTING POLICIES ─────────────────────────────────────────────
div()
h1('Route 53 Routing Policies')

blockquote(
    'Routing Policies define how Route 53 responds to DNS queries. DNS itself does NOT route '
    'traffic like a Load Balancer — it only decides which IP or resource name to return in '
    'the DNS response. The client then connects directly to that resource.'
)

h2('Routing Policies Overview')
tbl(['Policy', 'Routes Based On', 'Health Checks', 'Common Use'], [
    ['**Simple**', 'Single resource', 'Limited', 'Basic single-server websites'],
    ['**Weighted**', 'Assigned weights', 'Yes', 'A/B testing, gradual rollout'],
    ['**Latency**', 'Lowest network latency', 'Yes', 'Global low-latency applications'],
    ['**Failover**', 'Primary / Secondary health', 'Required', 'Disaster recovery'],
    ['**Geolocation**', 'User country / continent', 'Yes', 'Localization & compliance'],
    ['**Geoproximity**', 'Geography + configurable bias', 'Yes', 'Fine-grained traffic shaping'],
    ['**Multi-Value**', 'Multiple healthy IPs', 'Yes', 'Basic load distribution'],
    ['**IP-Based**', 'Client IP / CIDR range', 'Yes', 'ISP or network-based routing'],
])

h2('Simple Routing')
body('Returns a single resource for a domain. The simplest routing policy.')
cod('example.com  →  54.12.34.56')
diagram_label('ARCHITECTURE — Simple Routing')
cod(
    'User → DNS Query → Route 53 → Returns 54.12.34.56 → User connects to EC2\n\n'
    'If multiple IPs configured:\n'
    'Route 53 returns ALL IPs → Browser picks one randomly (round-robin)'
)
body('Features:')
bul('Simplest routing policy')
bul('Can return multiple IPs — browser chooses randomly')
bul('No health-check based failover')
bul('Best for small or simple single-server applications')
lines.append('')
body('Use Case: Personal blog hosted on one EC2 instance')

h2('Weighted Routing')
body('Splits traffic between multiple resources using assigned weights.')
cod(
    'Server A → Weight 80   →  80% of traffic\n'
    'Server B → Weight 20   →  20% of traffic'
)
diagram_label('ARCHITECTURE — Weighted Routing')
cod(
    'User Request\n'
    '     │\n'
    '     ▼\n'
    'Route 53 Weighted Policy\n'
    '     │\n'
    '     ├── 80% ──→ Server A (Production v1)\n'
    '     │               IP: 54.12.34.56\n'
    '     │\n'
    '     └── 20% ──→ Server B (New v2 being tested)\n'
    '                     IP: 54.12.34.99'
)
body('Features:')
bul('Supports gradual deployments and A/B testing')
bul('Blue-Green deployments — shift traffic incrementally')
bul('Weight range: `0–255`')
bul('Weight `0` stops traffic to a resource without deleting the record')
bul('If all weights are `0`, traffic is distributed equally among all records')
lines.append('')
body('Use Case: Testing a new application version with a limited percentage of users')

h2('Latency Routing')
body(
    "Routes users to the AWS region with the **lowest network latency**. This is measured "
    "between the end user's network and the AWS region — not purely geographic distance."
)
cod(
    'India User  → Mumbai Region    (ap-south-1)   ← lowest latency path\n'
    'US User     → Virginia Region  (us-east-1)\n'
    'EU User     → Ireland Region   (eu-west-1)'
)
diagram_label('ARCHITECTURE — Latency Routing')
cod(
    'User in India\n'
    '     │\n'
    '     ▼\n'
    'Route 53 Latency Check\n'
    '     │\n'
    '     ├── ap-south-1  (Mumbai)   ← 18ms   ← WINNER\n'
    '     ├── us-east-1   (Virginia) ← 210ms\n'
    '     └── eu-west-1   (Ireland)  ← 120ms\n'
    '     │\n'
    '     ▼\n'
    'User directed to Mumbai EC2 / ALB'
)
body('Features:')
bul('Optimizes global application performance')
bul('Based on actual latency measurements, not geographic proximity')
bul('Can integrate with health checks')
lines.append('')
blockquote('Germany users may be directed to US-East if that region has lower latency than EU regions.')
body('Use Case: Global applications requiring fast response times for users worldwide')

h2('Failover Routing')
body(
    'Routes traffic to a **primary resource** and automatically switches to a **secondary backup** '
    'if the primary becomes unhealthy. Requires health checks.'
)
diagram_label('ARCHITECTURE — Failover Routing')
cod(
    'Normal State:\n'
    'User → Route 53 → Primary Server (54.12.34.56) ← Active, Healthy\n'
    '                   Secondary Server (54.99.88.77)  ← Standby\n'
    '\n'
    'Failover State (Primary unhealthy):\n'
    'User → Route 53 → Primary Server (54.12.34.56) ← UNHEALTHY ✗\n'
    '               └─→ Secondary Server (54.99.88.77) ← NOW ACTIVE ✓\n'
    '\n'
    'Route 53 Health Checker detects failure within ~30 seconds\n'
    'DNS TTL determines how quickly clients switch over'
)
body('Features:')
bul('Requires health checks on the primary record')
bul('Automatic disaster recovery — no manual intervention')
bul('Active-Passive setup (primary serves all traffic normally)')
bul('Secondary can be in a different region for maximum resilience')
lines.append('')
body('Use Case: High availability applications with backup disaster recovery regions')

h2('Geolocation Routing')
body(
    "Routes traffic based on the **geographic location** of the user, determined by their "
    "IP address. Unlike Latency Routing, this is purely location-based regardless of speed."
)
body('Supported levels:')
bul('Continent (e.g. Europe, Asia, North America)')
bul('Country (e.g. Germany, India, United States)')
bul('US State (granular US-only routing)')
lines.append('')
cod(
    'Germany Users → German Server  (GDPR compliance)\n'
    'India Users   → India Server   (local language, pricing)\n'
    'Default       → Global Server  (catches all other countries)'
)
diagram_label('ARCHITECTURE — Geolocation Routing')
cod(
    'Route 53\n'
    '     │\n'
    '     ├── Country: DE (Germany)  ──→ eu-central-1 (Frankfurt)\n'
    '     ├── Country: IN (India)    ──→ ap-south-1 (Mumbai)\n'
    '     ├── Country: US (United States) ──→ us-east-1 (N. Virginia)\n'
    '     └── Default Record         ──→ us-east-1 (catches everyone else)\n'
    '\n'
    'IMPORTANT: Always configure a Default record.\n'
    'Without it, users from unlisted countries get NXDOMAIN (no DNS response).'
)
body('Features:')
bul('Supports localization (language, currency, pricing)')
bul('Useful for legal and compliance requirements (GDPR, data residency)')
bul('Default record strongly recommended to handle unlisted locations')
lines.append('')
body('Use Case: Region-specific pricing, language, or media content restrictions')

h2('Geoproximity Routing')
body(
    'Routes traffic based on user location AND resource location, with a configurable **bias** '
    'that expands or shrinks the geographic region served by each resource. '
    'Requires **Route 53 Traffic Flow**.'
)
body('Bias values:')
bul('`+1 to +99` → Expands the effective traffic region (attracts more users)')
bul('`-1 to -99` → Shrinks the effective traffic region (repels users to other endpoints)')
lines.append('')
cod('US-East Bias +50  →  Receives traffic from a larger geographic area than normal')
diagram_label('ARCHITECTURE — Geoproximity Routing with Bias')
cod(
    'Without Bias:\n'
    'US Users  → US-East\n'
    'EU Users  → EU-West\n'
    '(split at geographic midpoint)\n'
    '\n'
    'With US-East Bias +50:\n'
    'US Users  → US-East\n'
    'Most EU Users → US-East  ← bias expands the US-East coverage area\n'
    'Far EU Users  → EU-West\n'
    '\n'
    'Useful when one region has more capacity or lower cost'
)
body('Use Case: Intentionally directing more users to a preferred or higher-capacity region')

h2('Multi-Value Routing')
body(
    'Returns **multiple healthy IP addresses** for a single DNS query. '
    'The client receives up to 8 healthy IPs and picks one — providing basic client-side load distribution.'
)
cod(
    'Healthy:\n'
    '54.12.34.56  ✓\n'
    '54.12.34.99  ✓\n'
    '54.12.34.11  ✓\n'
    '\n'
    'Unhealthy:\n'
    '54.12.34.22  ✗  ← Route 53 will NOT return this IP'
)
diagram_label('ARCHITECTURE — Multi-Value Routing')
cod(
    'Route 53 Multi-Value Query Response:\n'
    '[\n'
    '  54.12.34.56,  ← healthy\n'
    '  54.12.34.99,  ← healthy\n'
    '  54.12.34.11,  ← healthy\n'
    '  54.12.34.22   ← EXCLUDED (unhealthy)\n'
    ']\n'
    '\n'
    'Client picks one IP randomly and connects directly\n'
    '\n'
    'NOTE: Multi-Value is NOT a replacement for an Elastic Load Balancer.\n'
    'ELB handles connection-level load balancing, health checks, SSL termination.\n'
    'Multi-Value only controls which IPs the DNS response includes.'
)
body('Features:')
bul('Returns up to 8 healthy records per query')
bul('Supports health checks — automatically excludes unhealthy endpoints')
bul('Basic client-side load distribution')
bul('Not a replacement for ELB — DNS does not balance existing connections')
lines.append('')
body('Use Case: Multiple EC2 instances serving the same application with basic redundancy')

h2('IP-Based Routing')
body(
    "Routes traffic based on the **client's IP address or CIDR range**. "
    "You define CIDR blocks and map each block to a specific endpoint."
)
cod(
    '203.0.113.0/24   →  Server A  (Corporate office network)\n'
    '198.51.100.0/24  →  Server B  (ISP or branch office network)\n'
    'Everything else  →  Default Server'
)
diagram_label('ARCHITECTURE — IP-Based Routing')
cod(
    'Client IP: 203.0.113.50\n'
    '     │\n'
    '     ▼\n'
    'Route 53 CIDR Block Lookup\n'
    '     │\n'
    '     │  203.0.113.50 matches 203.0.113.0/24\n'
    '     ▼\n'
    'Server A  (optimized endpoint for this network)'
)
body('Features:')
bul('ISP or network-specific routing for optimized performance')
bul('CIDR-based IP-to-endpoint mapping')
bul('Useful for enterprise branch office routing')
bul('Can direct known bot or crawler IPs to specific handling')
lines.append('')
body('Use Case: Directing branch offices or specific ISP users to optimized endpoints')

# ── SECTION 8 — HEALTH CHECKS ─────────────────────────────────────────────────
div()
h1('Route 53 Health Checks')

body(
    "Route 53 Health Checks continuously monitor application endpoints and automatically stop "
    "routing traffic to unhealthy resources. They are the backbone of Route 53's high availability features."
)
blockquote(
    'Think of Health Checks as an automated monitoring and failover system for your infrastructure. '
    'They run 24/7 from multiple AWS locations worldwide.'
)

h2('Types of Health Checks')

h3('1. Endpoint Health Check')
body(
    'Monitors a specific IP address, domain, or URL using **HTTP, HTTPS, or TCP** protocols. '
    'Route 53 sends requests from health checker locations around the world and evaluates the response.'
)
cod('https://example.com/health  →  Expected: HTTP 200 OK')
body('You can also configure Route 53 to check for specific text in the response body.')

h3('2. Calculated Health Check')
body(
    'Combines multiple individual health checks into a single logical result using '
    '**AND, OR, or NOT** conditions. Useful for expressing complex health logic.'
)
body('Example:')
bul('Healthy only if **2 out of 3** child checks pass')
bul('Unhealthy if ANY of 5 database checks fails')
bul('Healthy only if BOTH the web tier AND the database tier are healthy')
lines.append('')

h3('3. CloudWatch Alarm Health Check')
body(
    'Uses a **CloudWatch Alarm** state instead of directly checking an endpoint. '
    'The health check is considered healthy when the alarm is in OK state and '
    'unhealthy when the alarm is in ALARM state.'
)
blockquote(
    'Route 53 health checkers are public AWS infrastructure and cannot directly reach '
    'resources inside private VPCs. Use CloudWatch Alarm Health Checks for private resources '
    'by publishing custom metrics from your VPC to CloudWatch.'
)

h2('Health Check Configuration')
tbl(['Setting', 'Example', 'Notes'], [
    ['**Protocol**', 'HTTPS', 'HTTP, HTTPS, or TCP'],
    ['**Port**', '443', 'Standard or custom port'],
    ['**Path**', '`/health`', 'Endpoint that returns 200 when healthy'],
    ['**Check Interval**', '30 sec', '10 sec also available (higher cost)'],
    ['**Failure Threshold**', '3 failed checks', 'Consecutive failures before marking unhealthy'],
    ['**Success Threshold**', '1 success', 'Consecutive successes before marking healthy again'],
    ['**Regions**', 'Multiple', 'Choose which AWS regions run health checks from'],
])

h2('Key Health Check Behavior')
bul('Around **15 global AWS health checkers** monitor endpoints continuously from different regions')
bul('Only `2xx` and `3xx` HTTP responses are considered healthy')
bul('Response time threshold: default 4 seconds for standard, 2 seconds for fast checks')
bul('String matching: Route 53 can check the first 5,120 bytes of the response body')
bul('CloudWatch integration: health check status is published as CloudWatch metrics')
bul('SNS Notifications: trigger alerts via SNS when health status changes')
lines.append('')

h2('Health Check + Failover Flow')
diagram_label('ARCHITECTURE — Health Check Failover')
cod(
    'Route 53 Health Checkers (15 global locations)\n'
    '     │\n'
    '     │  Every 30 seconds: GET https://example.com/health\n'
    '     ▼\n'
    'Primary Server  →  HTTP 200  →  HEALTHY ✓\n'
    '     │\n'
    '     │  [If primary returns errors 3 times in a row]\n'
    '     ▼\n'
    'Primary Server  →  Connection Timeout  →  UNHEALTHY ✗\n'
    '     │\n'
    '     │  Route 53 stops returning Primary IP\n'
    '     ▼\n'
    'Secondary Server  →  Route 53 now returns Secondary IP\n'
    '     │\n'
    '     │  Clients get Secondary IP on next DNS query\n'
    '     ▼\n'
    'Traffic automatically rerouted  →  Failover complete\n'
    '\n'
    'When Primary recovers:\n'
    'Route 53 detects healthy response → Resumes sending traffic to Primary'
)

# ── SECTION 9 — TASKS ─────────────────────────────────────────────────────────
div()
h1('TASKS — Hands-On Route 53 Labs')

h2('Task 1 — Host a Website Using Simple Routing')

h3('Objective')
bul('Launch an EC2 instance')
bul('Install a web server')
bul('Configure a custom domain')
bul('Point the domain to EC2 using Route 53')
bul('Access the website publicly')
lines.append('')

h3('Architecture')
diagram_label('ARCHITECTURE — Simple Routing — Task 1')
cod(
    'Internet User\n'
    '     │\n'
    '     ▼\n'
    'www.yourdomain.com\n'
    '     │\n'
    '     ▼  (DNS Query)\n'
    'Route 53 Hosted Zone\n'
    '     │  A Record: yourdomain.com → 54.12.34.56\n'
    '     ▼\n'
    'EC2 Instance (Apache / Nginx)\n'
    'IP: 54.12.34.56  |  Port: 80  |  Public Subnet\n'
    '     │\n'
    '     ▼\n'
    'Response: Hello from AWS Route 53!'
)

h3('Step 1 — Purchase a Domain')
body('**GoDaddy / Namecheap:**')
bul('Purchase a domain')
bul('Route 53 will manage DNS after configuration')
lines.append('')
body('**Route 53 (directly):**')
bul('Open AWS Console → Route 53')
bul('Register Domain')
bul('Hosted zone is created automatically after purchase')
lines.append('')

h3('Step 2 — Launch EC2 Instance')
tbl(['Setting', 'Value'], [
    ['AMI', 'Amazon Linux 2023'],
    ['Instance Type', 't2.micro'],
    ['Public IP', 'Enabled'],
    ['Security Group', 'Allow SSH (22) & HTTP (80)'],
])
body('Launch steps:')
bul('Open EC2 → Launch Instance')
bul('Create or select key pair')
bul('Launch instance')
bul('Note the Public IP address')
lines.append('')
cod('Example Public IP: 54.12.34.56')

h3('Step 3 — Install Apache2 Web Server (Ubuntu)')
body('Connect to EC2:')
cod('ssh -i your-key.pem ubuntu@54.12.34.56')
body('Install Apache2:')
cod(
    'sudo apt update -y\n'
    'sudo apt install apache2 -y\n\n'
    'sudo systemctl start apache2\n'
    'sudo systemctl enable apache2'
)
body('Create sample webpage:')
cod(
    "sudo bash -c 'cat > /var/www/html/index.html << EOF\n"
    '<h1>Hello from AWS Route 53!</h1>\n'
    "EOF'"
)
body('Verify in browser:')
cod('http://54.12.34.56')

h3('Step 4 — Create Route 53 Hosted Zone')
bul('Open Route 53')
bul('Hosted Zones → Create Hosted Zone')
lines.append('')
tbl(['Field', 'Value'], [
    ['Domain Name', 'yourdomain.com'],
    ['Type', 'Public Hosted Zone'],
])
body('Copy the 4 generated NS records. Example:')
cod(
    'ns-123.awsdns-45.com\n'
    'ns-678.awsdns-12.net\n'
    'ns-901.awsdns-34.org\n'
    'ns-234.awsdns-56.co.uk'
)

h3('Step 5 — Update Nameservers at Registrar')
body('**GoDaddy:**')
bul('My Products → DNS')
bul('Nameservers → Change → Custom')
bul('Paste the 4 Route 53 NS records')
lines.append('')
body('**Namecheap:**')
bul('Domain List → Manage')
bul('Nameservers → Custom DNS')
bul('Paste the 4 Route 53 NS records')
lines.append('')
body('DNS propagation typically takes a few minutes to up to 48 hours.')

h3('Step 6 — Create A Record in Route 53')
bul('Route 53 → Hosted Zone → yourdomain.com')
bul('Create Record')
lines.append('')
tbl(['Field', 'Value'], [
    ['Record Name', 'www (or leave blank for root)'],
    ['Record Type', 'A'],
    ['Routing Policy', 'Simple'],
    ['Value', 'EC2 Public IP (54.12.34.56)'],
    ['TTL', '300'],
])

h3('Step 7 — Validate DNS Resolution')
cod(
    '# Check DNS propagation\n'
    'nslookup yourdomain.com\n'
    'dig yourdomain.com\n\n'
    '# Expected output\n'
    ';; ANSWER SECTION:\n'
    'yourdomain.com.  300  IN  A  54.12.34.56'
)
body('Open in browser:')
cod('http://yourdomain.com')

# ── Routing Policies Tasks ────────────────────────────────────────────────────
div()
h2('Routing Policies — Practice Tasks')

h3('Weighted Routing')
body('**Purpose:** Split traffic between servers for A/B testing or gradual deployments.')
tbl(['Server', 'Weight', 'Traffic %'], [
    ['Server 1 (Production)', '80', '80% of traffic'],
    ['Server 2 (New Version)', '20', '20% of traffic'],
])
body('Configuration:')
tbl(['Field', 'Value'], [
    ['Record Type', 'A'],
    ['Routing Policy', 'Weighted'],
    ['Record ID', 'Unique name per record (e.g. server-1, server-2)'],
    ['Weight', '80 or 20'],
])
body('Test weighted distribution:')
cod(
    '# Run 10 DNS lookups and observe IP distribution\n'
    'for i in {1..10}; do\n'
    '  dig +short yourdomain.com\n'
    'done'
)
diagram_label('ARCHITECTURE — Weighted Routing Task')
cod(
    'DNS Query → Route 53 Weighted Policy\n'
    '     │\n'
    '     ├── 80% → Server 1 IP (Production)\n'
    '     └── 20% → Server 2 IP (New version being tested)'
)

h3('Latency Routing')
body('**Purpose:** Route users to the lowest-latency AWS region.')
tbl(['Region Code', 'Location'], [
    ['ap-south-1', 'Mumbai, India'],
    ['us-east-1', 'N. Virginia, USA'],
    ['eu-west-1', 'Ireland, EU'],
])
body('Configuration:')
tbl(['Field', 'Value'], [
    ['Record Type', 'A'],
    ['Routing Policy', 'Latency'],
    ['Region', 'Select the AWS region where your resource is deployed'],
])
body("Create one Latency record per region pointing to that region's server/ALB.")
diagram_label('ARCHITECTURE — Latency Routing Task')
cod(
    'User in India → Route 53 measures latency:\n'
    '  ap-south-1:  18ms  ← LOWEST\n'
    '  us-east-1:   210ms\n'
    '  eu-west-1:   120ms\n'
    'Result: User routed to Mumbai server'
)

h3('Failover Routing')
body('**Purpose:** Disaster recovery with automatic failover to backup server.')
body('Step 1 — Create Health Check:')
tbl(['Field', 'Value'], [
    ['Protocol', 'HTTP'],
    ['Port', '80'],
    ['Path', '/health'],
    ['Failure Threshold', '3'],
])
body('Step 2 — Primary Record:')
tbl(['Field', 'Value'], [
    ['Failover Type', 'Primary'],
    ['Value', 'Primary Server IP'],
    ['Health Check', 'Attach the health check created above'],
])
body('Step 3 — Secondary Record:')
tbl(['Field', 'Value'], [
    ['Failover Type', 'Secondary'],
    ['Value', 'Backup Server IP'],
    ['Health Check', 'Optional (recommended)'],
])
body('Test failover — stop the web server on the primary:')
cod(
    '# Stop primary server\n'
    'sudo systemctl stop httpd\n\n'
    '# Watch Route 53 health check go unhealthy (~30-90 seconds)\n'
    '# Then DNS will start returning the secondary IP\n'
    'dig +short yourdomain.com\n\n'
    '# Restore primary\n'
    'sudo systemctl start httpd'
)
diagram_label('ARCHITECTURE — Failover Routing Task')
cod(
    'Normal:   Route 53 → Primary (Healthy ✓) → Traffic flows here\n'
    'Failure:  Route 53 → Primary (Unhealthy ✗) → Traffic → Secondary ✓'
)

h3('Geolocation Routing')
body("**Purpose:** Route traffic based on user's country or continent.")
tbl(['Location', 'Server', 'Use Case'], [
    ['India', 'India Server IP', 'Local language and pricing'],
    ['USA', 'US Server IP', 'English content, US pricing'],
    ['Default', 'Global Server IP', 'Catch-all for all other countries'],
])
body('Configuration:')
tbl(['Field', 'Value'], [
    ['Record Type', 'A'],
    ['Routing Policy', 'Geolocation'],
    ['Location', 'Select Continent, Country, or US State'],
])
blockquote('Always create a Default geolocation record. Without it, users from unlisted countries will get NXDOMAIN errors.')
diagram_label('ARCHITECTURE — Geolocation Routing Task')
cod(
    'Route 53 Geolocation\n'
    '  IN (India)  → India EC2\n'
    '  US (USA)    → US EC2\n'
    '  Default     → Global EC2  (catches everyone else)'
)

h3('Multi-Value Routing')
body('**Purpose:** Return multiple healthy IP addresses for basic client-side load distribution.')
tbl(['Field', 'Value'], [
    ['Record Type', 'A'],
    ['Routing Policy', 'Multivalue Answer'],
    ['Health Check', 'Enabled — attach one per IP'],
    ['Value', 'One IP per record (create multiple records)'],
])
body('Create one record per server IP with health checks. Route 53 returns all healthy IPs.')
diagram_label('ARCHITECTURE — Multi-Value Routing Task')
cod(
    'Route 53 Multi-Value Response:\n'
    '  54.12.34.56  ✓  (healthy, included in response)\n'
    '  54.12.34.99  ✓  (healthy, included in response)\n'
    '  54.12.34.11  ✗  (unhealthy, excluded from response)\n'
    '\n'
    'Client receives 2 IPs and picks one to connect to'
)

# ── DNS Record Types Exploration ───────────────────────────────────────────────
div()
h2('Route 53 Record Types — Exploration')
body('Explore different Route 53 DNS record types and their use cases:')
bul('**A Record** → Maps domain to IPv4 address')
bul('**AAAA Record** → Maps domain to IPv6 address')
bul('**CNAME Record** → Maps one domain to another domain')
bul('**MX Record** → Configures email routing for the domain')
bul('**TXT Record** → Used for domain verification and email security (SPF, DKIM, DMARC)')
bul('**NS Record** → Defines the authoritative nameservers for the domain')
bul('**SOA Record** → Stores DNS zone administrative information')
bul('**PTR Record** → Used for reverse DNS lookup (IP → domain)')
bul('**Alias Record** → Points root domain to AWS resources like ALB or CloudFront')
lines.append('')
body(
    'Explore and configure each record type in Route 53 to understand their practical use cases '
    'in real-world AWS architectures.'
)

# ── SECTION 10 — KEY TAKEAWAYS ────────────────────────────────────────────────
div()
h1('Key Takeaways')

bul('**DNS** is the global system that maps domain names to IP addresses through a hierarchical lookup chain')
bul('**Nameservers** are the authoritative source of DNS records — Route 53 assigns 4 NS per hosted zone')
bul('**Route 53** provides DNS management, intelligent routing, domain registration, and health monitoring in one service')
bul('**Hosted Zones** are containers for DNS records — Public for internet, Private for VPC-internal use')
bul('**Alias Records** are preferred over CNAME for AWS resources — they work at root domain and are free')
bul('**Routing Policies** control which resource IP is returned — Simple, Weighted, Latency, Failover, Geolocation, Geoproximity, Multi-Value, IP-Based')
bul('**Health Checks** continuously monitor endpoints and trigger automatic failover when resources become unhealthy')
bul('**TTL** controls how long DNS responses are cached — lower TTL allows faster updates but increases query volume')
bul('**DNS propagation** takes time — always plan changes in advance and lower TTL before major migrations')
bul('**Route 53 has a 100% availability SLA** — it is the only AWS service with a full uptime guarantee')
lines.append('')

h2('Explore Routing Policies')
bul('Simple Routing — Single resource, basic use cases')
bul('Weighted Routing — Traffic splitting, A/B testing, Blue-Green deployments')
bul('Latency Routing — Global applications, lowest-latency regional routing')
bul('Failover Routing — Disaster recovery, Active-Passive high availability')
bul('Geolocation Routing — Compliance, localization, region-specific content')
bul('Geoproximity Routing — Fine-grained traffic shaping with bias configuration')
bul('Multi-Value Routing — Basic redundancy across multiple healthy endpoints')
bul('IP-Based Routing — Enterprise networks, ISP-specific or CIDR-based routing')
lines.append('')
body(
    'Each policy has its own strengths. Real-world architectures often combine multiple policies '
    'using Route 53 Traffic Flow for complex, multi-condition routing logic.'
)

div()
lines.append('> *DNS is the first step of every internet request. Master Route 53 and you control where traffic goes.*')
lines.append('')

output = '\n'.join(lines)
with open('route53-case-study.md', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done → route53-case-study.md')
