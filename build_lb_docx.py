from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# ── Page setup ───────────────────────────────────────────────────────────────
for sec in doc.sections:
    sec.top_margin    = Cm(1.8)
    sec.bottom_margin = Cm(1.8)
    sec.left_margin   = Cm(2.2)
    sec.right_margin  = Cm(2.2)

# ── Colour palette ───────────────────────────────────────────────────────────
NAVY    = RGBColor(0x0F, 0x34, 0x60)
DARK    = RGBColor(0x16, 0x21, 0x3E)
RED     = RGBColor(0xE9, 0x45, 0x60)
PURPLE  = RGBColor(0x53, 0x34, 0x83)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
ORANGE  = RGBColor(0xE6, 0x7E, 0x22)
GREEN   = RGBColor(0x1E, 0x8B, 0x4C)
GREY_FG = RGBColor(0x44, 0x44, 0x44)

# ── Low-level helpers ─────────────────────────────────────────────────────────
def cell_shade(cell, hex_fill):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    # remove old shd
    for old in tcPr.findall(qn('w:shd')):
        tcPr.remove(old)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_fill)
    tcPr.append(shd)

def para_shade(p, hex_fill):
    pPr = p._p.get_or_add_pPr()
    for old in pPr.findall(qn('w:shd')):
        pPr.remove(old)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_fill)
    pPr.append(shd)

def set_para_border_bottom(p, color='CCCCCC', size='6'):
    pPr  = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot  = OxmlElement('w:bottom')
    bot.set(qn('w:val'),   'single')
    bot.set(qn('w:sz'),    size)
    bot.set(qn('w:space'), '1')
    bot.set(qn('w:color'), color)
    pBdr.append(bot)
    pPr.append(pBdr)

def no_space_before(p):
    p.paragraph_format.space_before = Pt(0)

def tight(p, before=0, after=4):
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after  = Pt(after)

# ── Font helpers ──────────────────────────────────────────────────────────────
def run_fmt(run, name='Calibri', size=11, bold=False, italic=False, color=None):
    run.font.name  = name
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color

def inline_run(p, text, name='Calibri', size=11, bold=False, italic=False, color=None):
    r = p.add_run(text)
    run_fmt(r, name, size, bold, italic, color)
    return r

# ── Block builders ────────────────────────────────────────────────────────────
def add_h1(text):
    p = doc.add_paragraph()
    tight(p, before=10, after=6)
    set_para_border_bottom(p, color='E94560', size='12')
    r = p.add_run(text)
    run_fmt(r, size=22, bold=True, color=NAVY)
    return p

def add_h2(text):
    p = doc.add_paragraph()
    tight(p, before=12, after=4)
    # left accent bar via paragraph shading trick — use a bordered para
    r = p.add_run('  ' + text)
    run_fmt(r, size=14, bold=True, color=DARK)
    pPr  = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    left = OxmlElement('w:left')
    left.set(qn('w:val'),   'single')
    left.set(qn('w:sz'),    '18')
    left.set(qn('w:space'), '4')
    left.set(qn('w:color'), '0F3460')
    pBdr.append(left)
    pPr.append(pBdr)
    return p

def add_h3(text):
    p = doc.add_paragraph()
    tight(p, before=8, after=3)
    r = p.add_run(text)
    run_fmt(r, size=12, bold=True, color=NAVY)
    return p

def add_h4(text):
    p = doc.add_paragraph()
    tight(p, before=6, after=2)
    r = p.add_run(text)
    run_fmt(r, size=11, bold=True, color=PURPLE)
    return p

def add_body(text, before=0, after=5):
    p = doc.add_paragraph()
    tight(p, before=before, after=after)
    _write_inline(p, text, size=11)
    return p

