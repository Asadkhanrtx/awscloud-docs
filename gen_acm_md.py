#!/usr/bin/env python3
"""Generate acm-case-study.md from the ACM case study content."""

lines = []

def h1(t): lines.append(f'# {t}'); lines.append('')
def h2(t): lines.append(f'## {t}'); lines.append('')
def h3(t): lines.append(f'### {t}'); lines.append('')
def h4(t): lines.append(f'#### {t}'); lines.append('')
def body(t): lines.append(t); lines.append('')
def bul(t, level=0): lines.append(('  ' * level) + f'- {t}')
def div(): lines.append('---'); lines.append('')
def blockquote(t): lines.append(f'> {t}'); lines.append('')

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

def section_banner(title):
    lines.append(f'---')
    lines.append('')
    lines.append(f'## {title}')
    lines.append('')

def add_step(num, title, body_text=''):
    lines.append(f'**Step {num}: {title}**')
    lines.append('')
    if body_text:
        lines.append(body_text)
        lines.append('')


# ── COVER ──────────────────────────────────────────────────────────────────────
lines.append('# AWS Certificate Manager (ACM) — Complete Case Study Documentation')
lines.append('')
lines.append('> **Topics:** TLS/SSL Fundamentals · Certificate Providers · ACM Deep Dive · Hands-On Task')
lines.append('')
div()

# ── TABLE OF CONTENTS ─────────────────────────────────────────────────────────
lines.append('## Table of Contents')
lines.append('')
lines.append('1. [PART 1 — SSL / TLS Fundamentals](#part-1--ssl--tls-fundamentals)')
lines.append('2. [What is SSL and TLS?](#what-is-ssl-and-tls)')
lines.append('3. [Certificate Providers and Certificate Types](#certificate-providers-and-certificate-types)')
lines.append('4. [TLS Handshake](#tls-handshake--how-a-secure-connection-is-established)')
lines.append('5. [TLS Termination at the Load Balancer](#tls-termination-at-the-load-balancer)')
lines.append('6. [PART 2 — AWS Certificate Manager (ACM)](#part-2--aws-certificate-manager-acm)')
lines.append('7. [ACM Core Components](#acm-core-components)')
lines.append('8. [PART 3 — Hands-On Task](#part-3--hands-on-task)')
lines.append('9. [Key Takeaways](#key-takeaways)')
lines.append('')
div()

# ── PART 1 ─────────────────────────────────────────────────────────────────────
lines.append('## PART 1 — SSL / TLS Fundamentals')
lines.append('')

h1('What is SSL and TLS?')
body(
    'Every time you see the padlock icon in a browser, **TLS (Transport Layer Security)** is '
    'silently protecting your connection. It ensures three things:'
)
bul('**Confidentiality** — data is encrypted so no one in the middle can read it')
bul('**Integrity** — data cannot be modified in transit without detection')
bul('**Authentication** — you are talking to the real server, not an impersonator')
lines.append('')
body(
    '**SSL (Secure Sockets Layer)** was the original protocol created by Netscape in 1994. '
    'All versions of SSL are now deprecated and considered insecure. '
    '**TLS** is its successor, first standardized in 1999, and is what the entire internet '
    'uses today. Despite this, the industry still commonly uses "SSL" as a colloquial term '
    'for what is technically TLS.'
)

h2('SSL/TLS Version History')
tbl(['Version', 'Year', 'Status', 'Notes'], [
    ['SSL 1.0', '1994', 'Never released', 'Internal Netscape draft — serious security flaws found'],
    ['SSL 2.0', '1995', 'Deprecated (RFC 6176)', 'First public release — broken, MITM vulnerable'],
    ['SSL 3.0', '1996', 'Deprecated (RFC 7568)', 'POODLE attack — do not use'],
    ['TLS 1.0', '1999', 'Deprecated (2021)', 'Upgrade of SSL 3.0 — BEAST attack vulnerability'],
    ['TLS 1.1', '2006', 'Deprecated (2021)', 'Minor fixes — still not recommended'],
    ['TLS 1.2', '2008', 'Widely supported', 'Still secure with correct configuration'],
    ['**TLS 1.3**', '**2018**', '**Current standard**', '**Faster, simpler, more secure — use this**'],
])
blockquote(
    'Modern AWS services (ALB, CloudFront, ACM) support TLS 1.2 and TLS 1.3. '
    'TLS 1.3 reduces handshake latency and removes insecure cipher suites entirely.'
)

