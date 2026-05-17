from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

for sec in doc.sections:
    sec.top_margin    = Cm(1.8)
    sec.bottom_margin = Cm(1.8)
    sec.left_margin   = Cm(2.2)
    sec.right_margin  = Cm(2.2)

NAVY   = RGBColor(0x0F,0x34,0x60)
DARK   = RGBColor(0x16,0x21,0x3E)
WHITE  = RGBColor(0xFF,0xFF,0xFF)
RED    = RGBColor(0xE9,0x45,0x60)
PURPLE = RGBColor(0x53,0x34,0x83)
ORANGE = RGBColor(0xE6,0x7E,0x22)
GREEN  = RGBColor(0x27,0xAE,0x60)
GREY   = RGBColor(0x44,0x44,0x44)
GOLD   = RGBColor(0x85,0x64,0x04)
LBLUE  = RGBColor(0x0F,0x34,0x60)

# ── Low-level ─────────────────────────────────────────────────────────────────
def cell_shade(cell, hex_fill):
    tc=cell._tc; tcPr=tc.get_or_add_tcPr()
    for o in tcPr.findall(qn('w:shd')): tcPr.remove(o)
    shd=OxmlElement('w:shd'); shd.set(qn('w:val'),'clear')
    shd.set(qn('w:color'),'auto'); shd.set(qn('w:fill'),hex_fill); tcPr.append(shd)

def para_shade(p, hex_fill):
    pPr=p._p.get_or_add_pPr()
    for o in pPr.findall(qn('w:shd')): pPr.remove(o)
    shd=OxmlElement('w:shd'); shd.set(qn('w:val'),'clear')
    shd.set(qn('w:color'),'auto'); shd.set(qn('w:fill'),hex_fill); pPr.append(shd)

def para_border_left(p, color='0F3460', size='18'):
    pPr=p._p.get_or_add_pPr(); pBdr=OxmlElement('w:pBdr')
    left=OxmlElement('w:left'); left.set(qn('w:val'),'single')
    left.set(qn('w:sz'),size); left.set(qn('w:space'),'4')
    left.set(qn('w:color'),color); pBdr.append(left); pPr.append(pBdr)

def para_border_bottom(p, color='CCCCCC', size='6'):
    pPr=p._p.get_or_add_pPr(); pBdr=OxmlElement('w:pBdr')
    bot=OxmlElement('w:bottom'); bot.set(qn('w:val'),'single')
    bot.set(qn('w:sz'),size); bot.set(qn('w:space'),'1')
    bot.set(qn('w:color'),color); pBdr.append(bot); pPr.append(pBdr)

def sp(p, before=0, after=4):
    p.paragraph_format.space_before=Pt(before)
    p.paragraph_format.space_after=Pt(after)

def rfmt(r, name='Calibri', size=11, bold=False, italic=False, color=None):
    r.font.name=name; r.font.size=Pt(size)
    r.font.bold=bold; r.font.italic=italic
    if color: r.font.color.rgb=color

def inline(p, text, name='Calibri', size=11, bold=False, italic=False, color=None):
    r=p.add_run(text); rfmt(r,name,size,bold,italic,color); return r

