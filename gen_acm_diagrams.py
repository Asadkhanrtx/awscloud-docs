"""Generate PNG architecture diagrams for the ACM case study."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

DARK_BG   = '#1A1A2E'
NAVY      = '#0F3460'
RED_ACC   = '#E94560'
PURPLE    = '#533483'
TEAL      = '#16C79A'
YELLOW    = '#F5A623'
LIGHT_TXT = '#E8E8F0'
GREY      = '#4A4A6A'
GREEN     = '#27AE60'
ORANGE    = '#E67E22'
LIGHT_BG  = '#F0F4FF'

def savefig(name):
    plt.savefig(name, dpi=150, bbox_inches='tight',
                facecolor=plt.gcf().get_facecolor())
    plt.close()
    print(f'  Saved {name}')


# ── Diagram 1: TLS Handshake Flow ────────────────────────────────────────────
def tls_handshake():
    fig, ax = plt.subplots(figsize=(13, 9))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(5, 9.6, 'TLS 1.3 Handshake — How a Secure Connection is Established',
            ha='center', va='center', fontsize=13, fontweight='bold',
            color=LIGHT_TXT, fontfamily='monospace')

    # Entity boxes
    def box(x, y, label, sub, color):
        rect = FancyBboxPatch((x-0.8, y-0.35), 1.6, 0.7,
                              boxstyle='round,pad=0.1', linewidth=2,
                              edgecolor=color, facecolor=NAVY)
        ax.add_patch(rect)
        ax.text(x, y+0.12, label, ha='center', va='center',
                fontsize=10, fontweight='bold', color=LIGHT_TXT)
        ax.text(x, y-0.14, sub, ha='center', va='center',
                fontsize=7.5, color=color)

    box(1.5, 8.7, 'CLIENT', 'Browser / App', TEAL)
    box(8.5, 8.7, 'SERVER', 'Web Server / ALB', RED_ACC)

    # Vertical timeline lines
    ax.plot([1.5, 1.5], [1.0, 8.35], color=TEAL, linewidth=1.5, linestyle='--', alpha=0.5)
    ax.plot([8.5, 8.5], [1.0, 8.35], color=RED_ACC, linewidth=1.5, linestyle='--', alpha=0.5)

    steps = [
        # (y, direction, label, sublabel, color)
        (7.9, '→', '① ClientHello',
         'TLS version, cipher suites, random nonce, supported extensions', YELLOW),
        (7.1, '←', '② ServerHello + Certificate',
         'Chosen cipher suite, server random, server certificate (X.509)', ORANGE),
        (6.3, '←', '③ Certificate Verify + Finished',
         'Signature over handshake messages, HMAC finished message', RED_ACC),
        (5.5, '→', '④ Client Finished',
         'Client HMAC — handshake authenticated both ways', TEAL),
        (4.6, '↔', '⑤ Application Data (Encrypted)',
         'AEAD cipher (AES-256-GCM / ChaCha20-Poly1305) — all payload encrypted', GREEN),
    ]

    for y, direction, label, sub, color in steps:
        if direction == '→':
            ax.annotate('', xy=(8.0, y), xytext=(2.0, y),
                        arrowprops=dict(arrowstyle='->', color=color, lw=2))
            ax.text(5, y+0.18, label, ha='center', va='bottom',
                    fontsize=9, fontweight='bold', color=color)
            ax.text(5, y-0.18, sub, ha='center', va='top',
                    fontsize=7, color=LIGHT_TXT, alpha=0.85)
        elif direction == '←':
            ax.annotate('', xy=(2.0, y), xytext=(8.0, y),
                        arrowprops=dict(arrowstyle='->', color=color, lw=2))
            ax.text(5, y+0.18, label, ha='center', va='bottom',
                    fontsize=9, fontweight='bold', color=color)
            ax.text(5, y-0.18, sub, ha='center', va='top',
                    fontsize=7, color=LIGHT_TXT, alpha=0.85)
        else:
            ax.annotate('', xy=(8.0, y), xytext=(2.0, y),
                        arrowprops=dict(arrowstyle='<->', color=color, lw=2.5))
            ax.text(5, y+0.18, label, ha='center', va='bottom',
                    fontsize=9, fontweight='bold', color=color)
            ax.text(5, y-0.18, sub, ha='center', va='top',
                    fontsize=7, color=LIGHT_TXT, alpha=0.85)

    # Key derivation note box
    kd = FancyBboxPatch((0.3, 0.9), 9.4, 0.65,
                        boxstyle='round,pad=0.1', linewidth=1.5,
                        edgecolor=PURPLE, facecolor='#16164A')
    ax.add_patch(kd)
    ax.text(5, 1.23, 'Session Keys derived from: ClientRandom + ServerRandom + (EC)DHE shared secret  →  '
                     'HKDF  →  handshake_secret, master_secret, app_write_key, app_read_key',
            ha='center', va='center', fontsize=7.5, color=YELLOW, fontfamily='monospace')

    savefig('diagram_tls_handshake.png')


# ── Diagram 2: Traditional SSL (No Cloud) ────────────────────────────────────
def traditional_ssl():
    fig, ax = plt.subplots(figsize=(13, 8))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')

    ax.text(6, 7.65, 'Traditional SSL/TLS Certificate — Without Cloud (Self-Managed)',
            ha='center', fontsize=13, fontweight='bold', color=LIGHT_TXT)

    def node(x, y, w, h, title, lines, edge_color, face_color=NAVY):
        rect = FancyBboxPatch((x-w/2, y-h/2), w, h,
                              boxstyle='round,pad=0.12', linewidth=2,
                              edgecolor=edge_color, facecolor=face_color)
        ax.add_patch(rect)
        ax.text(x, y + h/2 - 0.22, title, ha='center', va='top',
                fontsize=8.5, fontweight='bold', color=edge_color)
        for i, line in enumerate(lines):
            ax.text(x, y + h/2 - 0.48 - i*0.22, line, ha='center', va='top',
                    fontsize=7, color=LIGHT_TXT)

    def arrow(x1, y1, x2, y2, label='', color=GREY):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.8))
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx+0.05, my+0.12, label, ha='center', fontsize=7,
                    color=color, fontstyle='italic')

    # Nodes
    node(1.8, 6.2, 2.4, 1.2, 'Domain Owner', ['You own example.com', 'Need HTTPS'], TEAL)
    node(5.5, 6.2, 2.8, 1.2, 'Certificate Authority (CA)',
         ['Let\'s Encrypt / DigiCert', 'Comodo / GlobalSign'], YELLOW)
    node(9.8, 6.2, 2.4, 1.2, 'CSR (Cert Sign Request)',
         ['Private Key generated', 'CSR created with domain'], ORANGE)

    node(1.8, 4.0, 2.4, 1.3, 'Domain Validation',
         ['HTTP file challenge', 'OR DNS TXT record', 'Prove domain ownership'], RED_ACC)
    node(5.5, 4.0, 2.8, 1.3, 'CA Issues Certificate',
         ['Signed X.509 cert', 'cert.pem + chain.pem', 'Valid 90 days (LE) / 1-2 yr'], GREEN)
    node(9.8, 4.0, 2.4, 1.3, 'Install on Server',
         ['Nginx / Apache config', 'ssl_certificate cert.pem', 'ssl_certificate_key key.pem'], PURPLE)

    node(3.5, 1.9, 5.0, 1.3, 'Live HTTPS Traffic',
         ['Browser ←→ TLS Handshake ←→ Server', 'Certificate presented, chain validated',
          'Encrypted session established'], TEAL, '#0A2040')

    node(9.8, 1.9, 2.4, 1.3, 'Manual Renewal',
         ['Every 90 days (Let\'s Encrypt)', 'certbot renew / cron job', 'Or expire → site breaks'], RED_ACC)

    # Arrows
    arrow(3.0, 6.2, 4.1, 6.2, 'Submit CSR', YELLOW)
    arrow(1.8, 5.6, 1.8, 4.65, 'Validate', RED_ACC)
    arrow(4.1, 6.2, 3.0, 6.2, '', YELLOW)
    arrow(6.9, 6.2, 8.6, 6.2, 'Owns key', ORANGE)
    arrow(5.5, 5.6, 5.5, 4.65, 'After validation', GREEN)
    arrow(6.9, 4.0, 8.6, 4.0, 'Download + install', PURPLE)
    arrow(5.5, 3.35, 5.5, 2.55, 'Users connect', TEAL)
    arrow(9.8, 3.35, 9.8, 2.55, '', RED_ACC)

    # Providers legend
    legend_items = [
        (GREEN, "Let's Encrypt — Free, 90-day, automated via ACME/certbot"),
        (YELLOW, 'DigiCert / Comodo / GlobalSign — Paid, 1-2 yr, EV/OV/DV options'),
        (ORANGE, 'Self-signed — Free, not trusted by browsers (dev only)'),
    ]
    for i, (c, txt) in enumerate(legend_items):
        ax.plot(0.3, 0.85 - i*0.28, 's', color=c, markersize=8)
        ax.text(0.55, 0.85 - i*0.28, txt, va='center', fontsize=7.5, color=LIGHT_TXT)

    savefig('diagram_traditional_ssl.png')


# ── Diagram 3: AWS ACM Cloud SSL ─────────────────────────────────────────────
def aws_acm_ssl():
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 14); ax.set_ylim(0, 9)
    ax.axis('off')

    ax.text(7, 8.65, 'AWS ACM — Cloud SSL Certificate Flow',
            ha='center', fontsize=13, fontweight='bold', color=LIGHT_TXT)
    ax.text(7, 8.3, 'Automated issuance, validation, renewal — no private key management',
            ha='center', fontsize=9, color=TEAL, fontstyle='italic')

    def node(x, y, w, h, title, lines, edge_color, face_color=NAVY):
        rect = FancyBboxPatch((x-w/2, y-h/2), w, h,
                              boxstyle='round,pad=0.12', linewidth=2,
                              edgecolor=edge_color, facecolor=face_color)
        ax.add_patch(rect)
        ax.text(x, y + h/2 - 0.22, title, ha='center', va='top',
                fontsize=8.5, fontweight='bold', color=edge_color)
        for i, line in enumerate(lines):
            ax.text(x, y + h/2 - 0.48 - i*0.22, line, ha='center', va='top',
                    fontsize=7, color=LIGHT_TXT)

    def arrow(x1, y1, x2, y2, label='', color=GREY, style='->'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle=style, color=color, lw=1.8))
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my+0.14, label, ha='center', fontsize=7,
                    color=color, fontstyle='italic')

    # Internet user
    node(1.5, 7.4, 2.2, 1.0, 'Internet User', ['Browser / Mobile', 'HTTPS request'], TEAL)

    # Route 53
    node(4.5, 7.4, 2.2, 1.0, 'Amazon Route 53', ['DNS Resolution', 'CNAME validation record'], YELLOW)

    # ACM
    node(8, 7.4, 3.0, 1.0, 'AWS Certificate Manager (ACM)',
         ['Issues certificate', 'Auto-renews, stores private key'], RED_ACC)

    # ACM CA / Amazon Trust
    node(11.8, 7.4, 2.2, 1.0, 'Amazon Trust\nServices CA',
         ['Root CA / Int. CA', 'Signs ACM certs'], ORANGE)

    # ALB
    node(4.5, 5.4, 2.8, 1.3, 'Application Load Balancer',
         ['TLS Termination here', 'ACM cert attached to listener', 'HTTPS :443 → HTTP :80 backend'], PURPLE)

    # EC2 / ECS / Lambda
    node(8.5, 5.4, 2.8, 1.3, 'Backend (EC2 / ECS / Lambda)',
         ['Receives plain HTTP', 'No cert management needed', 'Private subnet — not exposed'], GREEN)

    # Private link note
    node(4.5, 3.3, 5.8, 1.1, 'ACM Private CA (optional)',
         ['For internal/private services', 'VPC-internal TLS, mTLS', 'Custom root CA'], GREY, '#1A1A3E')

    # Traffic flow at bottom
    rect = FancyBboxPatch((0.5, 1.0), 13, 1.6,
                          boxstyle='round,pad=0.1', linewidth=1.5,
                          edgecolor=TEAL, facecolor='#0A2040')
    ax.add_patch(rect)
    ax.text(7, 2.38, 'End-to-End Traffic Flow', ha='center', fontsize=9,
            fontweight='bold', color=TEAL)
    flows = [
        ('User types https://example.com', '→', 'Route 53 returns ALB DNS name', YELLOW),
        ('Browser connects to ALB :443', '→', 'ALB presents ACM certificate', RED_ACC),
        ('TLS Handshake completes', '→', 'ALB forwards plain HTTP to EC2', GREEN),
    ]
    for i, (a, arr, b, c) in enumerate(flows):
        y = 2.05 - i*0.3
        ax.text(1.0, y, f'• {a}  →  {b}', va='center', fontsize=7.5, color=c)

    # Arrows
    arrow(2.6, 7.4, 3.4, 7.4, 'DNS Query', YELLOW)
    arrow(5.6, 7.4, 6.5, 7.4, 'Request cert', RED_ACC)
    arrow(9.5, 7.4, 10.7, 7.4, 'Signs cert', ORANGE)
    arrow(4.5, 6.9, 4.5, 6.05, 'CNAME record auto-added\nfor domain validation', YELLOW)
    arrow(2.6, 7.1, 4.1, 5.9, 'HTTPS :443', TEAL)
    arrow(5.85, 5.4, 7.1, 5.4, 'HTTP :80 (private)', GREEN)
    arrow(8, 6.9, 8, 6.05, 'Cert attached\nto ALB HTTPS listener', RED_ACC)

    savefig('diagram_aws_acm_ssl.png')


# ── Diagram 4: Task Architecture ─────────────────────────────────────────────
def task_architecture():
    fig, ax = plt.subplots(figsize=(14, 9.5))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 14); ax.set_ylim(0, 9.5)
    ax.axis('off')

    ax.text(7, 9.15, 'Task Architecture — saistabakers.com with ACM + Route 53 + Apache',
            ha='center', fontsize=13, fontweight='bold', color=LIGHT_TXT)
    ax.text(7, 8.8, 'Domain on Hostinger  →  Route 53 Hosted Zone  →  ACM Certificate  →  HTTPS Apache',
            ha='center', fontsize=9, color=YELLOW, fontstyle='italic')

    def node(x, y, w, h, title, lines, edge_color, face_color=NAVY, title_size=8.5):
        rect = FancyBboxPatch((x-w/2, y-h/2), w, h,
                              boxstyle='round,pad=0.12', linewidth=2,
                              edgecolor=edge_color, facecolor=face_color)
        ax.add_patch(rect)
        ax.text(x, y + h/2 - 0.22, title, ha='center', va='top',
                fontsize=title_size, fontweight='bold', color=edge_color)
        for i, line in enumerate(lines):
            ax.text(x, y + h/2 - 0.48 - i*0.22, line, ha='center', va='top',
                    fontsize=7, color=LIGHT_TXT)

    def arrow(x1, y1, x2, y2, label='', color=GREY):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2))
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            off = 0.16 if x1 != x2 else 0.0
            ax.text(mx + off, my + 0.15, label, ha='center', fontsize=7.5,
                    color=color, fontstyle='italic', fontweight='bold')

    # Step labels on left
    steps_labels = [
        (0.55, 7.6, '① Domain\nRegistrar'),
        (0.55, 5.75, '② Route 53\nHosted Zone'),
        (0.55, 4.05, '③ ACM\nCertificate'),
        (0.55, 2.4, '④ DNS\nValidation'),
        (0.55, 1.0, '⑤ Live\nHTTPS'),
    ]
    for x, y, lbl in steps_labels:
        rect = FancyBboxPatch((x-0.5, y-0.4), 1.0, 0.8,
                              boxstyle='round,pad=0.08', linewidth=1,
                              edgecolor=GREY, facecolor='#16162A')
        ax.add_patch(rect)
        ax.text(x, y, lbl, ha='center', va='center', fontsize=6.5,
                color=GREY, fontweight='bold')

    # Main nodes
    # Row 1: User + Hostinger
    node(3.0, 7.6, 2.4, 1.1, 'Internet User',
         ['Browser: https://saistabakers.com', 'DNS lookup triggered'], TEAL)
    node(6.5, 7.6, 3.0, 1.1, 'Hostinger (Domain Registrar)',
         ['Owns saistabakers.com', 'Nameservers updated → Route 53 NS'], ORANGE)
    node(10.5, 7.6, 3.0, 1.1, 'Route 53 Name Servers',
         ['ns-xxx.awsdns-xx.com (×4)', 'Authoritative DNS for domain'], YELLOW)

    # Row 2: Route 53 Hosted Zone
    node(7, 5.75, 6.5, 1.5, 'Route 53 Hosted Zone — saistabakers.com',
         ['A Record (Simple Routing): saistabakers.com → EC2 Public IP',
          'CNAME Record 1: ACM validation (_abc123.saistabakers.com → acm-validate.aws)',
          'CNAME Record 2: www.saistabakers.com → EC2 or ALB DNS'], YELLOW, '#16162A')

    # Row 3: ACM
    node(3.5, 4.05, 3.2, 1.4, 'AWS Certificate Manager',
         ['Request public certificate', 'Domain: saistabakers.com', 'SANs: *.saistabakers.com',
          'Validation: DNS (CNAME)'], RED_ACC)
    node(8.5, 4.05, 4.0, 1.4, 'Amazon Trust Services CA',
         ['Intermediate CA signs the cert', 'Amazon Root CA 1 / 2 / 3 / 4',
          'Trusted by all major browsers', '13-month validity, auto-renew'], ORANGE)

    # Row 4: DNS Validation
    node(5.0, 2.4, 4.5, 1.3, 'DNS Validation CNAME',
         ['ACM provides a CNAME record:', '_abc123.saistabakers.com',
          '→ _xyz789.acm-validations.aws', 'Proves you control the domain'], GREEN)
    node(10.5, 2.4, 3.0, 1.3, 'Certificate Issued',
         ['Status: Issued ✓', 'Attached to ALB / EC2', 'Auto-renewed before expiry'], GREEN)

    # Row 5: EC2
    node(7, 0.9, 6.5, 1.1, 'EC2 Instance — Apache Web Server',
         ['Apache2 installed, HTTPS enabled via ACM cert on ALB',
          'Security Group: Allow :80 from ALB, :443 from internet, :22 from admin IP'], PURPLE)

    # Arrows
    arrow(4.2, 7.6, 5.0, 7.6, 'NS lookup', YELLOW)
    arrow(8.0, 7.6, 9.0, 7.6, 'Delegates to', YELLOW)
    arrow(6.5, 7.05, 6.5, 6.55, 'Reads NS records', ORANGE)
    arrow(10.5, 7.05, 9.25, 6.55, 'Answers DNS', YELLOW)
    arrow(3.5, 5.05, 3.5, 4.8, '', RED_ACC)
    arrow(3.5, 7.05, 3.5, 6.6, 'HTTPS req', TEAL)
    arrow(3.0, 7.05, 3.0, 5.55, '', TEAL)
    arrow(5.1, 4.05, 6.5, 4.05, 'CA signs', ORANGE)
    arrow(3.5, 3.35, 5.0, 2.95, 'Generates CNAME', GREEN)
    arrow(7.25, 2.4, 9.0, 2.4, 'Validates OK', GREEN)
    arrow(10.5, 3.75, 10.5, 3.05, '→ Issued', GREEN)
    arrow(7, 1.9, 7, 1.45, 'Traffic', PURPLE)
    arrow(9.0, 2.1, 8.5, 1.45, 'Cert attached', RED_ACC)

    # Legend
    legend = [
        (TEAL, 'User HTTPS traffic flow'),
        (YELLOW, 'DNS resolution path'),
        (RED_ACC, 'ACM certificate issuance'),
        (GREEN, 'DNS validation + cert issued'),
    ]
    for i, (c, lbl) in enumerate(legend):
        ax.plot(0.4, 0.55 - i*0.0, '', alpha=0)  # spacer
    rect = FancyBboxPatch((0.15, -0.05), 3.5, 0.55,
                          boxstyle='round,pad=0.05', linewidth=1,
                          edgecolor=GREY, facecolor='#16162A')
    ax.add_patch(rect)
    for i, (c, lbl) in enumerate(legend):
        ax.plot(0.35, 0.4 - i*0.13, 's', color=c, markersize=7)
        ax.text(0.55, 0.4 - i*0.13, lbl, va='center', fontsize=6.5, color=LIGHT_TXT)

    savefig('diagram_task_architecture.png')


# ── Diagram 5: Certificate Chain ─────────────────────────────────────────────
def cert_chain():
    fig, ax = plt.subplots(figsize=(11, 7))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 11); ax.set_ylim(0, 7)
    ax.axis('off')

    ax.text(5.5, 6.65, 'X.509 Certificate Chain of Trust',
            ha='center', fontsize=13, fontweight='bold', color=LIGHT_TXT)

    def cbox(x, y, w, h, title, lines, ec, fc=NAVY):
        rect = FancyBboxPatch((x-w/2, y-h/2), w, h,
                              boxstyle='round,pad=0.12', linewidth=2.5,
                              edgecolor=ec, facecolor=fc)
        ax.add_patch(rect)
        ax.text(x, y + h/2 - 0.22, title, ha='center', va='top',
                fontsize=9, fontweight='bold', color=ec)
        for i, l in enumerate(lines):
            ax.text(x, y + h/2 - 0.50 - i*0.24, l, ha='center', va='top',
                    fontsize=7.5, color=LIGHT_TXT)

    def arrow(x1, y1, x2, y2, label=''):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=GREY, lw=2))
        if label:
            ax.text((x1+x2)/2 + 0.3, (y1+y2)/2, label, ha='center',
                    fontsize=7.5, color=GREY, fontstyle='italic')

    cbox(5.5, 5.6, 5.5, 1.2, 'Root CA Certificate',
         ['Self-signed, pre-installed in OS/browser trust store',
          'Example: ISRG Root X1 (Let\'s Encrypt), Amazon Root CA 1'],
         YELLOW, '#2A2A10')

    cbox(5.5, 3.85, 5.5, 1.3, 'Intermediate CA Certificate',
         ['Signed by Root CA. Used to issue end-entity certs.',
          'Example: R10, R11 (Let\'s Encrypt)  |  Amazon RSA 2048 M01 (ACM)'],
         ORANGE, '#2A1A00')

    cbox(5.5, 2.0, 5.5, 1.5, 'End-Entity (Leaf) Certificate',
         ['Your domain certificate — issued to saistabakers.com',
          'Contains: Subject, SAN, Public Key, Validity period',
          'Signed by Intermediate CA'],
         GREEN, '#0A2A0A')

    cbox(2.5, 0.55, 4.0, 0.7, 'Browser Verification',
         ['Walks chain: Leaf → Intermediate → Root → Trusted ✓'], TEAL, '#0A2020')
    cbox(8.5, 0.55, 4.0, 0.7, 'If Chain Incomplete',
         ['Browser: NET::ERR_CERT_AUTHORITY_INVALID ✗'], RED_ACC, '#2A0A0A')

    arrow(5.5, 5.0, 5.5, 4.5, 'Signs')
    arrow(5.5, 3.2, 5.5, 2.75, 'Signs')
    arrow(4.0, 1.7, 3.2, 0.9)
    arrow(7.0, 1.7, 7.8, 0.9)

    savefig('diagram_cert_chain.png')


if __name__ == '__main__':
    print('Generating diagrams...')
    tls_handshake()
    traditional_ssl()
    aws_acm_ssl()
    task_architecture()
    cert_chain()
    print('All diagrams generated.')