h2('What is an X.509 Certificate?')
body(
    'An **X.509 certificate** is the standard format for SSL/TLS certificates. '
    'It is a digital document that binds a public key to an identity (domain name). '
    'It is signed by a Certificate Authority (CA) to prove its authenticity.'
)
body('A certificate contains:')
tbl(['Field', 'Example', 'Purpose'], [
    ['**Subject**', 'CN=saistabakers.com, O=Sais Bakers', 'Who the cert belongs to'],
    ['**SAN (Subject Alt Name)**', 'DNS:saistabakers.com, DNS:www.saistabakers.com', 'All domains covered by this cert'],
    ['**Issuer**', 'Amazon RSA 2048 M01', 'Which CA signed this cert'],
    ['**Public Key**', 'RSA 2048-bit or EC P-256', 'Used in TLS handshake key exchange'],
    ['**Validity Period**', 'Not Before / Not After dates', 'When the cert is valid'],
    ['**Serial Number**', 'Unique hex string', "CA's unique identifier for this cert"],
    ['**Signature**', "CA's cryptographic signature", 'Proves the CA verified and signed it'],
    ['**Key Usage**', 'digitalSignature, keyEncipherment', 'What the cert can be used for'],
])

h2('Certificate Chain of Trust')
body(
    "Certificates work in a **chain of trust**. Your browser comes pre-installed with "
    "a set of **Root CA certificates** (from companies like DigiCert, Comodo, Amazon, "
    "Let's Encrypt's ISRG). When your browser receives a certificate, it walks the "
    "chain from your domain's certificate up to a trusted root."
)
lines.append('![X.509 Certificate Chain — Root CA → Intermediate CA → Leaf Certificate → Browser Trust](diagram_cert_chain.png)')
lines.append('')
body(
    'If any link in the chain is missing, self-signed, or expired, the browser shows '
    '**NET::ERR_CERT_AUTHORITY_INVALID** and warns users not to proceed.'
)

# ── CERTIFICATE PROVIDERS ──────────────────────────────────────────────────────
div()
h1('Certificate Providers and Certificate Types')

h2('Certificate Validation Levels')
tbl(['Type', 'Validation', 'Browser Shows', 'Best For', 'Typical Cost'], [
    ['**DV — Domain Validated**', 'Prove domain ownership only (DNS or HTTP file)', 'Padlock', 'Blogs, personal sites, APIs', "Free (Let's Encrypt) to $10/yr"],
    ['**OV — Organization Validated**', 'Domain + company identity verified by CA', 'Padlock + org in cert details', 'Business websites', '$50–$200/yr'],
    ['**EV — Extended Validation**', 'Rigorous legal entity verification', 'Padlock (was green bar, now removed)', 'Banks, e-commerce, legal', '$100–$500/yr'],
    ['**Wildcard**', 'DV or OV, covers *.example.com', 'Padlock', 'Subdomains at scale', '$70–$300/yr'],
    ['**Multi-Domain (SAN)**', 'Multiple domains on one cert', 'Padlock', 'Multiple products/brands', 'Varies'],
])

h2('Major Certificate Providers')
tbl(['Provider', 'Cost', 'Validity', 'Automation', 'Notes'], [
    ["**Let's Encrypt**", 'Free', '90 days', 'ACME protocol / certbot', 'Largest CA by volume. Non-profit. No EV/OV.'],
    ['**AWS ACM (Public)**', 'Free', '13 months (auto-renew)', 'Fully automated', 'Only for AWS services (ALB, CloudFront, API GW)'],
    ['**DigiCert**', '$175–$500+/yr', '1–2 years', 'Partial', 'Premium CA. EV, OV, DV. Enterprise SLAs.'],
    ['**Comodo / Sectigo**', '$70–$300/yr', '1–2 years', 'Partial', 'Wide browser support. Wildcard & multi-domain.'],
    ['**GlobalSign**', '$150–$400+/yr', '1–2 years', 'API available', 'Enterprise, IoT, DevOps focus.'],
    ['**ZeroSSL**', 'Free / Paid', '90 days (free)', 'ACME support', "Let's Encrypt alternative. REST API."],
    ['**Google Trust Services**', 'Free (via GCP)', '90 days', 'ACME', 'For Google Cloud users.'],
    ['**Self-Signed**', 'Free', 'Any', 'Manual', 'Development only — not trusted by browsers.'],
])

h2("How to Get an SSL Certificate — Let's Encrypt (Without Cloud)")
body(
    "Let's Encrypt is the most widely used free CA. It uses the **ACME protocol** "
    "(Automated Certificate Management Environment, RFC 8555) to automate domain validation "
    "and certificate issuance. The tool **certbot** handles this automatically."
)
cod(
    '# Ubuntu/Debian — Install certbot\n'
    'sudo apt update\n'
    'sudo apt install certbot python3-certbot-apache -y\n\n'
    '# Obtain certificate and auto-configure Apache\n'
    'sudo certbot --apache -d example.com -d www.example.com\n\n'
    '# Certbot will:\n'
    '#  1. Create a temp file at /.well-known/acme-challenge/<token>\n'
    "#  2. Let's Encrypt CA fetches that URL to verify domain ownership\n"
    '#  3. CA issues certificate, certbot installs it in Apache\n'
    '#  4. Adds cron job / systemd timer for auto-renewal every 60 days\n\n'
    '# DNS validation (when no port 80 access)\n'
    'sudo certbot certonly --manual --preferred-challenges dns -d example.com\n'
    '# Certbot gives you a TXT record to add to your DNS provider\n\n'
    '# Test renewal\n'
    'sudo certbot renew --dry-run\n\n'
    '# Certificate files stored at:\n'
    '/etc/letsencrypt/live/example.com/fullchain.pem   # cert + chain\n'
    '/etc/letsencrypt/live/example.com/privkey.pem     # private key'
)