def write_inline(p, text, size=11):
    import re
    parts=re.split(r'(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)',text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            inline(p,part[2:-2],size=size,bold=True,color=NAVY)
        elif part.startswith('`') and part.endswith('`'):
            inline(p,part[1:-1],name='Courier New',size=size-1,color=RGBColor(0xC0,0x39,0x2B))
        elif part.startswith('*') and part.endswith('*'):
            inline(p,part[1:-1],size=size,italic=True,color=GREY)
        else:
            inline(p,part,size=size)

# ── Block builders ────────────────────────────────────────────────────────────
def h1(text):
    p=doc.add_paragraph(); sp(p,before=12,after=6)
    para_border_bottom(p,color='E94560',size='12')
    r=p.add_run(text); rfmt(r,size=20,bold=True,color=NAVY); return p

def h2(text):
    p=doc.add_paragraph(); sp(p,before=10,after=4)
    r=p.add_run('  '+text); rfmt(r,size=14,bold=True,color=DARK)
    para_border_left(p,'0F3460','18'); return p

def h3(text):
    p=doc.add_paragraph(); sp(p,before=8,after=3)
    r=p.add_run(text); rfmt(r,size=12,bold=True,color=NAVY); return p

def h4(text):
    p=doc.add_paragraph(); sp(p,before=6,after=2)
    r=p.add_run(text); rfmt(r,size=11,bold=True,color=PURPLE); return p

def body(text, before=0, after=5):
    p=doc.add_paragraph(); sp(p,before=before,after=after)
    write_inline(p,text,size=11); return p

def bullet(text, level=0, before=1, after=2):
    p=doc.add_paragraph(style='List Bullet'); sp(p,before=before,after=after)
    p.paragraph_format.left_indent=Inches(0.25+level*0.2)
    write_inline(p,text,size=11); return p

def numbered(text, before=1, after=2):
    p=doc.add_paragraph(style='List Number'); sp(p,before=before,after=after)
    p.paragraph_format.left_indent=Inches(0.25)
    write_inline(p,text,size=11); return p

def code(text, before=4, after=4):
    p=doc.add_paragraph(); sp(p,before=before,after=after)
    p.paragraph_format.left_indent=Inches(0.2)
    p.paragraph_format.right_indent=Inches(0.2)
    para_shade(p,'1A1A2E')
    r=p.add_run(text); rfmt(r,name='Courier New',size=9,color=RGBColor(0xDC,0xDC,0xDC)); return p

def note(text, before=4, after=4):
    p=doc.add_paragraph(); sp(p,before=before,after=after)
    p.paragraph_format.left_indent=Inches(0.25)
    para_shade(p,'FFF3CD')
    r=p.add_run('  ⚠  '+text); rfmt(r,size=10,italic=True,color=GOLD); return p

def info(text, before=4, after=4):
    p=doc.add_paragraph(); sp(p,before=before,after=after)
    p.paragraph_format.left_indent=Inches(0.25)
    para_shade(p,'E8F4FD')
    r=p.add_run('  ℹ  '+text); rfmt(r,size=10,color=LBLUE); return p

def divider():
    p=doc.add_paragraph(); sp(p,before=4,after=4)
    para_border_bottom(p,color='DDDDDD',size='4'); return p

def tbl(headers, rows, col_widths=None):
    t=doc.add_table(rows=1+len(rows),cols=len(headers))
    t.style='Table Grid'; t.alignment=WD_TABLE_ALIGNMENT.LEFT
    hr=t.rows[0]
    for i,h in enumerate(headers):
        c=hr.cells[i]; c.text=''
        p=c.paragraphs[0]; sp(p,before=2,after=2)
        r=p.add_run(h); rfmt(r,size=10,bold=True,color=WHITE)
        cell_shade(c,'0F3460'); c.vertical_alignment=WD_ALIGN_VERTICAL.CENTER
    for ri,row in enumerate(rows):
        tr=t.rows[ri+1]; fill='F0F4FF' if ri%2==1 else 'FFFFFF'
        for ci,val in enumerate(row):
            c=tr.cells[ci]; c.text=''
            p=c.paragraphs[0]; sp(p,before=2,after=2)
            write_inline(p,str(val),size=10); cell_shade(c,fill)
    if col_widths:
        for i,w in enumerate(col_widths):
            for row in t.rows: row.cells[i].width=Inches(w)
    p=doc.add_paragraph(); sp(p,before=0,after=2); return t

def arch(lines, title=None):
    if title:
        p=doc.add_paragraph(); sp(p,before=6,after=0)
        para_shade(p,'533483')
        r=p.add_run(f'  Architecture — {title}')
        rfmt(r,size=10,bold=True,color=WHITE)
    code('\n'.join(lines),before=0,after=6)

def step_banner(n, title):
    p=doc.add_paragraph(); sp(p,before=8,after=4)
    para_shade(p,'16213E')
    r1=p.add_run(f'  STEP {n} — '); rfmt(r1,size=12,bold=True,color=RED)
    r2=p.add_run(title); rfmt(r2,size=12,bold=True,color=WHITE)

# ═══════════════════════════════════════════════════════════════════════════════
#  COVER
# ═══════════════════════════════════════════════════════════════════════════════
p=doc.add_paragraph(); sp(p,before=0,after=0); para_shade(p,'0F3460')
p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('AWS LOAD BALANCER'); rfmt(r,size=26,bold=True,color=WHITE)

p=doc.add_paragraph(); sp(p,before=0,after=0); para_shade(p,'16213E')
p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('Complete Case Study Documentation  ·  Module: Elastic Load Balancing')
rfmt(r,size=11,color=RGBColor(0xAA,0xCC,0xFF))

p=doc.add_paragraph(); sp(p,before=0,after=10); para_shade(p,'E94560')
p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('Level: Beginner → Production  ·  Includes: ALB  |  NLB  |  GLB  |  Real-World Tasks')
rfmt(r,size=10,bold=True,color=WHITE)

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — WHAT IS A LOAD BALANCER
# ═══════════════════════════════════════════════════════════════════════════════
h1('1. What is a Load Balancer?')

h3('Definition')
body(
    'A **Load Balancer** is a networking service that distributes incoming traffic across multiple '
    'targets (EC2 instances, containers, IP addresses, Lambda functions) in one or more '
    'Availability Zones to ensure:'
)
bullet('**High Availability** — no single point of failure across your infrastructure')
bullet('**Fault Tolerance** — unhealthy servers are automatically removed from rotation')
bullet('**Scalability** — handles growing traffic by spreading load across many servers')
bullet('**Reliability** — consistent performance even during failures or traffic spikes')

body(
    'Without a load balancer, all traffic hits a single server. When that server becomes '
    'overloaded or crashes, your entire application goes down. A load balancer acts as the '
    'single entry point for all traffic and intelligently spreads requests across healthy '
    'servers — making your architecture production-grade and enterprise-ready.'
)

arch([
    '  WITHOUT LOAD BALANCER              WITH LOAD BALANCER',
    '',
    '  All Users ──────────────────┐      All Users',
    '                              │           │',
    '                         [Server]    [Load Balancer]',
    '                      Overloaded!    /     |      \\',
    '                      Crashes!    [S1]   [S2]   [S3]',
    '                                Healthy Healthy Healthy',
    '',
    '  Result: Single point of failure    Result: HA · Scalable · Fault Tolerant',
], title='Why You Need a Load Balancer')

divider()

# ── Real-World Analogy ────────────────────────────────────────────────────────
h3('Real-World Analogy')

p=doc.add_paragraph(); sp(p,before=0,after=0); para_shade(p,'FFF3CD')
r=p.add_run('  Imagine a restaurant with multiple billing counters.'); rfmt(r,size=11,italic=True,color=GOLD)

p=doc.add_paragraph(); sp(p,before=0,after=0); para_shade(p,'FFF3CD')
r=p.add_run(
    '  A manager stands at the entrance and sends customers to the counter with the shortest queue.'
); rfmt(r,size=11,italic=True,color=GOLD)

p=doc.add_paragraph(); sp(p,before=0,after=0); para_shade(p,'FFF3CD')
r=p.add_run('  That manager is exactly like a Load Balancer.'); rfmt(r,size=11,bold=True,color=RGBColor(0x8B,0x45,0x13))

p=doc.add_paragraph(); sp(p,before=0,after=6); para_shade(p,'FFF3CD')
r=p.add_run('  '); rfmt(r,size=4)

body('**Result:**')
bullet('No single counter gets overloaded')
bullet('Customers are served faster')
bullet('If one counter fails, others continue working')

arch([
    '  RESTAURANT ANALOGY',
    '',
    '  Customers (Users/Traffic)',
    '         |',
    '   [Manager = Load Balancer]',
    '    /      |       \\',
    '[Counter1] [Counter2] [Counter3]   ← Backend Servers',
    '',
    '  Manager logic: send to shortest queue = least connections algorithm',
    '  If Counter2 breaks: Manager stops sending customers there (health check)',
], title='Restaurant Analogy')

divider()

# ── Key Benefits ──────────────────────────────────────────────────────────────
h3('Key Benefits of Load Balancers')

tbl(
    ['#', 'Benefit', 'Description'],
    [
        ['1', '**High Availability**',        'Distributes traffic across multiple Availability Zones'],
        ['2', '**Fault Tolerance**',           'Stops sending traffic to unhealthy servers automatically'],
        ['3', '**Scalability**',               'Handles increasing traffic automatically with Auto Scaling'],
        ['4', '**Security**',                  'Backend servers are hidden behind the load balancer'],
        ['5', '**Health Checks**',             'Continuously monitors target health and removes unhealthy ones'],
        ['6', '**SSL/TLS Termination**',       'Offloads HTTPS encryption/decryption from backend servers'],
        ['7', '**Better Performance**',        'Prevents server overload by distributing CPU and memory load'],
        ['8', '**Zero-Downtime Deploys**',     'Drain one server, update it, re-register — users notice nothing'],
    ],
    col_widths=[0.3, 2.0, 4.2]
)

divider()

# ── ELB Family ────────────────────────────────────────────────────────────────
h1('2. AWS Elastic Load Balancing (ELB) Family')

arch([
    '  ┌──────────────────────────────────────────────────────────────────┐',
    '  │               AWS Elastic Load Balancing (ELB)                   │',
    '  ├──────────────────────┬───────────────────────┬───────────────────┤',
    '  │         ALB          │          NLB          │        GLB        │',
    '  │  Application LB      │      Network LB       │    Gateway LB     │',
    '  │      Layer 7         │       Layer 4         │      Layer 3      │',
    '  │    HTTP/HTTPS        │    TCP/UDP/TLS         │    IP Traffic     │',
    '  └──────────────────────┴───────────────────────┴───────────────────┘',
], title='ELB Family Overview')

h3('Comparison: ALB vs NLB vs GLB')
tbl(
    ['Feature', 'ALB (Layer 7)', 'NLB (Layer 4)', 'GLB (Layer 3)'],
    [
        ['OSI Layer',         'Layer 7 — Application', 'Layer 4 — Transport', 'Layer 3 — Network'],
        ['Protocols',         'HTTP, HTTPS, WebSocket, gRPC', 'TCP, UDP, TLS', 'IP (all protocols)'],
        ['Routing Logic',     'Path, Host, Headers, Query String', 'Port-based only', 'Flow Hash'],
        ['Latency',           'Moderate', 'Ultra-low (microseconds)', 'Low'],
        ['Source IP',         'Not preserved (use X-Forwarded-For)', 'Preserved natively', 'Preserved'],
        ['Security Groups',   'Yes — on the ALB itself', 'No — only on backend EC2', 'No'],
        ['SSL Termination',   'Yes', 'Yes (also TLS passthrough)', 'No'],
        ['Static IP',         'No (DNS only)', 'Yes — Elastic IP per AZ', 'Yes'],
        ['Best Use Case',     'Web apps, APIs, microservices', 'Banking, gaming, IoT, TCP apps', 'Firewall / IDS / IPS appliances'],
    ],
    col_widths=[1.7, 1.8, 1.8, 1.8]
)

h3('Application Load Balancer (ALB) — Layer 7')
body(
    'ALB is the most feature-rich load balancer. It reads the actual **content** of HTTP requests '
    'and makes intelligent routing decisions based on URL path, hostname, HTTP headers, '
    'query strings, and source IP.'
)
bullet('**Path-based routing** — `/api/*` routes to API servers, `/images/*` routes to media servers')
bullet('**Host-based routing** — `app.example.com` and `admin.example.com` route to different clusters')
bullet('**WAF integration** — attach AWS Web Application Firewall to block attacks at the load balancer')
bullet('**Sticky sessions** — bind a user session to the same backend instance for stateful apps')
bullet('**Authentication** — integrate with Amazon Cognito or OIDC providers for login-protected routes')

h3('Network Load Balancer (NLB) — Layer 4')
body(
    'NLB operates at the transport layer, forwarding raw TCP/UDP packets without reading application content. '
    'It delivers **extreme performance**: millions of requests per second, single-digit millisecond latency, '
    'and native source IP preservation.'
)
bullet('**Source IP preservation** — backend sees real client IP natively, not the LB IP')
bullet('**Static Elastic IP** — one fixed public IP per AZ, ideal for IP whitelisting by partners or banks')
bullet('**TLS passthrough** — can forward encrypted TLS traffic without decrypting it at the LB')
bullet('**No security group on NLB** — all filtering is done at backend EC2 security groups')

h3('Gateway Load Balancer (GLB) — Layer 3')
body(
    'GLB is a specialised load balancer for routing traffic through third-party virtual network '
    'appliances — firewalls, intrusion detection systems, deep packet inspection tools — '
    'before it reaches your application. Used in advanced enterprise security architectures.'
)

divider()

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — NLB TASK
# ═══════════════════════════════════════════════════════════════════════════════
h1('3. Task — AWS Network Load Balancer (NLB) Implementation')

p=doc.add_paragraph(); sp(p,before=0,after=6); para_shade(p,'533483')
p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('  Real-World Banking TCP Gateway Scenario  ')
rfmt(r,size=12,bold=True,color=WHITE)

# ── Scenario ──────────────────────────────────────────────────────────────────
h2('Scenario')
body(
    'This demo demonstrates a real-world TCP-based banking gateway architecture where:'
)
bullet('Application Load Balancer (ALB) cannot be used')
bullet('Network Load Balancer (NLB) is required')
bullet('Raw TCP traffic is load balanced')
bullet('Health checks and failover are demonstrated')

body('**ALB only supports:**')
bullet('HTTP')
bullet('HTTPS')
bullet('WebSocket')
bullet('gRPC')

body('**Our application uses:**')
bullet('Raw TCP traffic on port 9000')

info('Therefore: ALB cannot support this architecture. NLB is required.')

body('**NLB works at:**')
body('Layer 4 (Transport Layer)')
body('**and supports:**')
bullet('TCP')
bullet('UDP')
bullet('TLS')

arch([
    '  WHY NLB AND NOT ALB',
    '',
    '  ┌──────────────────────────┬──────────────────────────┐',
    '  │   ALB Supports           │   Our Banking App Uses   │',
    '  ├──────────────────────────┼──────────────────────────┤',
    '  │   HTTP                   │   Raw TCP port 9000  ✗   │',
    '  │   HTTPS                  │   Raw TCP port 9000  ✗   │',
    '  │   WebSocket              │   Raw TCP port 9000  ✗   │',
    '  │   gRPC                   │   Raw TCP port 9000  ✗   │',
    '  └──────────────────────────┴──────────────────────────┘',
    '',
    '  NLB Supports TCP ✓  →  NLB is the ONLY correct choice here',
], title='ALB vs NLB Protocol Comparison')

divider()

# ── Architecture Flow ─────────────────────────────────────────────────────────
h2('Architecture Flow')
arch([
    '  ATM Client (EC2)',
    '        |',
    '        |  TCP : 9000',
    '        ▼',
    '  Network Load Balancer (TCP : 9000)',
    '        |',
    '  ──────────────────────────────────',
    '  |                                |',
    '  ▼                                ▼',
    'banking-core-1              banking-core-2',
    'EC2 Instance                EC2 Instance',
    'TCP Banking Server          TCP Banking Server',
    'AZ: ap-south-1a             AZ: ap-south-1b',
    '10.0.1.101                  10.0.2.102',
], title='NLB Banking Gateway Architecture Flow')

divider()

# ── Steps ─────────────────────────────────────────────────────────────────────
h2('Step-by-Step Implementation')

# STEP 1
step_banner(1, 'CREATE VPC')
tbl(
    ['Setting', 'Value'],
    [['VPC Name', 'Banking-VPC'], ['CIDR', '10.0.0.0/16']],
    col_widths=[2.5, 4.0]
)
arch([
    '  ┌─────────────────────────────────────┐',
    '  │  Banking-VPC                        │',
    '  │  CIDR: 10.0.0.0/16                  │',
    '  │                                     │',
    '  │  Will contain all subnets,          │',
    '  │  EC2s, NLB, and route tables        │',
    '  └─────────────────────────────────────┘',
], title='VPC')

# STEP 2
step_banner(2, 'CREATE PUBLIC SUBNETS')
tbl(
    ['Subnet Name', 'CIDR', 'Availability Zone'],
    [
        ['Public-Subnet-A', '10.0.1.0/24', 'ap-south-1a'],
        ['Public-Subnet-B', '10.0.2.0/24', 'ap-south-1b'],
    ],
    col_widths=[2.0, 2.0, 2.5]
)
arch([
    '  Banking-VPC (10.0.0.0/16)',
    '  ┌──────────────────┬──────────────────┐',
    '  │  Public-Subnet-A │  Public-Subnet-B │',
    '  │  10.0.1.0/24     │  10.0.2.0/24     │',
    '  │  ap-south-1a     │  ap-south-1b     │',
    '  └──────────────────┴──────────────────┘',
], title='Public Subnets across Two AZs')

# STEP 3
step_banner(3, 'CREATE INTERNET GATEWAY')
tbl(
    ['Setting', 'Value'],
    [
        ['Internet Gateway Name', 'Banking-IGW'],
        ['Attach to', 'Banking-VPC'],
    ],
    col_widths=[2.5, 4.0]
)
arch([
    '  Internet',
    '     |',
    '  Banking-IGW  ←── Attached to Banking-VPC',
    '     |',
    '  Banking-VPC',
    '  (enables inbound/outbound internet for public subnets)',
], title='Internet Gateway')

# STEP 4
step_banner(4, 'CREATE ROUTE TABLE')
body('**Route:**')
tbl(
    ['Destination', 'Target'],
    [['10.0.0.0/16', 'local'], ['0.0.0.0/0', 'Banking-IGW (Internet Gateway)']],
    col_widths=[2.5, 4.0]
)
body('**Associate Route Table With:**')
bullet('Public-Subnet-A')
bullet('Public-Subnet-B')
arch([
    '  Public Route Table (Public-Route-Table)',
    '  ┌────────────────────────────────────┐',
    '  │  Destination    Target             │',
    '  │  10.0.0.0/16    local              │',
    '  │  0.0.0.0/0      Banking-IGW        │',
    '  └──────────┬─────────────────────────┘',
    '             |',
    '    ┌────────┴────────┐',
    '  Subnet-A         Subnet-B',
    '  (10.0.1.0/24)    (10.0.2.0/24)',
], title='Route Table Associations')

# STEP 5
step_banner(5, 'CREATE SECURITY GROUPS')

h4('1. banking-backend-sg')
body('**Attach To:** banking-core-1  and  banking-core-2')
body('**Inbound Rules:**')
tbl(
    ['Type', 'Port', 'Protocol', 'Source'],
    [
        ['SSH',        '22',   'TCP', 'Your Public IP'],
        ['Custom TCP', '9000', 'TCP', '0.0.0.0/0  (For Demo)'],
    ],
    col_widths=[1.5, 1.0, 1.2, 2.8]
)

h4('2. atm-client-sg')
body('**Attach To:** atm-client')
body('**Inbound Rules:**')
tbl(
    ['Type', 'Port', 'Protocol', 'Source'],
    [['SSH', '22', 'TCP', 'Your Public IP']],
    col_widths=[1.5, 1.0, 1.2, 2.8]
)

h2('Important Note About NLB Security Groups')
body('**Traditionally:**')
body('NLB does NOT use Security Groups.')
body('Traffic filtering is handled at:')
body('**Backend EC2 Security Groups**')

arch([
    '  NLB SECURITY MODEL',
    '',
    '  Internet Traffic',
    '       |',
    '      NLB  ← No Security Group on NLB itself',
    '       |',
    '  ┌────┴─────┐',
    '  |          |',
    'banking-   banking-',
    'core-1     core-2',
    '│banking-  │banking-',
    '│backend-sg│backend-sg',
    '│SSH:22    │SSH:22    ← All filtering here',
    '│TCP:9000  │TCP:9000',
], title='NLB Security Group Architecture')

# STEP 6
step_banner(6, 'CREATE EC2 INSTANCES')
body('**Create 3 Instances:**')
body('**1. banking-core-1** — Backend TCP Banking Server')
body('**2. banking-core-2** — Backend TCP Banking Server')
body('**3. atm-client** — Simulated ATM Client')

h4('Instance Configuration')
tbl(
    ['Setting', 'Value'],
    [
        ['AMI',       'Ubuntu 22.04'],
        ['Instance Type', 't2.micro'],
        ['Public IP', 'Enabled'],
    ],
    col_widths=[2.5, 4.0]
)

h4('Subnet Placement')
tbl(
    ['Instance', 'Subnet'],
    [
        ['banking-core-1', 'Public-Subnet-A'],
        ['banking-core-2', 'Public-Subnet-B'],
        ['atm-client',     'Any Public Subnet'],
    ],
    col_widths=[2.5, 4.0]
)

arch([
    '  Banking-VPC',
    '  ┌──────────────────────┬──────────────────────┐',
    '  │  Public-Subnet-A     │  Public-Subnet-B     │',
    '  │  ap-south-1a         │  ap-south-1b         │',
    '  │                      │                      │',
    '  │  [banking-core-1]    │  [banking-core-2]    │',
    '  │   10.0.1.101         │   10.0.2.102         │',
    '  │   TCP Banking Server │   TCP Banking Server  │',
    '  │                      │                      │',
    '  │  [atm-client]        │                      │',
    '  │   Simulator          │                      │',
    '  └──────────────────────┴──────────────────────┘',
], title='EC2 Instance Placement')

h4('User Data — banking-core-1')
note('Paste this in the User Data field when launching banking-core-1.')
code('''#!/bin/bash

apt update -y
apt install netcat-openbsd -y

cat <<EOF > /home/ubuntu/server1.sh
#!/bin/bash

while true
do
    echo "Connected to Banking Server 1 at Availability Zone A - Transaction Gateway" | nc -l -p 9000 -N
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
systemctl start banking-server1.service''')

h4('User Data — banking-core-2')
note('Paste this in the User Data field when launching banking-core-2.')
code('''#!/bin/bash

apt update -y
apt install netcat-openbsd -y

cat <<EOF > /home/ubuntu/server2.sh
#!/bin/bash

while true
do
    echo "Connected to Banking Server 2 at Availability Zone B - Transaction Gateway" | nc -l -p 9000 -N
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
systemctl start banking-server2.service''')

h4('User Data — atm-client')
code('''#!/bin/bash

apt update -y
apt install netcat-openbsd -y''')

arch([
    '  HOW THE BANKING SERVERS WORK',
    '',
    '  banking-core-1 runs a loop:',
    '  while true:',
    '    listen on TCP port 9000',
    '    when connection arrives → send response string → close',
    '    repeat',
    '',
    '  Response: "Connected to Banking Server 1 at AZ A - Transaction Gateway"',
    '',
    '  netcat (nc) acts as the TCP server — no actual banking app needed for this demo',
], title='Banking Server Logic')

# STEP 7
step_banner(7, 'VERIFY BACKEND SERVERS')
body('SSH into: **atm-client**')

h4('TEST SERVER 1')
code('''nc <BANKING-CORE-1-PUBLIC-IP> 9000

Expected Output:
Connected to Banking Server 1 at Availability Zone A - Transaction Gateway''')

h4('TEST SERVER 2')
code('''nc <BANKING-CORE-2-PUBLIC-IP> 9000

Expected Output:
Connected to Banking Server 2 at Availability Zone B - Transaction Gateway''')

arch([
    '  DIRECT VERIFICATION (before NLB)',
    '',
    '  atm-client ──TCP:9000──▶ banking-core-1 (direct, using public IP)',
    '  atm-client ──TCP:9000──▶ banking-core-2 (direct, using public IP)',
    '',
    '  Both must respond before creating the NLB.',
    '  If no response: check banking-backend-sg has TCP:9000 open.',
], title='Direct Backend Verification')

# STEP 8
step_banner(8, 'CREATE TARGET GROUP')
tbl(
    ['Setting', 'Value'],
    [
        ['Target Group Name',     'banking-tg'],
        ['Target Type',           'Instances'],
        ['Protocol',              'TCP'],
        ['Port',                  '9000'],
        ['Health Check Protocol', 'TCP'],
        ['Health Check Port',     '9000'],
        ['Healthy Threshold',     '3'],
        ['Unhealthy Threshold',   '3'],
        ['Interval',              '10s'],
        ['Timeout',               '6s'],
        ['Register Targets',      'banking-core-1, banking-core-2'],
    ],
    col_widths=[2.5, 4.0]
)
arch([
    '  Target Group: banking-tg',
    '  Protocol: TCP  Port: 9000',
    '',
    '  Health Check → TCP:9000 every 10s',
    '  Healthy after 3 passes, Unhealthy after 3 fails',
    '',
    '  Registered Targets:',
    '  ├── banking-core-1  10.0.1.101  AZ: ap-south-1a',
    '  └── banking-core-2  10.0.2.102  AZ: ap-south-1b',
    '',
    '  NLB will only route to targets showing status: Healthy',
], title='Target Group Configuration')

# STEP 9
step_banner(9, 'CREATE NETWORK LOAD BALANCER')
tbl(
    ['Setting', 'Value'],
    [
        ['Name',             'banking-nlb'],
        ['Scheme',           'Internet-facing'],
        ['Listener Protocol','TCP'],
        ['Listener Port',    '9000'],
        ['Attach Subnets',   'Public-Subnet-A (ap-south-1a), Public-Subnet-B (ap-south-1b)'],
        ['Attach Target Group', 'banking-tg'],
    ],
    col_widths=[2.5, 4.0]
)
body('Wait until status becomes: **Active**')

arch([
    '  NLB: banking-nlb (Internet-facing)',
    '  DNS: banking-nlb-xxxx.elb.ap-south-1.amazonaws.com',
    '',
    '  Listener: TCP:9000 → Forward → banking-tg',
    '',
    '                 NLB',
    '                  │',
    '         ┌────────┴────────┐',
    '         │                 │',
    '    AZ Node A          AZ Node B',
    '   (Elastic IP)       (Elastic IP)',
    '         │                 │',
    '   Subnet-A           Subnet-B',
    '   banking-core-1    banking-core-2',
], title='NLB Structure')

# STEP 10
step_banner(10, 'TEST NLB')
body('Copy: **NLB DNS NAME**')
body('Example: `banking-nlb-xxxx.elb.ap-south-1.amazonaws.com`')
body('FROM atm-client, Run:')
code('''nc <NLB-DNS> 9000

Expected:
Connected to Banking Server 1 ...

Run again:
Connected to Banking Server 2 ...

Traffic gets distributed automatically.''')

arch([
    '  LOAD BALANCING IN ACTION',
    '',
    '  atm-client ──TCP:9000──▶ NLB DNS',
    '                                │',
    '                   ┌────────────┤',
    '                   │            │',
    '  Connection 1 ──▶ banking-core-1   (AZ A)',
    '  Connection 2 ──▶ banking-core-2   (AZ B)',
    '  Connection 3 ──▶ banking-core-1   (AZ A)',
    '  Connection 4 ──▶ banking-core-2   (AZ B)',
    '',
    '  NLB uses flow-hash algorithm to distribute TCP connections',
], title='NLB Traffic Distribution')

# LIVE DEMO
h2('Live Load Balancing Demo')
body('Run:')
code('''while true
do
  nc <NLB-DNS> 9000
  sleep 1
done

Expected Output:
Server 1
Server 2
Server 1
Server 2

This demonstrates:
TCP load balancing in real time.''')

# STEP 11
step_banner(11, 'FAILOVER DEMO')
body('Stop: **banking-core-1**')
body('Wait: 30–40 seconds')
body('Now run again:')
code('''nc <NLB-DNS> 9000

Only:
Server 2

responds.

This demonstrates:
automatic health checks and failover.''')

arch([
    '  FAILOVER SCENARIO',
    '',
    '  NORMAL STATE:              AFTER banking-core-1 STOPS:',
    '',
    '  NLB                        NLB',
    '   ├──▶ core-1  ✓ Healthy     ├──▶ core-1  ✗ Unhealthy (stopped)',
    '   └──▶ core-2  ✓ Healthy     └──▶ core-2  ✓ All traffic goes here',
    '',
    '  Health check fails 3x → NLB removes core-1 from rotation',
    '  Restart core-1 → health check passes 3x → traffic returns',
], title='Automatic Failover')

# STEP 12
step_banner(12, 'SOURCE IP PRESERVATION DEMO')
body('SSH into backend server: **banking-core-1**')
body('Install tcpdump:')
code('sudo apt install tcpdump -y')

body('Start packet capture:')
code('sudo tcpdump -i any port 9000')

body('Open another terminal. SSH into: **atm-client**')
body('Check client private IP:')
code('''hostname -I

Example:
10.0.2.132''')

body('Now connect to NLB:')
code('nc <NLB-DNS> 9000')

body('Observe tcpdump output on backend server.')
body('Example:')
code('''IP 10.0.2.132.54872 > 10.0.1.25.9000

This proves:
NLB preserves the original client IP.''')

arch([
    '  SOURCE IP PRESERVATION — NLB vs ALB',
    '',
    '  NLB (Layer 4):                  ALB (Layer 7):',
    '',
    '  atm-client                      atm-client',
    '  IP: 10.0.2.132                  IP: 10.0.2.132',
    '       |                               |',
    '      NLB (transparent pass-through)  ALB (terminates TCP, re-originates)',
    '       |                               |',
    '  banking-core-1                  banking-core-1',
    '  tcpdump sees: 10.0.2.132 ✓      tcpdump sees: ALB-IP  ✗',
    '  (real client IP preserved)      (must use X-Forwarded-For header)',
    '',
    '  NLB is critical for banking fraud detection and security audit logs',
], title='Source IP Preservation')

divider()

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — IMPORTANT NLB CONCEPTS
# ═══════════════════════════════════════════════════════════════════════════════
h1('4. Important NLB Concepts')

h3('NLB Works at Layer 4')
body('Supports:')
bullet('TCP')
bullet('UDP')
bullet('TLS')

h3('NLB Preserves Source IP')
body('Backend servers can see: **Real Client IP**')
body('Useful in:')
bullet('Banking')
bullet('Fraud Detection')
bullet('Security Logging')

h3('NLB is Built For:')
bullet('Banking Systems')
bullet('Gaming Servers')
bullet('Trading Platforms')
bullet('IoT Applications')
bullet('TCP-Based Applications')
bullet('Ultra-Low Latency Workloads')

tbl(
    ['NLB Characteristic', 'Detail'],
    [
        ['OSI Layer',            'Layer 4 — Transport Layer'],
        ['Protocols Supported',  'TCP, UDP, TLS'],
        ['Latency',              'Ultra-low — single-digit milliseconds'],
        ['Scale',                'Millions of connections per second'],
        ['Source IP',            'Preserved — backend sees real client IP'],
        ['Static IP',            'One Elastic IP per Availability Zone'],
        ['Security Groups',      'None on NLB — filtering at backend EC2 only'],
        ['Health Checks',        'TCP, HTTP, HTTPS — configurable interval'],
        ['TLS Termination',      'Supported OR TLS passthrough to backend'],
        ['Cross-Zone LB',        'Optional — distribute evenly across all AZs'],
        ['zonal Isolation',      'One NLB node per AZ — independent Elastic IPs'],
    ],
    col_widths=[2.5, 4.0]
)

arch([
    '  COMPLETE NLB BANKING ARCHITECTURE — FINAL VIEW',
    '',
    '                    ATM Simulator (atm-client)',
    '                    IP: 10.0.2.132  |  TCP:9000',
    '                              |',
    '                          Internet',
    '                              |',
    '  ┌─────────────── AWS Cloud ap-south-1 ──────────────────┐',
    '  │          Banking-VPC: 10.0.0.0/16                     │',
    '  │                       |                               │',
    '  │      ┌────────────────▼────────────────┐              │',
    '  │      │   Network Load Balancer (NLB)   │              │',
    '  │      │   banking-nlb  TCP:9000          │              │',
    '  │      │   Internet-facing  Multi-AZ      │              │',
    '  │      └────────────┬────────────┬────────┘              │',
    '  │                   |            |                       │',
    '  │  AZ A (ap-south-1a)         AZ B (ap-south-1b)        │',
    '  │  Public-Subnet-A 10.0.1/24  Public-Subnet-B 10.0.2/24 │',
    '  │         |                          |                   │',
    '  │  [banking-core-1]          [banking-core-2]            │',
    '  │   10.0.1.101                10.0.2.102                 │',
    '  │   banking-backend-sg        banking-backend-sg          │',
    '  │   SSH:22  TCP:9000          SSH:22  TCP:9000            │',
    '  │                   ↑                                    │',
    '  │           banking-tg (Target Group)                    │',
    '  │           Health Check: TCP:9000 every 10s             │',
    '  └───────────────────────────────────────────────────────┘',
], title='Final Complete Architecture')

divider()

# ── Closing quote ─────────────────────────────────────────────────────────────
p=doc.add_paragraph(); sp(p,before=10,after=0); para_shade(p,'0F3460')
p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('"Application Load Balancer understands applications.\nNetwork Load Balancer understands network traffic."')
rfmt(r,size=13,bold=True,italic=True,color=WHITE)

p=doc.add_paragraph(); sp(p,before=0,after=0); para_shade(p,'16213E')
p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('Documentation prepared for AWS Load Balancer Case Study Module')
rfmt(r,size=9,color=RGBColor(0xAA,0xCC,0xFF))

doc.save('lb-case-study.docx')
print('Done → lb-case-study.docx')