def _write_inline(p, text, size=11):
    import re
    parts = re.split(r'(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            inline_run(p, part[2:-2], size=size, bold=True, color=NAVY)
        elif part.startswith('`') and part.endswith('`'):
            inline_run(p, part[1:-1], name='Courier New', size=size-1, color=RGBColor(0xC0,0x39,0x2B))
        elif part.startswith('*') and part.endswith('*'):
            inline_run(p, part[1:-1], size=size, italic=True, color=GREY_FG)
        else:
            inline_run(p, part, size=size)

def add_bullet(text, level=0, before=1, after=2):
    p = doc.add_paragraph(style='List Bullet')
    tight(p, before=before, after=after)
    p.paragraph_format.left_indent = Inches(0.25 + level * 0.2)
    _write_inline(p, text, size=11)
    return p

def add_numbered(text, before=1, after=2):
    p = doc.add_paragraph(style='List Number')
    tight(p, before=before, after=after)
    p.paragraph_format.left_indent = Inches(0.25)
    _write_inline(p, text, size=11)
    return p

def add_code(text, before=4, after=4):
    p = doc.add_paragraph()
    tight(p, before=before, after=after)
    p.paragraph_format.left_indent  = Inches(0.2)
    p.paragraph_format.right_indent = Inches(0.2)
    para_shade(p, '1A1A2E')
    r = p.add_run(text)
    run_fmt(r, name='Courier New', size=9, color=RGBColor(0xDC,0xDC,0xDC))
    return p

def add_note(text, before=4, after=4):
    p = doc.add_paragraph()
    tight(p, before=before, after=after)
    p.paragraph_format.left_indent  = Inches(0.25)
    p.paragraph_format.right_indent = Inches(0.25)
    para_shade(p, 'FFF3CD')
    r = p.add_run('  ' + text)
    run_fmt(r, size=10, italic=True, color=RGBColor(0x85,0x64,0x04))
    return p

def add_info(text, before=4, after=4):
    p = doc.add_paragraph()
    tight(p, before=before, after=after)
    p.paragraph_format.left_indent  = Inches(0.25)
    p.paragraph_format.right_indent = Inches(0.25)
    para_shade(p, 'E8F4FD')
    r = p.add_run('  ' + text)
    run_fmt(r, size=10, color=RGBColor(0x0F,0x34,0x60))
    return p

def add_divider():
    p = doc.add_paragraph()
    tight(p, before=4, after=4)
    set_para_border_bottom(p, color='DDDDDD', size='4')
    return p

def add_table(headers, rows, col_widths=None):
    ncols = len(headers)
    t = doc.add_table(rows=1+len(rows), cols=ncols)
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    # header
    hr = t.rows[0]
    for i, h in enumerate(headers):
        c = hr.cells[i]
        c.text = ''
        p = c.paragraphs[0]
        tight(p, before=2, after=2)
        r = p.add_run(h)
        run_fmt(r, size=10, bold=True, color=WHITE)
        cell_shade(c, '0F3460')
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    # data
    for ri, row in enumerate(rows):
        tr = t.rows[ri+1]
        fill = 'F0F4FF' if ri % 2 == 1 else 'FFFFFF'
        for ci, val in enumerate(row):
            c = tr.cells[ci]
            c.text = ''
            p = c.paragraphs[0]
            tight(p, before=2, after=2)
            _write_inline(p, val, size=10)
            cell_shade(c, fill)
    # col widths
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in t.rows:
                row.cells[i].width = Inches(w)
    p = doc.add_paragraph()
    tight(p, before=0, after=2)
    return t

def add_arch_diagram(lines, title=None):
    """Renders ASCII architecture diagram in styled code block with optional title."""
    if title:
        p = doc.add_paragraph()
        tight(p, before=6, after=2)
        r = p.add_run(f'  Architecture Diagram — {title}')
        run_fmt(r, size=10, bold=True, color=WHITE)
        para_shade(p, '533483')
    add_code('\n'.join(lines), before=0, after=6)

# ═══════════════════════════════════════════════════════════════════════════════
#  DOCUMENT START
# ═══════════════════════════════════════════════════════════════════════════════

# ── Cover banner ─────────────────────────────────────────────────────────────
p = doc.add_paragraph()
tight(p, before=0, after=2)
para_shade(p, '0F3460')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('AWS LOAD BALANCER')
run_fmt(r, size=26, bold=True, color=WHITE)

p = doc.add_paragraph()
tight(p, before=0, after=2)
para_shade(p, '16213E')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Complete Case Study Documentation  ·  Module: Elastic Load Balancing')
run_fmt(r, size=11, color=RGBColor(0xAA,0xCC,0xFF))

p = doc.add_paragraph()
tight(p, before=0, after=10)
para_shade(p, 'E94560')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Level: Beginner → Production  ·  Region: ap-south-1 (Mumbai)')
run_fmt(r, size=10, bold=True, color=WHITE)

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — WHAT IS A LOAD BALANCER
# ═══════════════════════════════════════════════════════════════════════════════
add_h1('1. What is a Load Balancer?')

add_h3('Definition')
add_body(
    'A **Load Balancer** is a fully managed AWS networking service that automatically distributes '
    'incoming application or network traffic across multiple targets — EC2 instances, containers, '
    'IP addresses, or Lambda functions — in one or more Availability Zones.'
)
add_body(
    'Without a load balancer, all traffic hits a single server. When that server becomes '
    'overloaded or goes down, your entire application fails. A load balancer solves this '
    'by acting as the single entry point for all traffic, while intelligently spreading '
    'requests across healthy servers behind the scenes.'
)

add_h3('Why Do We Need a Load Balancer?')
add_body('Consider a production web application serving millions of users. Three problems arise without load balancing:')
add_bullet('**Single Point of Failure** — one server crash = complete outage')
add_bullet('**Traffic Spikes** — a viral moment overwhelms one server while others sit idle')
add_bullet('**Deployment Downtime** — updating software requires taking the server offline')
add_body('A load balancer eliminates all three. It is the cornerstone of every highly available AWS architecture.')

add_h3('Real-World Analogy')
add_info(
    'Think of a busy restaurant with 6 billing counters. A manager stands at the entrance '
    'and guides each customer to the counter with the shortest queue. No counter gets '
    'overwhelmed. If one counter breaks down, the manager simply stops sending customers '
    'there. That manager is your load balancer.'
)
add_bullet('No single server (counter) gets overloaded')
add_bullet('Users (customers) are served faster')
add_bullet('If one server fails, traffic automatically goes to healthy ones')
add_bullet('You can add more servers without users noticing any disruption')

add_h3('Key Benefits')
add_table(
    ['Benefit', 'How It Helps'],
    [
        ['**High Availability**',     'Distributes traffic across multiple Availability Zones — no single point of failure'],
        ['**Fault Tolerance**',       'Health checks detect unhealthy targets and stop routing traffic to them instantly'],
        ['**Scalability**',           'Works seamlessly with Auto Scaling Groups — new instances register automatically'],
        ['**Security**',              'Backend servers are hidden; only the load balancer DNS is publicly exposed'],
        ['**SSL/TLS Termination**',   'Offloads HTTPS encryption/decryption from backend servers (ALB)'],
        ['**Sticky Sessions**',       'Routes the same user to the same backend for stateful applications (ALB)'],
        ['**Better Performance**',    'Prevents any single server from being overwhelmed; distributes CPU/memory load'],
        ['**Zero-Downtime Deploys**', 'Drain connections from one server, update it, re-register — users notice nothing'],
    ],
    col_widths=[2.2, 4.3]
)

# ── Architecture diagram — why LB ────────────────────────────────────────────
add_arch_diagram([
    '  WITHOUT LOAD BALANCER          WITH LOAD BALANCER',
    '',
    '  Users ──────────────────┐      Users',
    '                          │        │',
    '                    [Server]      [Load Balancer]',
    '                   Overloaded!     /     |     \\',
    '                   Single POF   [S1]   [S2]   [S3]',
    '                               Healthy Healthy Healthy',
    '',
    '  Result: Crash under load    Result: HA, Fault-Tolerant, Scalable',
], title='Load Balancer — Before vs After')

add_divider()

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — AWS ELB FAMILY
# ═══════════════════════════════════════════════════════════════════════════════
add_h1('2. AWS Elastic Load Balancing (ELB) Family')

add_body(
    'AWS offers three types of load balancers under the **Elastic Load Balancing (ELB)** service. '
    'Each operates at a different OSI layer and is designed for a specific type of traffic.'
)

add_arch_diagram([
    '  ┌──────────────────────────────────────────────────────────────────────────┐',
    '  │                    AWS Elastic Load Balancing (ELB)                      │',
    '  ├────────────────────────┬─────────────────────────┬───────────────────────┤',
    '  │          ALB           │           NLB           │          GLB          │',
    '  │   Application LB       │      Network LB         │      Gateway LB       │',
    '  │       Layer 7          │        Layer 4          │        Layer 3        │',
    '  │    HTTP / HTTPS        │    TCP / UDP / TLS      │      IP Traffic       │',
    '  │   Path & Host routing  │   Ultra-low latency     │  3rd-party appliances │',
    '  │   WAF, Auth, gRPC      │   Source IP preserved   │   Firewall / IDS/IPS  │',
    '  └────────────────────────┴─────────────────────────┴───────────────────────┘',
], title='ELB Family Overview')

add_h3('Comparison: ALB vs NLB vs GLB')
add_table(
    ['Feature', 'ALB (Layer 7)', 'NLB (Layer 4)', 'GLB (Layer 3)'],
    [
        ['OSI Layer',          'Layer 7 — Application', 'Layer 4 — Transport', 'Layer 3 — Network'],
        ['Protocols',          'HTTP, HTTPS, WebSocket, gRPC', 'TCP, UDP, TLS', 'IP (all protocols)'],
        ['Routing',            'Path, Host, Header, Query', 'Port-based only', 'Flow-based'],
        ['Latency',            'Moderate',     'Ultra-low (microseconds)', 'Low'],
        ['Source IP',          'Not preserved (use X-Forwarded-For)', 'Preserved natively', 'Preserved'],
        ['Security Groups',    'Yes (on ALB)', 'No (on backend EC2 only)', 'No'],
        ['SSL Termination',    'Yes',          'Yes (TLS passthrough too)', 'No'],
        ['Use Case',           'Web apps, APIs, microservices', 'Banking, gaming, IoT, TCP apps', 'Firewall, IDS/IPS appliances'],
        ['Health Checks',      'HTTP/HTTPS',   'TCP/HTTP/HTTPS',            'TCP/HTTP/HTTPS'],
        ['Fixed IP',           'No (DNS only)', 'Yes (Elastic IP per AZ)',  'Yes'],
    ],
    col_widths=[1.8, 1.8, 1.8, 1.8]
)

add_h3('Application Load Balancer (ALB) — Layer 7 Deep Dive')
add_body(
    'ALB is the most feature-rich load balancer. It reads the actual **content** of HTTP requests '
    'and can make intelligent routing decisions based on URL path, hostname, HTTP headers, query strings, '
    'and even the source IP.'
)
add_bullet('**Path-based routing** — `/api/*` → API servers, `/images/*` → media servers')
add_bullet('**Host-based routing** — `app.example.com` → App cluster, `admin.example.com` → Admin cluster')
add_bullet('**Sticky sessions** — bind a user session to a specific backend instance')
add_bullet('**WAF integration** — attach AWS Web Application Firewall to block attacks at the LB')
add_bullet('**Authentication** — integrate with Cognito or OIDC for login-protected endpoints')

add_h3('Network Load Balancer (NLB) — Layer 4 Deep Dive')
add_body(
    'NLB operates at the transport layer, dealing only with TCP/UDP packets — not HTTP content. '
    'It is designed for **extreme performance**: millions of requests per second with single-digit '
    'millisecond latency. It is the right choice when ALB cannot be used.'
)
add_bullet('**Source IP preservation** — backend servers see the real client IP, not the LB IP')
add_bullet('**Static IP** — each AZ gets a fixed Elastic IP (great for IP whitelisting)')
add_bullet('**TLS passthrough** — can forward encrypted traffic without decrypting it')
add_bullet('**No security groups on NLB** — filtering is done at backend EC2 security groups')

add_h3('Gateway Load Balancer (GLB) — Layer 3')
add_body(
    'GLB is a specialised load balancer for routing traffic through third-party virtual network '
    'appliances such as firewalls, intrusion detection systems, and deep packet inspection tools '
    'before it reaches your application. It is used in advanced enterprise security architectures.'
)

add_divider()

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — TASK: NLB BANKING SCENARIO
# ═══════════════════════════════════════════════════════════════════════════════
add_h1('3. Task — NLB Implementation: Real-World Banking TCP Gateway')

# Banner
p = doc.add_paragraph()
tight(p, before=0, after=6)
para_shade(p, '533483')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('  AWS Network Load Balancer  ·  Real-World Banking TCP Gateway Scenario  ')
run_fmt(r, size=11, bold=True, color=WHITE)

add_h3('Scenario Overview')
add_body(
    'ATM machines (clients) connect to the Banking System over **TCP port 9000**. '
    'A Network Load Balancer distributes this raw TCP traffic across banking servers '
    'in multiple Availability Zones for high availability, fault tolerance, and ultra-low latency.'
)
add_body(
    'This scenario specifically requires **NLB** because ALB only supports HTTP, HTTPS, '
    'WebSocket, and gRPC. Our banking application uses **raw TCP on port 9000** — '
    'a protocol ALB cannot handle. NLB operates at Layer 4 (Transport Layer) and '
    'natively supports TCP, UDP, and TLS.'
)

add_h3('Why ALB Cannot Be Used Here')
add_table(
    ['ALB Supports', 'Our App Uses', 'Result'],
    [
        ['HTTP', 'Raw TCP port 9000', '✗ ALB cannot handle raw TCP'],
        ['HTTPS', 'Raw TCP port 9000', '✗ Not HTTP traffic'],
        ['WebSocket', 'Raw TCP port 9000', '✗ Different protocol'],
        ['gRPC', 'Raw TCP port 9000', '✗ gRPC runs over HTTP/2'],
    ],
    col_widths=[1.8, 2.2, 2.5]
)
add_info('Therefore: NLB is the only correct choice. It handles raw TCP at Layer 4 without inspecting application-level content.')

add_h3('Full Architecture Diagram')
add_arch_diagram([
    '                        ATM Simulator (Client)',
    '                        EC2 Instance: 10.0.2.132',
    '                               |',
    '                           Internet',
    '                               |',
    '  ┌────────────── AWS Cloud (ap-south-1) ──────────────────┐',
    '  │            Banking-VPC: 10.0.0.0/16                    │',
    '  │                         |                              │',
    '  │         ┌───────────────▼────────────────┐             │',
    '  │         │    NETWORK LOAD BALANCER (NLB)  │             │',
    '  │         │           TCP : 9000            │             │',
    '  │         │  DNS: banking-nlb-xxxx.elb...   │             │',
    '  │         └──────────┬────────────┬─────────┘             │',
    '  │                    │            │                        │',
    '  │   AZ A (ap-south-1a)           AZ B (ap-south-1b)       │',
    '  │   Public-Subnet-A              Public-Subnet-B           │',
    '  │   10.0.1.0/24                  10.0.2.0/24              │',
    '  │         │                            │                  │',
    '  │  ┌──────▼────────┐         ┌─────────▼──────┐          │',
    '  │  │ banking-core-1│         │ banking-core-2  │          │',
    '  │  │  10.0.1.101   │         │  10.0.2.102     │          │',
    '  │  │ TCP Server    │         │ TCP Server      │          │',
    '  │  │ banking-       │         │ banking-        │          │',
    '  │  │  backend-sg   │         │  backend-sg     │          │',
    '  │  └───────────────┘         └────────────────┘          │',
    '  │                                                         │',
    '  │   Internet Gateway: Banking-IGW                         │',
    '  └─────────────────────────────────────────────────────────┘',
], title='NLB Banking TCP Gateway Architecture')

add_h3('Infrastructure Details')
add_table(
    ['Component', 'Name / Value'],
    [
        ['VPC',              'Banking-VPC  ·  CIDR: 10.0.0.0/16'],
        ['Public Subnet A',  'Public-Subnet-A  ·  10.0.1.0/24  ·  ap-south-1a'],
        ['Public Subnet B',  'Public-Subnet-B  ·  10.0.2.0/24  ·  ap-south-1b'],
        ['Internet Gateway', 'Banking-IGW  →  attached to Banking-VPC'],
        ['Backend SG',       'banking-backend-sg  →  SSH:22 (Your IP), TCP:9000 (0.0.0.0/0)'],
        ['Client SG',        'atm-client-sg  →  SSH:22 (Your IP)'],
        ['NLB',              'banking-nlb  ·  TCP:9000  ·  Internet-facing'],
        ['Target Group',     'banking-tg  ·  TCP:9000  ·  Health Check: TCP'],
        ['Backend 1',        'banking-core-1  ·  10.0.1.101  ·  ap-south-1a'],
        ['Backend 2',        'banking-core-2  ·  10.0.2.102  ·  ap-south-1b'],
        ['ATM Client',       'atm-client  ·  10.0.2.132  ·  EC2 simulator'],
    ],
    col_widths=[2.0, 4.5]
)

add_divider()
add_h2('Step-by-Step Implementation')

# ── Step 1 ────────────────────────────────────────────────────────────────────
add_h3('Step 1 — Create VPC')
add_body('**AWS Console → VPC → Create VPC**')
add_table(
    ['Setting', 'Value'],
    [['VPC Name', 'Banking-VPC'], ['CIDR Block', '10.0.0.0/16'], ['Tenancy', 'Default']],
    col_widths=[2.0, 4.5]
)

# ── Step 2 ────────────────────────────────────────────────────────────────────
add_h3('Step 2 — Create Public Subnets')
add_body('**VPC → Subnets → Create Subnet → Select Banking-VPC**')
add_table(
    ['Subnet Name', 'Availability Zone', 'CIDR Block'],
    [
        ['Public-Subnet-A', 'ap-south-1a', '10.0.1.0/24'],
        ['Public-Subnet-B', 'ap-south-1b', '10.0.2.0/24'],
    ],
    col_widths=[2.0, 2.2, 2.3]
)
add_note('Enable Auto-assign Public IPv4 for both subnets: Actions → Edit Subnet Settings.')

# ── Step 3 ────────────────────────────────────────────────────────────────────
add_h3('Step 3 — Create Internet Gateway')
add_body('**VPC → Internet Gateways → Create Internet Gateway**')
add_table(
    ['Setting', 'Value'],
    [['Name', 'Banking-IGW'], ['Action after creation', 'Actions → Attach to VPC → Banking-VPC']],
    col_widths=[2.5, 4.0]
)

# ── Step 4 ────────────────────────────────────────────────────────────────────
add_h3('Step 4 — Create Route Table')
add_body('**VPC → Route Tables → Create Route Table → Attach to Banking-VPC**')
add_table(
    ['Destination', 'Target'],
    [['10.0.0.0/16', 'local'], ['0.0.0.0/0', 'Banking-IGW']],
    col_widths=[2.5, 4.0]
)
add_body('**Subnet Associations:** Public-Subnet-A, Public-Subnet-B')

add_arch_diagram([
    '  Internet (0.0.0.0/0)',
    '        |',
    '  Banking-IGW  ←── attached to Banking-VPC',
    '        |',
    '  Public Route Table',
    '  ├── 10.0.0.0/16  →  local',
    '  └── 0.0.0.0/0   →  Banking-IGW',
    '        |',
    '  ┌─────┴─────┐',
    '  Subnet-A   Subnet-B',
    '  (10.0.1)   (10.0.2)',
], title='Route Table Flow')

# ── Step 5 ────────────────────────────────────────────────────────────────────
add_h3('Step 5 — Create Security Groups')
add_body('**EC2 → Security Groups → Create Security Group (inside Banking-VPC)**')

add_h4('1. banking-backend-sg  —  Attached to banking-core-1 and banking-core-2')
add_table(
    ['Type', 'Protocol', 'Port', 'Source', 'Purpose'],
    [
        ['SSH',        'TCP', '22',   'Your Public IP', 'Admin access'],
        ['Custom TCP', 'TCP', '9000', '0.0.0.0/0',      'Accept banking traffic from NLB'],
    ],
    col_widths=[1.2, 1.1, 0.8, 1.8, 2.1]
)

add_h4('2. atm-client-sg  —  Attached to atm-client EC2')
add_table(
    ['Type', 'Protocol', 'Port', 'Source', 'Purpose'],
    [['SSH', 'TCP', '22', 'Your Public IP', 'Admin access to ATM simulator']],
    col_widths=[1.2, 1.1, 0.8, 1.8, 2.1]
)

add_note(
    'Important: NLB does NOT use Security Groups. Traffic filtering for NLB is handled '
    'entirely at the backend EC2 Security Groups (banking-backend-sg). This is a key '
    'architectural difference from ALB.'
)

add_arch_diagram([
    '  SECURITY GROUP CHAIN',
    '',
    '  atm-client-sg           banking-backend-sg',
    '  ┌─────────────┐         ┌──────────────────────┐',
    '  │ atm-client  │         │ banking-core-1        │',
    '  │  SSH:22     │         │ banking-core-2        │',
    '  │  (Your IP)  │         │  SSH:22   (Your IP)   │',
    '  └─────────────┘         │  TCP:9000 (0.0.0.0/0) │',
    '                          └──────────────────────┘',
    '                          ↑ NLB has NO security group',
    '                            Backend SG handles all filtering',
], title='Security Group Design')

# ── Step 6 ────────────────────────────────────────────────────────────────────
add_h3('Step 6 — Launch EC2 Instances')
add_body('**EC2 → Launch Instance** (repeat for all 3 instances)')
add_table(
    ['Instance Name', 'Purpose', 'Subnet', 'Security Group', 'Public IP'],
    [
        ['banking-core-1', 'Backend TCP Banking Server', 'Public-Subnet-A', 'banking-backend-sg', 'Enabled'],
        ['banking-core-2', 'Backend TCP Banking Server', 'Public-Subnet-B', 'banking-backend-sg', 'Enabled'],
        ['atm-client',     'Simulated ATM Client',       'Any Public Subnet', 'atm-client-sg',  'Enabled'],
    ],
    col_widths=[1.5, 2.0, 1.6, 1.8, 0.9]
)
add_body('**AMI:** Ubuntu 22.04 LTS  ·  **Instance Type:** t2.micro')

add_h4('User Data — banking-core-1')
add_note('Paste this in the User Data field when launching banking-core-1.')
add_code(
'''#!/bin/bash
apt update -y
apt install netcat-openbsd -y

cat <<EOF > /home/ubuntu/server1.sh
#!/bin/bash
while true
do
    echo "Connected to Banking Server 1 at AZ A - Transaction Gateway" | nc -l -p 9000 -N
done
EOF

chmod +x /home/ubuntu/server1.sh

cat <<EOF > /etc/systemd/system/banking-server1.service
[Unit]
Description=Banking TCP Server 1
After=network.target

[Service]
ExecStart=/home/ubuntu/server1.sh
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable banking-server1.service
systemctl start banking-server1.service'''
)

add_h4('User Data — banking-core-2')
add_note('Paste this in the User Data field when launching banking-core-2.')
add_code(
'''#!/bin/bash
apt update -y
apt install netcat-openbsd -y

cat <<EOF > /home/ubuntu/server2.sh
#!/bin/bash
while true
do
    echo "Connected to Banking Server 2 at AZ B - Transaction Gateway" | nc -l -p 9000 -N
done
EOF

chmod +x /home/ubuntu/server2.sh

cat <<EOF > /etc/systemd/system/banking-server2.service
[Unit]
Description=Banking TCP Server 2
After=network.target

[Service]
ExecStart=/home/ubuntu/server2.sh
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable banking-server2.service
systemctl start banking-server2.service'''
)

add_h4('User Data — atm-client')
add_code(
'''#!/bin/bash
apt update -y
apt install netcat-openbsd -y'''
)

# ── Step 7 ────────────────────────────────────────────────────────────────────
add_h3('Step 7 — Verify Backend Servers Directly')
add_body('SSH into **atm-client** and test each banking server directly before creating the NLB.')
add_code(
'''# Test banking-core-1 directly
nc <BANKING-CORE-1-PUBLIC-IP> 9000
# Expected: Connected to Banking Server 1 at AZ A - Transaction Gateway

# Test banking-core-2 directly
nc <BANKING-CORE-2-PUBLIC-IP> 9000
# Expected: Connected to Banking Server 2 at AZ B - Transaction Gateway'''
)
add_note('Both servers must respond before proceeding. If they do not, check the security groups and user data script execution.')

# ── Step 8 ────────────────────────────────────────────────────────────────────
add_h3('Step 8 — Create Target Group')
add_body('**EC2 → Target Groups → Create Target Group**')
add_table(
    ['Setting', 'Value'],
    [
        ['Name',                  'banking-tg'],
        ['Target Type',           'Instances'],
        ['Protocol',              'TCP'],
        ['Port',                  '9000'],
        ['Health Check Protocol', 'TCP'],
        ['Health Check Port',     '9000'],
        ['Healthy Threshold',     '3'],
        ['Unhealthy Threshold',   '3'],
        ['Interval',              '10 seconds'],
        ['Timeout',               '6 seconds'],
        ['Register Targets',      'banking-core-1, banking-core-2'],
    ],
    col_widths=[2.5, 4.0]
)

add_arch_diagram([
    '  Target Group: banking-tg',
    '  Protocol: TCP  ·  Port: 9000',
    '',
    '  Health Check: TCP:9000 every 10s',
    '  Healthy after:   3 consecutive passes',
    '  Unhealthy after: 3 consecutive fails',
    '',
    '  Registered Targets:',
    '  ├── banking-core-1  (10.0.1.101)  AZ: ap-south-1a',
    '  └── banking-core-2  (10.0.2.102)  AZ: ap-south-1b',
], title='Target Group Configuration')

# ── Step 9 ────────────────────────────────────────────────────────────────────
add_h3('Step 9 — Create Network Load Balancer')
add_body('**EC2 → Load Balancers → Create Load Balancer → Network Load Balancer**')
add_table(
    ['Setting', 'Value'],
    [
        ['Name',             'banking-nlb'],
        ['Scheme',           'Internet-facing'],
        ['Listener Protocol','TCP'],
        ['Listener Port',    '9000'],
        ['Subnets',          'Public-Subnet-A (ap-south-1a), Public-Subnet-B (ap-south-1b)'],
        ['Target Group',     'banking-tg'],
    ],
    col_widths=[2.5, 4.0]
)
add_note('Wait until NLB status becomes Active (1–2 minutes). Copy the DNS name once active.')

# ── Step 10 ────────────────────────────────────────────────────────────────────
add_h3('Step 10 — Test NLB Load Balancing')
add_body('SSH into **atm-client** and connect to the NLB DNS on port 9000.')
add_code(
'''# Single connection test
nc <NLB-DNS-NAME> 9000
# Expected: Connected to Banking Server 1 ...

nc <NLB-DNS-NAME> 9000
# Expected: Connected to Banking Server 2 ...

# Live load balancing loop
while true
do
  nc <NLB-DNS-NAME> 9000
  sleep 1
done

# Expected output:
# Connected to Banking Server 1 at AZ A - Transaction Gateway
# Connected to Banking Server 2 at AZ B - Transaction Gateway
# Connected to Banking Server 1 at AZ A - Transaction Gateway
# ...'''
)

add_arch_diagram([
    '  LIVE LOAD BALANCING FLOW',
    '',
    '  atm-client ──TCP:9000──▶ NLB (banking-nlb)',
    '                                    │',
    '               ┌────────────────────┤',
    '               │                    │',
    '        Request 1 ──▶ banking-core-1 (AZ A)',
    '        Request 2 ──▶ banking-core-2 (AZ B)',
    '        Request 3 ──▶ banking-core-1 (AZ A)',
    '        Request 4 ──▶ banking-core-2 (AZ B)',
    '',
    '  NLB distributes TCP connections in round-robin across AZs',
], title='NLB Traffic Distribution')

# ── Step 11 ────────────────────────────────────────────────────────────────────
add_h3('Step 11 — Failover Demo')
add_body('Demonstrate automatic health check and failover:')
add_numbered('**Stop banking-core-1** (EC2 → Instances → Select → Instance State → Stop)')
add_numbered('**Wait 30–40 seconds** for NLB health checks to mark it unhealthy')
add_numbered('**Run:** `nc <NLB-DNS> 9000` — observe only **Server 2** responds')
add_numbered('**Start banking-core-1** again — traffic returns to both servers automatically')
add_code(
'''# After stopping banking-core-1:
nc <NLB-DNS> 9000
# Expected: Connected to Banking Server 2 at AZ B - Transaction Gateway
# (Server 1 never responds — NLB has removed it from rotation)'''
)

add_arch_diagram([
    '  FAILOVER SCENARIO',
    '',
    '  NORMAL:                          AFTER banking-core-1 STOPS:',
    '',
    '  NLB                              NLB',
    '   ├──▶ banking-core-1 ✓ Healthy    ├──▶ banking-core-1 ✗ Unhealthy (stopped)',
    '   └──▶ banking-core-2 ✓ Healthy    └──▶ banking-core-2 ✓ Healthy (all traffic here)',
    '',
    '  Traffic → both servers           Traffic → Server 2 only',
    '  (round-robin)                    (automatic failover)',
], title='NLB Automatic Failover')

# ── Step 12 ────────────────────────────────────────────────────────────────────
add_h3('Step 12 — Source IP Preservation Demo')
add_body(
    'Unlike ALB, NLB preserves the **real client IP address**. Backend servers see the '
    'actual ATM client IP — not the NLB IP. This is critical for banking fraud detection '
    'and security logging.'
)
add_code(
'''# On banking-core-1 — install and start packet capture
sudo apt install tcpdump -y
sudo tcpdump -i any port 9000

# On atm-client — check its private IP
hostname -I
# Example output: 10.0.2.132

# On atm-client — connect to NLB
nc <NLB-DNS> 9000

# On banking-core-1 tcpdump — you will see:
# IP 10.0.2.132.54872 > 10.0.1.101.9000
#     ^^^^^^^^^^^
#     Real ATM client IP is visible — NOT the NLB IP'''
)
add_info(
    'This proves NLB Source IP Preservation. With ALB, the backend would see the ALB\'s '
    'IP instead, requiring the X-Forwarded-For header to retrieve the original client IP.'
)

add_arch_diagram([
    '  SOURCE IP PRESERVATION — NLB vs ALB',
    '',
    '  NLB (Layer 4):                   ALB (Layer 7):',
    '',
    '  ATM Client                       ATM Client',
    '  IP: 10.0.2.132                   IP: 10.0.2.132',
    '       |                                |',
    '      NLB                             ALB',
    '  (transparent)                   (terminates TCP)',
    '       |                                |',
    '  banking-core-1                  banking-core-1',
    '  sees: 10.0.2.132 ✓              sees: ALB-IP ✗',
    '  (real client IP preserved)      (need X-Forwarded-For header)',
], title='Source IP Preservation')

add_divider()

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — KEY NLB CONCEPTS
# ═══════════════════════════════════════════════════════════════════════════════
add_h1('4. Key NLB Concepts & Summary')

add_h3('NLB Technical Characteristics')
add_table(
    ['Concept', 'Detail'],
    [
        ['OSI Layer',          'Layer 4 — Transport Layer'],
        ['Supported Protocols','TCP, UDP, TLS'],
        ['Latency',            'Ultra-low — single-digit milliseconds, millions of req/sec'],
        ['Security Groups',    'None on NLB itself — filtering at backend EC2 security groups'],
        ['Source IP',          'Preserved — backend sees real client IP natively'],
        ['Static IP',          'One Elastic IP per AZ — ideal for IP allowlisting'],
        ['Health Checks',      'TCP, HTTP, HTTPS — checks at configurable intervals'],
        ['Cross-Zone LB',      'Optional — can distribute across all AZs evenly'],
        ['TLS Termination',    'Supported — or use TLS passthrough to backend'],
        ['zonal isolation',    'One node per AZ — each AZ node has its own EIP'],
    ],
    col_widths=[2.0, 4.5]
)

add_h3('When to Use NLB')
add_table(
    ['Use Case', 'Why NLB'],
    [
        ['**Banking / Financial Systems**',  'Raw TCP, source IP for fraud detection, ultra-low latency'],
        ['**Gaming Servers**',               'UDP support, millions of concurrent connections, low latency'],
        ['**Trading Platforms**',            'Microsecond-level performance, static IP for compliance'],
        ['**IoT Applications**',             'TCP/UDP protocols, massive connection scale'],
        ['**Firewall IP Whitelisting**',     'Static Elastic IP per AZ — predictable IPs for partner systems'],
        ['**TLS Passthrough**',              'End-to-end encryption without terminating at LB'],
    ],
    col_widths=[2.5, 4.0]
)

add_h3('Final Architecture — Full Traffic Flow')
add_arch_diagram([
    '  USER / ATM CLIENT',
    '  TCP Request on Port 9000',
    '       |',
    '       ▼',
    '  ┌──────────────────────────────┐',
    '  │   Network Load Balancer      │  ← Layer 4, TCP:9000',
    '  │   banking-nlb (Internet-     │  ← Static EIP per AZ',
    '  │   facing, Multi-AZ)          │  ← No security group on NLB',
    '  └──────────┬───────────────────┘',
    '             |',
    '      ┌──────┴──────┐',
    '      |             |',
    '      ▼             ▼',
    ' [banking-tg]  Health Check TCP:9000',
    '      |             |',
    '   ┌──┴──┐      ┌───┴────┐',
    '   | S1  |      |   S2   |     banking-backend-sg',
    '   |AZ-A |      |  AZ-B  |     Port 9000 open',
    '   |10.0.1.101| |10.0.2.102|   Port 22 (Your IP)',
    '   └─────┘      └────────┘',
    '',
    '  SSH ACCESS:',
    '  Your Machine ──SSH:22──▶ banking-core-1 / banking-core-2 (direct, public IP)',
    '  Your Machine ──SSH:22──▶ atm-client (direct, public IP)',
], title='Complete NLB Banking Architecture')

add_divider()

# ── Closing quote ─────────────────────────────────────────────────────────────
p = doc.add_paragraph()
tight(p, before=10, after=4)
para_shade(p, '0F3460')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(
    '"Application Load Balancer understands applications.\n'
    'Network Load Balancer understands network traffic."'
)
run_fmt(r, size=13, bold=True, italic=True, color=WHITE)

p = doc.add_paragraph()
tight(p, before=0, after=0)
para_shade(p, '16213E')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Documentation prepared for AWS Load Balancer Case Study Module')
run_fmt(r, size=9, color=RGBColor(0xAA, 0xCC, 0xFF))

# ── Save ──────────────────────────────────────────────────────────────────────
doc.save('lb-case-study.docx')
print('Done → lb-case-study.docx')