h2('How to Get an SSL Certificate — Manual / Paid CA')
steps_manual = [
    ('Generate Private Key + CSR on your server',
     'The private key never leaves your server. The CSR (Certificate Signing Request) '
     'contains your public key and domain info and is sent to the CA.'),
    ('Submit CSR to CA (DigiCert, Comodo, etc.)', ''),
    ('Complete Domain Validation (DV) or Organization Validation (OV/EV)',
     'For DV: add a CNAME/TXT DNS record or upload a file to your web server. '
     'For OV/EV: the CA calls your company and verifies legal documents.'),
    ('Download Certificate Files from CA',
     'You receive: certificate.crt (your cert), ca-bundle.crt (intermediate chain), '
     'and your existing private key.'),
    ('Install Certificate on Server', ''),
]
for i, (title, desc) in enumerate(steps_manual, 1):
    add_step(i, title, desc)

cod(
    '# Step 1 — Generate private key and CSR\n'
    'openssl genrsa -out private.key 2048\n'
    'openssl req -new -key private.key -out domain.csr \\\n'
    '  -subj "/C=IN/ST=Maharashtra/L=Mumbai/O=Sais Bakers/CN=saistabakers.com"\n\n'
    '# View CSR content\n'
    'openssl req -text -noout -in domain.csr\n\n'
    '# Step 5 — Install on Nginx\n'
    'ssl_certificate     /etc/ssl/certs/certificate.crt;\n'
    'ssl_certificate_key /etc/ssl/private/private.key;\n'
    'ssl_trusted_certificate /etc/ssl/certs/ca-bundle.crt;\n\n'
    '# Install on Apache\n'
    'SSLCertificateFile    /etc/ssl/certs/certificate.crt\n'
    'SSLCertificateKeyFile /etc/ssl/private/private.key\n'
    'SSLCACertificateFile  /etc/ssl/certs/ca-bundle.crt'
)

# ── TLS HANDSHAKE ──────────────────────────────────────────────────────────────
div()
h1('TLS Handshake — How a Secure Connection is Established')

body(
    "Before any application data is exchanged, the **TLS handshake** establishes "
    "a shared secret between client and server, authenticates the server's identity "
    "via its certificate, and negotiates the encryption algorithms to use."
)

lines.append('![TLS 1.3 Handshake — Full Message Flow with Key Derivation](diagram_tls_handshake.png)')
lines.append('')

h2('TLS 1.3 Handshake Step by Step')
tbl(['Step', 'Message', 'Who Sends', 'What It Contains'], [
    ['1', '**ClientHello**', 'Client → Server',
     'Supported TLS versions, cipher suites, client random nonce, key_share (EC public key)'],
    ['2', '**ServerHello**', 'Server → Client',
     'Chosen cipher suite, server random nonce, server key_share, session ID'],
    ['3', '**EncryptedExtensions**', 'Server → Client',
     'Additional negotiated parameters (ALPN, SNI confirmation)'],
    ['4', '**Certificate**', 'Server → Client',
     "Server's X.509 cert chain (leaf + intermediate CA)"],
    ['5', '**CertificateVerify**', 'Server → Client',
     'Digital signature over handshake transcript proving server holds the private key'],
    ['6', '**Finished**', 'Server → Client',
     'HMAC over entire handshake — proves integrity of negotiation'],
    ['7', '**Finished**', 'Client → Server',
     'Client HMAC — confirms both sides derived the same keys'],
    ['8', '**Application Data**', 'Both (encrypted)',
     'All payload encrypted with AEAD cipher (AES-256-GCM or ChaCha20-Poly1305)'],
])

h3('Key Derivation (HKDF)')
body(
    'TLS 1.3 uses **HKDF (HMAC-based Key Derivation Function)** to derive multiple keys '
    'from the shared secret produced by the (EC)DHE key exchange:'
)
cod(
    'Inputs:\n'
    '  Client Random  +  Server Random  +  (EC)DHE shared secret\n\n'
    'HKDF derives:\n'
    '  handshake_traffic_secret  → encrypts the handshake itself\n'
    '  client_application_traffic_secret  → client write key + IV\n'
    '  server_application_traffic_secret  → server write key + IV\n'
    '  exporter_master_secret    → for applications needing keying material\n\n'
    'Session keys are EPHEMERAL — new keys for every session\n'
    'Perfect Forward Secrecy: past sessions cannot be decrypted even if private key is later compromised'
)

h2('How Payload is Encrypted')
body(
    'TLS uses a combination of **asymmetric cryptography** (for key exchange) and '
    '**symmetric cryptography** (for bulk data encryption):'
)
tbl(['Phase', 'Algorithm Type', 'Algorithm Used', 'Purpose'], [
    ['Key Exchange', 'Asymmetric', 'ECDHE (P-256, X25519)', 'Securely establish shared secret without transmitting it'],
    ['Authentication', 'Asymmetric', 'RSA-2048 / ECDSA P-256', 'Server proves identity using private key signature'],
    ['Key Derivation', 'Symmetric', 'HKDF-SHA256 / HKDF-SHA384', 'Derive session keys from shared secret'],
    ['Data Encryption', 'Symmetric', 'AES-256-GCM / ChaCha20-Poly1305', 'Encrypt all application data (fast, AEAD)'],
    ['Integrity', 'Built into AEAD', 'Poly1305 / GCM tag', 'Detect any tampering with encrypted data'],
])
blockquote(
    'AEAD = Authenticated Encryption with Associated Data. It simultaneously encrypts '
    'the payload AND produces an authentication tag. If any byte is altered in transit, '
    'decryption fails and the connection is dropped immediately.'
)

# ── TLS TERMINATION ────────────────────────────────────────────────────────────
div()
h1('TLS Termination at the Load Balancer')

body(
    '**TLS Termination** means the Load Balancer decrypts incoming HTTPS traffic '
    'and forwards plain HTTP to the backend servers. This is the standard pattern '
    'in AWS and most cloud architectures.'
)

h2('Why Terminate TLS at the Load Balancer?')
tbl(['Reason', 'Explanation'], [
    ['**Certificate in one place**', 'Single cert on the ALB — backends need no cert management'],
    ['**Offload CPU cost**', 'TLS crypto is CPU-intensive. ALB handles it, freeing EC2 for app logic'],
    ['**Inspect HTTP headers**', 'ALB can route by path, host, header — only possible after decryption'],
    ['**WAF integration**', 'AWS WAF inspects decrypted HTTP traffic for SQL injection, XSS, etc.'],
    ['**Centralized renewal**', 'ACM auto-renews one cert instead of managing certs on every EC2'],
    ['**Scaling**', 'Add/remove EC2s without redistributing certificates'],
])

cod(
    'HTTPS Traffic Flow with TLS Termination:\n\n'
    'Browser\n'
    '  │\n'
    '  │  HTTPS :443  (TLS encrypted)\n'
    '  ▼\n'
    'ALB  ←── ACM Certificate attached here\n'
    '  │  TLS Handshake + Decryption happens at ALB\n'
    '  │\n'
    '  │  HTTP :80  (plain text — travels over private VPC network only)\n'
    '  ▼\n'
    'EC2 Instances  (no cert needed, receives plain HTTP)\n\n'
    'Optional — End-to-End Encryption (E2E TLS):\n'
    'Browser → HTTPS :443 → ALB → HTTPS :443 → EC2\n'
    '(ALB re-encrypts to backend — used for strict compliance requirements)\n\n'
    'Optional — mTLS (Mutual TLS):\n'
    'Client presents its own cert → ALB validates client cert → Backend\n'
    '(Used in zero-trust, B2B APIs, service mesh)'
)

h2('Traditional SSL vs Cloud SSL — Flow Comparison')
lines.append('![Traditional SSL/TLS — Self-Managed Certificate on Your Server (Without Cloud)](diagram_traditional_ssl.png)')
lines.append('')
body(
    'In the traditional model you generate a private key on your server, create a CSR, '
    'submit it to a CA, download the signed certificate, install it manually, configure '
    'your web server, and remember to renew it before it expires. The private key never '
    'leaves your server — but managing this across many servers becomes complex and error-prone.'
)

# ── PART 2 — AWS ACM ───────────────────────────────────────────────────────────
div()
lines.append('## PART 2 — AWS Certificate Manager (ACM)')
lines.append('')

h1('What is AWS Certificate Manager?')

body(
    '**AWS Certificate Manager (ACM)** is a fully managed service that provisions, manages, '
    'and automatically renews SSL/TLS certificates for use with AWS services. '
    'ACM eliminates the manual work of certificate management — you never handle private keys, '
    'never manually renew, and certificates are free for use with supported AWS services.'
)

lines.append('![AWS ACM — Cloud SSL Certificate Flow: Issuance · Validation · Attachment · Traffic](diagram_aws_acm_ssl.png)')
lines.append('')

h2('ACM Key Features')
tbl(['Feature', 'Details'], [
    ['**Free for AWS services**', 'No charge for ACM public certificates. Only pay for ACM Private CA.'],
    ['**Automatic renewal**', 'ACM renews certs at least 60 days before expiry — completely hands-free'],
    ['**Private key security**', 'Private key stored in AWS HSMs (Hardware Security Modules) — you never see it'],
    ['**Two validation methods**', 'DNS validation (recommended) or Email validation'],
    ['**Wildcard support**', 'Single cert for *.example.com covers unlimited subdomains'],
    ['**Multi-region**', 'CloudFront requires cert in us-east-1. ALB requires cert in same region.'],
    ['**Transparency logging**', 'All issued certs logged to public Certificate Transparency logs'],
    ['**ACM Private CA**', 'Create your own internal CA for private services, mTLS, IoT'],
])

h2('ACM vs Self-Managed Certificate')
tbl(['Aspect', 'ACM (Cloud)', "Self-Managed (Let's Encrypt / DigiCert)"], [
    ['Cost', 'Free (for AWS resources)', 'Free (LE) to $500+/yr (DigiCert EV)'],
    ['Renewal', 'Fully automatic', 'Manual or cron job (can fail)'],
    ['Private Key Access', 'Never exposed — stored in AWS HSM', 'You have full access to key'],
    ['Installation', 'Click to attach to ALB/CloudFront', 'Manual server config (Nginx/Apache)'],
    ['Works on non-AWS servers', 'No — AWS services only', 'Yes — any server'],
    ['Wildcard', 'Yes', 'Yes'],
    ['EV/OV certificates', 'No — DV only', 'Yes (paid CAs)'],
    ['Private CA', 'ACM Private CA (paid)', 'Self-hosted (OpenSSL, CFSSL)'],
    ['Validity', '13 months (auto-renewed)', '90 days (LE) or 1-2 years (paid)'],
])

# ── ACM CORE COMPONENTS ────────────────────────────────────────────────────────
div()
h1('ACM Core Components')

h3('1. Public Certificate')
body(
    "A free, domain-validated certificate issued by **Amazon Trust Services** (Amazon's own CA). "
    "Can only be attached to: **ALB, NLB, CloudFront, API Gateway, Elastic Beanstalk, "
    "AppSync, and other integrated AWS services**. "
    "Cannot be exported or installed on an EC2 directly."
)

h3('2. Certificate Validation')
body('ACM must verify you own the domain before issuing a certificate:')
tbl(['Method', 'How It Works', 'Best For'], [
    ['**DNS Validation (Recommended)**',
     'ACM gives you a CNAME record to add to your DNS. '
     'ACM polls the record periodically. Auto-renews as long as the CNAME stays in DNS.',
     'Route 53 users (one-click add), programmatic workflows'],
    ['**Email Validation**',
     "ACM emails the domain's WHOIS contacts (admin@, webmaster@, etc.). "
     'Someone must click the approval link.',
     'Domains where you cannot modify DNS'],
])

h3('3. Amazon Trust Services (ATS)')
body(
    "**Amazon Trust Services** is Amazon's own Certificate Authority, launched in 2016. "
    'It operates the root CAs and intermediate CAs that sign all ACM-issued certificates.'
)
tbl(['Root CA', 'Algorithm', 'Validity', 'Trusted Since'], [
    ['Amazon Root CA 1', 'RSA 2048', '2038', '2016 — pre-installed in all major browsers/OS'],
    ['Amazon Root CA 2', 'RSA 4096', '2040', '2016'],
    ['Amazon Root CA 3', 'EC P-256', '2040', '2016'],
    ['Amazon Root CA 4', 'EC P-384', '2040', '2016'],
    ['Starfield Services Root CA G2', 'RSA 2048', '2037', 'Cross-certified by older Starfield root for legacy devices'],
])
body(
    'ACM certificates are signed by an **Intermediate CA** (e.g. Amazon RSA 2048 M01, M02) '
    'which is in turn signed by Amazon Root CA 1. Browsers trust Amazon Root CA 1 by default, '
    'so ACM certs are trusted everywhere.'
)

h3('4. Automatic Renewal')
body(
    'ACM begins the renewal process at least **60 days before expiry** for DNS-validated certs. '
    'As long as the validation CNAME record remains in your DNS, renewal is fully automatic '
    'and zero-downtime — the new certificate is silently swapped in.'
)
blockquote(
    'For email-validated certs, someone must click the renewal email within 72 hours. '
    'This is why DNS validation is strongly recommended for production workloads.'
)

h3('5. ACM Private CA')
body(
    '**ACM Private CA** (previously AWS Private CA) lets you create and operate your own '
    'private Certificate Authority for issuing certificates to internal services:'
)
bul('Private microservices communicating over mTLS inside a VPC')
bul('IoT devices that need unique certificates')
bul('Internal tools that need HTTPS without public CA validation')
bul('Zero-trust architectures requiring client certificates')
lines.append('')
body('Pricing: $400/month per CA + $0.75 per certificate issued.')

h2('ACM Supported AWS Services')
tbl(['Service', 'Notes'], [
    ['**Application Load Balancer (ALB)**', 'Most common — HTTPS listener attaches ACM cert'],
    ['**Network Load Balancer (NLB)**', 'TLS listener on port 443'],
    ['**CloudFront**', 'Certificate must be in us-east-1 (N. Virginia) region'],
    ['**API Gateway**', 'Custom domain name with ACM cert'],
    ['**Elastic Beanstalk**', 'HTTPS on load balancer'],
    ['**AppSync**', 'Custom domain with ACM cert'],
    ['**Cognito**', 'Custom domain for hosted UI'],
    ['**Global Accelerator**', 'TLS termination at edge'],
])
blockquote(
    'ACM certificates CANNOT be directly installed on EC2 instances. '
    "If you need HTTPS directly on EC2 (without a load balancer), use Let's Encrypt or a paid CA."
)

h2('ACM Certificate Lifecycle Flow')
cod(
    'You request cert in ACM console\n'
    '  │\n'
    '  │ Enter domain: saistabakers.com + *.saistabakers.com\n'
    '  │ Choose: DNS validation\n'
    '  ▼\n'
    'ACM generates CNAME record\n'
    '  _abc123xyz.saistabakers.com → _xyz789abc.acm-validations.aws\n'
    '  │\n'
    '  │ You add this CNAME to Route 53 (or any DNS provider)\n'
    '  ▼\n'
    'ACM polls your DNS every few minutes\n'
    '  │\n'
    '  │ Sees CNAME record → Domain ownership confirmed\n'
    '  ▼\n'
    'Amazon Trust Services signs certificate\n'
    '  │\n'
    '  │ Status changes: Pending Validation → Issued\n'
    '  ▼\n'
    'You attach cert to ALB HTTPS listener\n'
    '  │\n'
    '  │ Select cert from ACM in ALB listener config\n'
    '  ▼\n'
    'HTTPS live on your domain\n'
    '  │\n'
    '  │ Auto-renewed at 60 days before expiry\n'
    '  ▼\n'
    'Renewal: ACM polls same CNAME → Re-issues → Zero downtime swap'
)

# ── PART 3 — TASK ─────────────────────────────────────────────────────────────
div()
lines.append('## PART 3 — Hands-On Task')
lines.append('')

h1('Task — Enable HTTPS on saistabakers.com Using ACM + Route 53')

h2('Task Overview')
body(
    'In this task, you already own the domain **saistabakers.com** purchased from **Hostinger**. '
    'The goal is to serve a secure HTTPS Apache website using AWS Route 53 for DNS and '
    'AWS ACM for the SSL certificate — without managing any certificate files manually.'
)

tbl(['Component', 'Detail'], [
    ['Domain', 'saistabakers.com (purchased on Hostinger)'],
    ['DNS Provider', 'Amazon Route 53 (Hosted Zone created, NS updated at Hostinger)'],
    ['SSL Certificate', 'AWS ACM — DNS validated, free, auto-renewing'],
    ['Validation', 'CNAME record added in Route 53'],
    ['Traffic', 'Simple Routing — A record → EC2 Public IP'],
    ['Web Server', 'Apache2 on EC2 serving HTTPS (via ACM on ALB or directly)'],
    ['Subdomain', 'www.saistabakers.com → same EC2 (additional CNAME in Route 53)'],
])

h2('Task Architecture Diagram')
lines.append('![saistabakers.com — Hostinger → Route 53 → ACM DNS Validation → HTTPS Apache on EC2](diagram_task_architecture.png)')
lines.append('')

h2('Complete Step-by-Step Guide')

# Step 1
add_step(1, 'Create Route 53 Hosted Zone for saistabakers.com')
bul('Open AWS Console → Route 53 → Hosted Zones → **Create Hosted Zone**')
bul('Domain name: `saistabakers.com`')
bul('Type: **Public Hosted Zone**')
bul('Click Create')
lines.append('')
body('Route 53 auto-creates NS and SOA records. Note the 4 NS records:')
cod(
    'ns-xxx.awsdns-xx.com\n'
    'ns-yyy.awsdns-yy.net\n'
    'ns-zzz.awsdns-zz.org\n'
    'ns-www.awsdns-ww.co.uk'
)

# Step 2
add_step(2, 'Update Nameservers at Hostinger')
bul('Log in to Hostinger → Domains → saistabakers.com → **DNS / Nameservers**')
bul('Change nameservers from Hostinger default to **Custom Nameservers**')
bul('Enter all 4 Route 53 NS records')
bul('Save — DNS propagation takes a few minutes to 48 hours')
lines.append('')
blockquote(
    'Once Hostinger nameservers are updated, all DNS for saistabakers.com is '
    'controlled by Route 53. Any records you add in Route 53 are now live on the internet.'
)

# Step 3
add_step(3, 'Launch EC2 Instance and Install Apache2')
tbl(['Setting', 'Value'], [
    ['AMI', 'Ubuntu 22.04 LTS (or Amazon Linux 2023)'],
    ['Instance Type', 't2.micro (Free Tier)'],
    ['Key Pair', 'Create or select existing'],
    ['Public IP', 'Enable auto-assign'],
    ['Security Group', 'Allow SSH :22 (your IP), HTTP :80 (anywhere), HTTPS :443 (anywhere)'],
])
body('Connect and install Apache2:')
cod(
    'ssh -i your-key.pem ubuntu@<EC2-PUBLIC-IP>\n\n'
    'sudo apt update -y\n'
    'sudo apt install apache2 -y\n'
    'sudo systemctl start apache2\n'
    'sudo systemctl enable apache2\n\n'
    '# Create a simple webpage\n'
    "sudo bash -c 'cat > /var/www/html/index.html << EOF\n"
    '<!DOCTYPE html>\n'
    '<html>\n'
    '<head><title>Sais Bakers</title></head>\n'
    '<body>\n'
    '<h1>Welcome to Sais Bakers!</h1>\n'
    '<p>Secured with AWS ACM + Route 53</p>\n'
    '</body>\n'
    '</html>\n'
    "EOF'\n\n"
    '# Verify Apache is running\n'
    'sudo systemctl status apache2\n'
    'curl http://localhost'
)
body("Note your EC2 public IP — you'll need it for the DNS A record.")

# Step 4
add_step(4, 'Request SSL Certificate in AWS ACM')
bul('Open AWS Console → **Certificate Manager (ACM)**')
bul('Click **Request a certificate** → **Request a public certificate**')
bul('Add domain names:')
lines.append('')
cod('saistabakers.com\n*.saistabakers.com')
bul('Validation method: **DNS validation** (Recommended)', 1)
bul('Key algorithm: RSA 2048', 1)
bul('Click **Request**')
lines.append('')
body(
    'The certificate status shows **Pending validation**. ACM is waiting for you to prove '
    'domain ownership by adding a CNAME record to your DNS.'
)

# Step 5
add_step(5, 'Add ACM CNAME Validation Record to Route 53')
body('In the ACM certificate details page, you will see a CNAME record that ACM generated:')
cod(
    'Record Name:  _abc123xyz.saistabakers.com\n'
    'Record Type:  CNAME\n'
    'Record Value: _xyz789abc.acm-validations.aws'
)
body('Add this to Route 53:')
bul('Go to Route 53 → Hosted Zones → saistabakers.com')
bul('Click **Create Record**')
bul('Record name: `_abc123xyz` (just the part before .saistabakers.com)')
bul('Record type: **CNAME**')
bul('Value: `_xyz789abc.acm-validations.aws`')
bul('TTL: 300')
bul('Click **Create records**')
lines.append('')
body(
    'Shortcut: If your domain is already in Route 53, ACM offers a '
    '**"Create records in Route 53"** button that adds the CNAME automatically in one click.'
)
body('Wait 2–5 minutes. ACM detects the CNAME and the status changes to **Issued**.')

# Step 6
add_step(6, 'Add Subdomain CNAME for www.saistabakers.com')
body('Add a second DNS record in Route 53 to handle the `www` subdomain:')
cod(
    'Record Name:  www\n'
    'Record Type:  CNAME\n'
    'Record Value: saistabakers.com\n'
    'TTL:          300'
)
body(
    'This makes `www.saistabakers.com` resolve to the same destination as `saistabakers.com`. '
    'The ACM wildcard cert (`*.saistabakers.com`) already covers the www subdomain.'
)

# Step 7
add_step(7, 'Create A Record with Simple Routing — Point Domain to EC2')
bul('Route 53 → Hosted Zones → saistabakers.com → **Create Record**')
lines.append('')
tbl(['Field', 'Value'], [
    ['Record Name', '(leave blank — for root domain saistabakers.com)'],
    ['Record Type', 'A — Routes traffic to IPv4 address'],
    ['Routing Policy', 'Simple routing'],
    ['Value', 'EC2 Public IP (e.g. 54.12.34.56)'],
    ['TTL', '300'],
])
body('Click **Create records**.')
body('Your Route 53 hosted zone now has these records:')
cod(
    'saistabakers.com              A      54.12.34.56           (→ EC2)\n'
    'www.saistabakers.com          CNAME  saistabakers.com      (→ root)\n'
    '_abc123.saistabakers.com      CNAME  _xyz789.acm-valid...  (ACM validation)\n'
    'saistabakers.com              NS     ns-xxx.awsdns-xx.com  (auto-created)\n'
    'saistabakers.com              SOA    (auto-created)'
)

# Step 8
add_step(8, 'Attach ACM Certificate to ALB (for full HTTPS end-to-end)')
body(
    "Since ACM certs cannot be directly installed on EC2, you need an **Application Load Balancer** "
    "to terminate TLS and forward HTTP to EC2. If you want HTTPS directly to EC2 without an ALB, "
    "use Let's Encrypt certbot instead (see Step 8B below)."
)
body('ALB path (Recommended for production):')
bul('Create ALB in same region as your EC2')
bul('Add **HTTPS :443 listener** → select your ACM certificate')
bul('Add **HTTP :80 listener** → redirect to HTTPS (optional)')
bul('Create Target Group → add EC2 → attach to ALB')
bul('Update Route 53 A record → change value to ALB DNS name (use **Alias record**)')
lines.append('')
cod(
    '# Route 53 after ALB setup:\n'
    'saistabakers.com   A (Alias)  →  my-alb-1234.us-east-1.elb.amazonaws.com\n\n'
    '# Security Group: EC2\n'
    'Allow HTTP :80 from ALB Security Group (not 0.0.0.0/0)\n\n'
    '# Security Group: ALB\n'
    'Allow HTTPS :443 from 0.0.0.0/0\n'
    'Allow HTTP  :80  from 0.0.0.0/0'
)
body('Alternative — Step 8B: certbot directly on EC2 (no ALB needed):')
cod(
    '# Install certbot on EC2\n'
    'sudo apt install certbot python3-certbot-apache -y\n\n'
    '# Get certificate (requires port 80 open and DNS already pointing to EC2)\n'
    'sudo certbot --apache -d saistabakers.com -d www.saistabakers.com\n\n'
    '# certbot auto-configures Apache with HTTPS and sets up auto-renewal\n'
    'sudo systemctl reload apache2\n\n'
    '# Verify HTTPS\n'
    'curl -I https://saistabakers.com'
)

# Step 9
add_step(9, 'Validate the Complete Setup')
cod(
    '# Check DNS propagation\n'
    'nslookup saistabakers.com\n'
    'dig saistabakers.com A\n'
    'dig www.saistabakers.com CNAME\n\n'
    '# Check certificate details\n'
    'openssl s_client -connect saistabakers.com:443 -servername saistabakers.com\n\n'
    '# Check certificate info\n'
    'curl -vI https://saistabakers.com 2>&1 | grep -E "SSL|certificate|issuer"\n\n'
    '# Expected output:\n'
    '* Server certificate:\n'
    '*  subject: CN=saistabakers.com\n'
    '*  start date: ...\n'
    '*  expire date: ...\n'
    '*  issuer: C=US, O=Amazon, CN=Amazon RSA 2048 M01\n'
    '*  SSL certificate verify ok.\n\n'
    '# Check browser:\n'
    'https://saistabakers.com   →  Padlock visible\n'
    'https://www.saistabakers.com  →  Same page'
)

h2('DNS Records Summary')
tbl(['Record Name', 'Type', 'Value', 'Purpose'], [
    ['saistabakers.com', 'A', '54.12.34.56 (or ALB Alias)', 'Simple routing → EC2 / ALB'],
    ['www.saistabakers.com', 'CNAME', 'saistabakers.com', 'www subdomain → root domain'],
    ['_abc123.saistabakers.com', 'CNAME', '_xyz789.acm-validations.aws', 'ACM DNS validation'],
    ['saistabakers.com', 'NS', '4× awsdns NS records', 'Route 53 nameservers (auto)'],
    ['saistabakers.com', 'SOA', 'ns-xxx.awsdns-xx.com', 'Zone authority record (auto)'],
])

h2('Common Errors and Fixes')
tbl(['Error', 'Cause', 'Fix'], [
    ['ACM cert stuck in Pending Validation',
     'CNAME not yet added or DNS not propagated',
     'Verify CNAME in Route 53. Wait 5 min. Check with: dig _abc123.saistabakers.com CNAME'],
    ['Site shows insecure / padlock missing',
     'HTTP still served or cert not attached',
     'Check ALB HTTPS listener. Redirect HTTP→HTTPS. Verify ACM cert status is Issued.'],
    ['nslookup returns Hostinger IPs',
     'Hostinger nameservers not yet updated or propagation pending',
     'Check Hostinger panel. NS records must match Route 53 NS. Wait up to 48 hours.'],
    ['ERR_CERT_NAME_INVALID',
     'Cert domain does not match the URL',
     'Cert was issued for saistabakers.com but accessed via IP or different domain.'],
    ['Apache serves HTTP not HTTPS on EC2 directly',
     'No cert on EC2 — ACM only works with ALB',
     'Use ALB with ACM cert, or use certbot on EC2 directly.'],
])

# ── KEY TAKEAWAYS ──────────────────────────────────────────────────────────────
div()
h1('Key Takeaways')

bul('**TLS** replaced SSL — TLS 1.3 is the current standard. Never use SSL 2.0/3.0 or TLS 1.0/1.1.')
bul('**X.509 certificates** bind a domain to a public key and are signed by a trusted CA.')
bul('**Certificate chain of trust**: Root CA → Intermediate CA → Leaf certificate.')
bul('**TLS Handshake** authenticates the server, negotiates cipher, and derives session keys — all before data flows.')
bul('**AEAD encryption** (AES-256-GCM, ChaCha20-Poly1305) ensures both confidentiality and integrity of payload.')
bul('**TLS Termination at ALB** offloads certificate management and enables HTTP-level routing and WAF inspection.')
bul('**ACM** is free, fully managed, and auto-renews. Best choice for all AWS-hosted applications.')
bul("**Amazon Trust Services** is Amazon's own CA — its root certs are trusted by all major browsers.")
bul('**DNS Validation** is preferred over Email Validation — it enables fully automatic renewal.')
bul("**ACM certs cannot be installed on EC2 directly** — use ALB, or use certbot/Let's Encrypt for direct EC2 HTTPS.")
bul('**Wildcard cert** (`*.saistabakers.com`) covers all subdomains with one certificate.')
lines.append('')

div()
lines.append('> *HTTPS is not optional — ACM makes it effortless. Secure every endpoint, automate every renewal.*')
lines.append('')

output = '\n'.join(lines)
with open('acm-case-study.md', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done → acm-case-study.md')
