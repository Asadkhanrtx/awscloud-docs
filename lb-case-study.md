# AWS Load Balancer — Complete Case Study Documentation

> **Module:** Elastic Load Balancing | **Topics:** ALB · NLB · GLB · Path Routing · Host Routing · Query Routing · HTTP Method Routing · NLB→ALB

---

# 1. What is a Load Balancer?

### Definition

A Load Balancer is a networking service that distributes incoming traffic across multiple targets (EC2 instances, containers, IP addresses, Lambda functions) in one or more Availability Zones to ensure:

- High Availability
- Fault Tolerance
- Scalability
- Reliability

---

### Real-World Analogy

> Imagine a restaurant with multiple billing counters.
> A manager stands at the entrance and sends customers to the counter with the **shortest queue**.
> That manager is exactly like a Load Balancer.

**Result:**

- No single counter gets overloaded
- Customers are served faster
- If one counter fails, others continue working

**Architecture — Restaurant = Load Balancer Analogy**

```text
  Customers (Traffic)
         |
  [Manager = Load Balancer]  ← single entry point
   /        |        \
[Counter1] [Counter2] [Counter3]   ← Backend Servers

  If Counter2 breaks → Manager stops sending customers there (health check)
  New counter added → Manager starts sending customers automatically (Auto Scaling)
```

---

### Key Benefits of Load Balancers

| # | Benefit | Description |
| --- | --- | --- |
| 1 | **High Availability** | Distributes traffic across multiple Availability Zones |
| 2 | **Fault Tolerance** | Stops sending traffic to unhealthy servers |
| 3 | **Scalability** | Handles increasing traffic automatically |
| 4 | **Security** | Backend servers are hidden behind the LB |
| 5 | **Health Checks** | Continuously monitors target health |
| 6 | **SSL/TLS Termination** | Offloads HTTPS encryption/decryption |
| 7 | **Better Performance** | Prevents server overload |

---

### AWS Elastic Load Balancing (ELB) Family

**Architecture — ELB Family**

```text
  ┌──────────────────────────────────────────────────────────────┐
  │              AWS Elastic Load Balancing (ELB)               │
  ├──────────────────────┬──────────────────────┬───────────────┤
  │         ALB          │         NLB          │      GLB      │
  │  Application LB      │    Network LB        │  Gateway LB   │
  │      Layer 7         │      Layer 4         │    Layer 3    │
  │    HTTP/HTTPS        │    TCP/UDP/TLS        │   IP Traffic  │
  └──────────────────────┴──────────────────────┴───────────────┘
```

> **Note:** Classic Load Balancer (CLB) is legacy/deprecated. AWS recommends ALB or NLB for new projects.

---

# 2. Application Load Balancer (ALB) — Layer 7

### Definition

An **Application Load Balancer (ALB)** operates at **OSI Layer 7 (Application Layer)**.

It makes routing decisions based on the **content of HTTP/HTTPS requests** such as:

- URL Path
- Hostname
- HTTP Headers
- Query Strings
- HTTP Methods

---

### ALB Key Characteristics

| Feature | Description |
| --- | --- |
| Protocol Support | HTTP, HTTPS, gRPC, WebSocket |
| OSI Layer | Layer 7 (Application Layer) |
| Routing Type | Content-Based Routing |
| Targets Supported | EC2, ECS, Lambda, IP addresses |
| SSL Termination | Supported |
| Sticky Sessions | Supported |
| Health Checks | HTTP/HTTPS path-based |
| Cross-Zone LB | Enabled by default (free) |

---

### ALB Architecture

**Architecture — ALB Content-Based Routing**

```text
                     ┌────────────────────────────────┐
                     │     Application Load Balancer  │
Client ──HTTP/HTTPS─►│             (ALB)              │
                     │  Listener Rules                │
                     │                                │
                     │  IF path = /api/*      ─────►  API Target Group
                     │  IF path = /images/*   ─────►  Image Target Group
                     │  IF host = mobile.*    ─────►  Mobile Target Group
                     │  DEFAULT               ─────►  Web Target Group
                     └────────────────────────────────┘
```

---

### ALB Core Components

| Component | Description |
| --- | --- |
| **Listener** | Checks incoming requests on a specific port |
| **Listener Rule** | Defines how traffic should be routed |
| **Target Group** | Group of backend servers/targets |
| **Health Check** | Monitors target health status |

---

### ALB Listener Rules — One-Line Definitions

| Rule Type | One-Line Definition |
| --- | --- |
| **Path-Based Routing** | Routes traffic based on URL path |
| **Host-Based Routing** | Routes traffic based on domain/hostname |
| **Header-Based Routing** | Routes traffic based on HTTP headers |
| **Query String Routing** | Routes traffic using query parameters |
| **HTTP Method Routing** | Routes based on GET, POST, PUT, DELETE methods |
| **Source IP Routing** | Routes traffic based on client IP range |

---

### ALB Routing Examples

#### 1. Path-Based Routing

```text
example.com/api/*      ───► API Servers
example.com/images/*   ───► Image Servers
example.com/admin/*    ───► Admin Servers
```

#### 2. Host-Based Routing

```text
api.example.com        ───► API Target Group
www.example.com        ───► Web Target Group
admin.example.com      ───► Admin Target Group
```

#### 3. Header-Based Routing

```text
Header: Device=Mobile  ───► Mobile Backend
Header: Device=Web     ───► Web Backend
```

#### 4. Query String Routing

```text
?platform=mobile       ───► Mobile Servers
?version=v2            ───► Version 2 Backend
```

#### 5. HTTP Method Routing

```text
GET Requests           ───► Read Servers
POST Requests          ───► Write Servers
```

#### 6. Source IP Routing

```text
Corporate IP Range     ───► Internal Application
Public Users           ───► Public Backend
```

---

# 3. Internet-Facing ALB vs Internal ALB

## Internet-Facing ALB

### Definition

An **Internet-Facing ALB** has:

- Public IP addresses
- Public DNS name
- Internet accessibility

It receives traffic directly from the internet.

**Architecture — Internet-Facing ALB**

```text
                           INTERNET
                               │
                               ▼
                ┌───────────────────────────┐
                │   Internet-Facing ALB     │
                │  Public IP / Public DNS   │
                │  Deployed in PUBLIC       │
                │  Subnets                  │
                └────────────┬──────────────┘
                             │
      ┌──────────────────────┼──────────────────────┐
      ▼                      ▼                      ▼
┌──────────┐           ┌──────────┐           ┌──────────┐
│  EC2-1   │           │  EC2-2   │           │  EC2-3   │
│ Private  │           │ Private  │           │ Private  │
└──────────┘           └──────────┘           └──────────┘
       Backend instances can remain PRIVATE
```

| Feature | Details |
| --- | --- |
| DNS Name | Resolves to Public IPs |
| ALB Placement | Public Subnets |
| Targets | Usually Private Subnets |
| Security Group | Allow 80/443 from 0.0.0.0/0 |
| Accessed By | Public Internet Users |
| Use Cases | Websites, Public APIs |

---

## Internal ALB

### Definition

An **Internal ALB** has:

- Private IP addresses only
- Private DNS name
- No internet accessibility

Used for internal communication inside a VPC.

**Architecture — Internal ALB in Three-Tier Architecture**

```text
       ┌─────────────────────────┐
       │   Internet-Facing ALB   │
       │     Public Traffic      │
       └──────────┬──────────────┘
                  │
                  ▼
       ┌─────────────────────────┐
       │       Web Tier          │
       │     Frontend EC2        │
       └──────────┬──────────────┘
                  │
                  ▼
       ┌─────────────────────────┐
       │      Internal ALB       │
       │ Private IP / Private DNS│
       │  Deployed in PRIVATE    │
       │        Subnets          │
       └──────────┬──────────────┘
                  │
     ┌────────────┼────────────┐
     ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│ App-1   │  │ App-2   │  │ App-3   │
│ Private │  │ Private │  │ Private │
└─────────┘  └─────────┘  └─────────┘
```

| Feature | Details |
| --- | --- |
| DNS Name | Resolves to Private IPs |
| Placement | Private Subnets |
| Access | Only inside VPC |
| Security Group | Allow VPC CIDR or specific SGs |
| Use Cases | Microservices, Internal APIs |

---

### Internet-Facing ALB vs Internal ALB — Comparison

| Feature | Internet-Facing ALB | Internal ALB |
| --- | --- | --- |
| IP Type | Public IP | Private IP |
| DNS Resolution | Public DNS | Private DNS |
| Subnets | Public | Private |
| Accessible From | Internet + VPC | VPC Only |
| Security Group | 0.0.0.0/0 | VPC CIDR / Specific SG |
| Position | Edge Entry Point | Between Application Tiers |
| Example | www.example.com | order-service.internal |

---

# 4. Network Load Balancer (NLB) — Layer 4

### Definition

A **Network Load Balancer (NLB)** operates at **OSI Layer 4 (Transport Layer)**.

It routes traffic based on:

- IP Address
- TCP/UDP Port

It does NOT inspect request content.

Designed for:

- Ultra High Performance
- Very Low Latency
- Millions of requests per second

---

### NLB Key Characteristics

| Feature | Description |
| --- | --- |
| Protocol Support | TCP, UDP, TLS |
| OSI Layer | Layer 4 |
| Routing Type | IP + Port Based |
| Performance | Millions of requests/sec |
| Latency | Microseconds |
| Static IP | Supported |
| Elastic IP | Supported |
| Preserve Client IP | Yes |
| SSL Termination | Supported |
| Health Checks | TCP/HTTP/HTTPS |

---

### NLB Architecture

**Architecture — NLB Layer 4 Routing**

```text
                        INTERNET
                            │
                            ▼
                ┌────────────────────┐
                │ Network Load       │
                │ Balancer (NLB)     │
                │ Layer 4            │
                │ Static IP          │
                └─────────┬──────────┘
                          │
                          │ Routes using IP + Port
                          │
      ┌───────────────────┼───────────────────┐
      ▼                   ▼                   ▼
 ┌─────────┐         ┌─────────┐         ┌─────────┐
 │ EC2-1   │         │ EC2-2   │         │ EC2-3   │
 │ :8080   │         │ :8080   │         │ :8080   │
 └─────────┘         └─────────┘         └─────────┘
```

---

### Why Static IP in NLB Matters

#### ALB

```text
my-alb-123.elb.amazonaws.com
→ Dynamic IPs
→ IPs can change anytime
→ Use DNS name only
```

#### NLB

```text
52.10.20.30
→ Static IP
→ Never changes
→ Can attach Elastic IP
→ Easy firewall whitelisting
```

---

### ALB vs NLB — Detailed Comparison

| Feature | ALB | NLB |
| --- | --- | --- |
| OSI Layer | Layer 7 | Layer 4 |
| Protocols | HTTP, HTTPS, gRPC, WebSocket | TCP, UDP, TLS |
| Routing | Content-Based | IP + Port |
| Performance | High | Extreme |
| Latency | Milliseconds | Microseconds |
| Static IP | ❌ No | ✅ Yes |
| Elastic IP | ❌ No | ✅ Yes |
| Preserve Client IP | Via X-Forwarded-For | Native |
| SSL Termination | Supported | Supported |
| Sticky Sessions | Cookie-Based | Source IP Based |
| Lambda Support | ✅ Yes | ❌ No |
| ALB as Target | ❌ | ✅ |
| Cross-Zone LB | Enabled by Default | Disabled by Default |
| Security Groups | Supported | Not Supported |

> **Note:** NLB does NOT have Security Groups. The backend EC2 instance sees the real client IP. EC2 Security Group must allow client IP ranges directly — traffic does NOT appear from NLB IPs.

---

## AWS Load Balancer Practice Tasks (ALB + NLB)
> Path-Based Routing · NLB · NLB in Front of ALB

---

### Architecture Overview

**Architecture — ALB + NLB Practice Architecture**

```text
                    INTERNET
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌─────────────────┐         ┌─────────────────┐
│       ALB       │         │       NLB       │
│ Path Routing    │         │ TCP Load Bal.   │
└────────┬────────┘         └────────┬────────┘
         │                            │
 ┌───────┴────────┐         ┌─────────┴────────┐
 ▼                ▼         ▼                  ▼
EC2-App1      EC2-App2   EC2-NLB-1        EC2-NLB-2
/app1         /app2      Red Page         Purple Page
```

---

### Task 1 — Launch EC2-App1 Instance

**Objective:** Create an EC2 instance that serves the `/app1` application.

| Setting | Value |
| --- | --- |
| Name | EC2-App1 |
| AMI | Ubuntu |
| Instance Type | t2.micro |
| VPC | LB-Practice-VPC |
| Subnet | Public-Subnet-1 |
| Public IP | Enabled |
| Security Group | EC2-SG |

#### User Data Script

```text
#!/bin/bash
apt update -y
apt install apache2 -y
systemctl start apache2
systemctl enable apache2
mkdir -p /var/www/html/app1
cat <<EOF > /var/www/html/app1/index.html
<html>
<body style='background-color:#4CAF50; text-align:center;'>
<h1 style='color:white; margin-top:200px;'>Welcome to APP 1 🟢</h1>
<h2 style='color:white;'>This is EC2 - App1 Server</h2>
<h3 style='color:white;'>Path: /app1</h3>
</body>
</html>
EOF
```

---

### Task 2 — Launch EC2-App2 Instance

**Objective:** Create another EC2 instance that serves the `/app2` application.

| Setting | Value |
| --- | --- |
| Name | EC2-App2 |
| AMI | Ubuntu |
| Instance Type | t2.micro |
| Subnet | Public-Subnet-2 |
| Security Group | EC2-SG |

#### User Data Script

```text
#!/bin/bash
apt update -y
apt install apache2 -y
systemctl start apache2
systemctl enable apache2
mkdir -p /var/www/html/app2
cat <<EOF > /var/www/html/app2/index.html
<html>
<body style='background-color:#2196F3; text-align:center;'>
<h1 style='color:white; margin-top:200px;'>Welcome to APP 2 🔵</h1>
<h2 style='color:white;'>This is EC2 - App2 Server</h2>
<h3 style='color:white;'>Path: /app2</h3>
</body>
</html>
EOF
```

---

### Task 3 — Launch EC2-NLB-1 Instance

**Objective:** Create backend server 1 for Network Load Balancer testing.

| Setting | Value |
| --- | --- |
| Name | EC2-NLB-1 |
| AMI | Ubuntu |
| Subnet | Public-Subnet-1 |
| Security Group | EC2-SG |

#### User Data Script

```text
#!/bin/bash
apt update -y
apt install apache2 -y
systemctl start apache2
systemctl enable apache2
cat <<EOF > /var/www/html/index.html
<html>
<body style='background-color:#FF5722; text-align:center;'>
<h1 style='color:white; margin-top:200px;'>NLB Server 1 🔴</h1>
<h2 style='color:white;'>This request was handled by NLB-Server-1</h2>
</body>
</html>
EOF
```

---

### Task 4 — Launch EC2-NLB-2 Instance

**Objective:** Create backend server 2 for Network Load Balancer testing.

| Setting | Value |
| --- | --- |
| Name | EC2-NLB-2 |
| AMI | Ubuntu |
| Subnet | Public-Subnet-2 |
| Security Group | EC2-SG |

#### User Data Script

```text
#!/bin/bash
apt update -y
apt install apache2 -y
systemctl start apache2
systemctl enable apache2
cat <<EOF > /var/www/html/index.html
<html>
<body style='background-color:#9C27B0; text-align:center;'>
<h1 style='color:white; margin-top:200px;'>NLB Server 2 🟣</h1>
<h2 style='color:white;'>This request was handled by NLB-Server-2</h2>
</body>
</html>
EOF
```

---

### Task 5 — Create Target Group for App1

**Objective:** Create a target group for the App1 server.

| Setting | Value |
| --- | --- |
| Target Group Name | TG-App1 |
| Protocol | HTTP |
| Port | 80 |
| Target Type | Instances |
| Health Check Path | /app1/index.html |
| Registered Target | EC2-App1 |

### Task 6 — Create Target Group for App2

**Objective:** Create a target group for the App2 server.

| Setting | Value |
| --- | --- |
| Target Group Name | TG-App2 |
| Protocol | HTTP |
| Port | 80 |
| Target Type | Instances |
| Health Check Path | /app2/index.html |
| Registered Target | EC2-App2 |

---

### Task 7 — Create Application Load Balancer (ALB)

**Objective:** Create an Internet-Facing ALB for path-based routing.

| Setting | Value |
| --- | --- |
| Name | My-ALB |
| Type | Application Load Balancer |
| Scheme | Internet-Facing |
| Protocol | HTTP |
| Port | 80 |
| VPC | LB-Practice-VPC |
| Subnets | Public-Subnet-1 & Public-Subnet-2 |
| Security Group | LB-SG |
| Default Action | Forward traffic to TG-App1 |

---

### Task 8 — Configure Path-Based Routing

**Objective:** Route requests to different target groups based on URL paths.

#### Rule 1 — App1 Routing

| Setting | Value |
| --- | --- |
| Condition Type | Path |
| Path Value | /app1* |
| Action | Forward to TG-App1 |
| Priority | 1 |

#### Rule 2 — App2 Routing

| Setting | Value |
| --- | --- |
| Condition Type | Path |
| Path Value | /app2* |
| Action | Forward to TG-App2 |
| Priority | 2 |

**Architecture — Path-Based Routing Rules**

```text
  ALB Listener Rules (Path-Based):

  Request: http://ALB-DNS/app1   → Rule 1 matches → TG-App1 → EC2-App1 🟢
  Request: http://ALB-DNS/app2   → Rule 2 matches → TG-App2 → EC2-App2 🔵
  Request: http://ALB-DNS/other  → Default rule   → TG-App1
```

---

### Task 9 — Test ALB Path-Based Routing

**Objective:** Verify that ALB routes traffic correctly.

```text
http://ALB-DNS/app1
Expected: Green APP1 page 🟢

http://ALB-DNS/app2
Expected: Blue APP2 page 🔵
```

---

### Task 10 — Create Target Group for NLB

**Objective:** Create target group for Network Load Balancer.

| Setting | Value |
| --- | --- |
| Name | TG-NLB |
| Protocol | TCP |
| Port | 80 |
| Target Type | Instances |
| Health Check | TCP |
| Registered Targets | EC2-NLB-1, EC2-NLB-2 |

---

### Task 11 — Create Network Load Balancer (NLB)

**Objective:** Create an Internet-Facing NLB.

| Setting | Value |
| --- | --- |
| Name | My-NLB |
| Type | Network Load Balancer |
| Scheme | Internet-Facing |
| Protocol | TCP |
| Port | 80 |
| Subnets | Public-Subnet-1 & Public-Subnet-2 |
| Default Action | Forward traffic to TG-NLB |

---

### Task 12 — Test NLB

**Objective:** Verify NLB distributes traffic between servers.

```text
http://NLB-DNS/

Sometimes: NLB Server 1 🔴
Sometimes: NLB Server 2 🟣

Traffic gets distributed automatically across both EC2 instances.
```

**Architecture — NLB Round-Robin Distribution**

```text
  NLB Traffic Distribution:

  Request 1 → EC2-NLB-1  🔴 (Red Page)
  Request 2 → EC2-NLB-2  🟣 (Purple Page)
  Request 3 → EC2-NLB-1  🔴
  Request 4 → EC2-NLB-2  🟣

  NLB uses flow-hash algorithm — same client IP = same server (sticky by default)
```

---

### Task 13 — Configure NLB in Front of ALB

**Objective:** Configure a **Network Load Balancer (NLB)** to forward traffic to an **Application Load Balancer (ALB)** using the special Application Load Balancer Target Type.

This combines:

- NLB → Static IP + High Performance
- ALB → Smart Layer 7 Routing

---

### What is "Application Load Balancer" Target Type?

The **Application Load Balancer Target Type** is a special target type available in NLB Target Groups where the NLB can directly forward traffic to an ALB. AWS automatically manages the ALB IP addresses internally.

#### Old Method vs New Method

|  | Old Method ❌ | New Method ✅ |
| --- | --- | --- |
| Flow | NLB → IP Target Group → Manually add ALB IPs | NLB → ALB Target Group → ALB directly |
| Problem/Benefit | ALB IPs change frequently, manual updates needed | AWS manages IP changes automatically |
| Complexity | Needed Lambda automation | Simple setup |

**Architecture — NLB → ALB: Old vs New Method**

```text
  OLD METHOD (Complex):             NEW METHOD (Simple):

  NLB                               NLB
   │                                 │
   ▼                                 ▼
  IP Target Group                   ALB Target Group
   │                                 │
   ▼                                 ▼
  Manually add ALB IPs        Application Load Balancer
  (IPs change = broken)        (AWS manages IPs internally)
```

#### Step 1 — Create Target Group with ALB Type

**Navigation:** EC2 → Target Groups → Create Target Group

| Setting | Value |
| --- | --- |
| Target Type | Application Load Balancer |
| Name | TG-NLB-to-ALB |
| Protocol | TCP |
| Port | 80 |
| VPC | LB-Practice-VPC |
| Health Check Protocol | HTTP |
| Health Check Path | /app1/index.html |
| Register Target | My-ALB on Port 80 |

#### Step 2 — Update Existing NLB Listener

**Navigation:** EC2 → Load Balancers → My-NLB → Listeners Tab

1. Select TCP : 80 Listener
1. Click Actions → Edit Listener
1. Change Default Action: Forward to TG-NLB-to-ALB
1. Save Changes

#### Step 3 — Test the Architecture

```text
http://NLB-DNS/app1  →  Expected: GREEN APP1 Page 🟢
http://NLB-DNS/app2  →  Expected: BLUE APP2 Page 🔵
```

---

### Complete Request Flow

```text
Step 1: User sends request to NLB DNS
            │
            ▼
Step 2: NLB receives TCP traffic
            │
            ▼
Step 3: NLB forwards traffic to ALB
        (AWS internally manages ALB IPs)
            │
            ▼
Step 4: ALB reads HTTP request content
            │
            ▼
Step 5: ALB applies path-based routing
            │
            ├── /app1 → TG-App1 → EC2-App1 🟢
            │
            └── /app2 → TG-App2 → EC2-App2 🔵
```

**Architecture — NLB → ALB Real World Architecture**

```text
                     INTERNET
                         │
                         ▼
               ┌─────────────────┐
               │       NLB       │
               │  Static Public  │
               │       IP        │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │       ALB       │
               │ Smart Routing   │
               └────────┬────────┘
                        │
      ┌─────────────────┼─────────────────┐
      ▼                 ▼                 ▼
    /api              /web             /admin
      │                 │                 │
   API EC2s         Web EC2s         Admin EC2s
```

### Why This Architecture is Powerful

| NLB Feature | Benefit |
| --- | --- |
| Static IP | Easy firewall whitelisting |
| High Performance | Handles millions of requests |
| Ultra Low Latency | Fast traffic forwarding |

| ALB Feature | Benefit |
| --- | --- |
| Path-Based Routing | Smart traffic distribution |
| Host-Based Routing | Domain-based routing |
| HTTP Awareness | Understands web requests |

---

### Task 14 — Summary — What Was Implemented

```text
✅ Application Load Balancer (ALB)
✅ Path-Based Routing
✅ Network Load Balancer (NLB)
✅ Multi-Server Traffic Distribution
✅ Apache Web Hosting using User Data
✅ NLB → ALB → EC2 Architecture
✅ Static Public Entry Point
✅ Advanced Routing + High Availability
✅ Scalable Infrastructure
✅ Production-Level AWS Design
```

---

## AWS ALB Routing Methods Practice Tasks
> Host-Based · Path-Based · Query String · HTTP Method Routing

---

### All Routing Methods Overview

**Architecture — All ALB Routing Rules**

```text
  ALB Listener Rules
         │
  ┌──────┴──────────────────────────────────────────┐
  │  Rule 1: Host Header = app1.example.com → TG-App1
  │  Rule 2: Host Header = app2.example.com → TG-App2
  │  Rule 3: Path = /api*                  → TG-API
  │  Rule 4: Path = /web*                  → TG-Web
  │  Rule 5: Query platform=mobile         → TG-Mobile
  │  Rule 6: Query platform=desktop        → TG-Desktop
  │  Rule 7: HTTP Method = GET             → TG-GET
  │  Rule 8: HTTP Method = POST            → TG-POST
  └──────────────────────────────────────────────────┘
```

---

### Task 1 — Launch EC2-App1 (Host-Based Routing)

**Objective:** Server for `app1.example.com`

| Setting | Value |
| --- | --- |
| Name | EC2-App1 |
| AMI | Ubuntu |
| Instance Type | t2.micro |
| Subnet | Public-Subnet-1 |
| Security Group | EC2-SG |

#### User Data

```text
#!/bin/bash
apt update -y
apt install apache2 -y
systemctl start apache2
systemctl enable apache2
cat <<EOF > /var/www/html/index.html
<html>
<body style='background-color:#4CAF50; text-align:center;'>
<h1 style='color:white; margin-top:200px;'>🟢 APP 1 Server</h1>
<h2 style='color:white;'>Host: app1.example.com</h2>
</body>
</html>
EOF
```

---

### Task 2 — Launch EC2-App2 (Host-Based Routing)

**Objective:** Server for `app2.example.com`

| Setting | Value |
| --- | --- |
| Name | EC2-App2 |
| AMI | Ubuntu |
| Instance Type | t2.micro |
| Subnet | Public-Subnet-2 |
| Security Group | EC2-SG |

#### User Data

```text
#!/bin/bash
apt update -y
apt install apache2 -y
systemctl start apache2
systemctl enable apache2
cat <<EOF > /var/www/html/index.html
<html>
<body style='background-color:#2196F3; text-align:center;'>
<h1 style='color:white; margin-top:200px;'>🔵 APP 2 Server</h1>
<h2 style='color:white;'>Host: app2.example.com</h2>
</body>
</html>
EOF
```

---

### Task 3 — Launch EC2-API (Path-Based Routing)

**Objective:** Server for `/api`

| Setting | Value |
| --- | --- |
| Name | EC2-API |
| AMI | Ubuntu |
| Instance Type | t2.micro |
| Subnet | Public-Subnet-1 |
| Security Group | EC2-SG |

#### User Data

```text
#!/bin/bash
apt update -y
apt install apache2 -y
systemctl start apache2
systemctl enable apache2
mkdir -p /var/www/html/api
cat <<EOF > /var/www/html/api/index.html
<html>
<body style='background-color:#FF9800; text-align:center;'>
<h1 style='color:white; margin-top:200px;'>🟠 API Server</h1>
<h2 style='color:white;'>Path: /api</h2>
</body>
</html>
EOF
```

---

### Task 4 — Launch EC2-Web (Path-Based Routing)

**Objective:** Server for `/web`

| Setting | Value |
| --- | --- |
| Name | EC2-Web |
| AMI | Ubuntu |
| Instance Type | t2.micro |
| Subnet | Public-Subnet-2 |
| Security Group | EC2-SG |

#### User Data

```text
#!/bin/bash
apt update -y
apt install apache2 -y
systemctl start apache2
systemctl enable apache2
mkdir -p /var/www/html/web
cat <<EOF > /var/www/html/web/index.html
<html>
<body style='background-color:#9C27B0; text-align:center;'>
<h1 style='color:white; margin-top:200px;'>🟣 Web Server</h1>
<h2 style='color:white;'>Path: /web</h2>
</body>
</html>
EOF
```

---

### Task 5 — Launch EC2-Mobile (Query String Routing)

**Objective:** Server for `?platform=mobile`

| Setting | Value |
| --- | --- |
| Name | EC2-Mobile |
| AMI | Ubuntu |
| Instance Type | t2.micro |
| Subnet | Public-Subnet-1 |
| Security Group | EC2-SG |

#### User Data

```text
#!/bin/bash
apt update -y
apt install apache2 -y
systemctl start apache2
systemctl enable apache2
cat <<EOF > /var/www/html/index.html
<html>
<body style='background-color:#E91E63; text-align:center;'>
<h1 style='color:white; margin-top:200px;'>📱 Mobile Server</h1>
<h2 style='color:white;'>You are on Mobile Platform!</h2>
<h3 style='color:white;'>Routed via Query String</h3>
</body>
</html>
EOF
```

---

### Task 6 — Launch EC2-Desktop (Query String Routing)

**Objective:** Server for `?platform=desktop`

| Setting | Value |
| --- | --- |
| Name | EC2-Desktop |
| AMI | Ubuntu |
| Instance Type | t2.micro |
| Subnet | Public-Subnet-2 |
| Security Group | EC2-SG |

#### User Data

```text
#!/bin/bash
apt update -y
apt install apache2 -y
systemctl start apache2
systemctl enable apache2
cat <<EOF > /var/www/html/index.html
<html>
<body style='background-color:#607D8B; text-align:center;'>
<h1 style='color:white; margin-top:200px;'>🖥️ Desktop Server</h1>
<h2 style='color:white;'>You are on Desktop Platform!</h2>
<h3 style='color:white;'>Routed via Query String</h3>
</body>
</html>
EOF
```

---

### Task 7 — Create All Target Groups

| Target Group | EC2 Target | Purpose |
| --- | --- | --- |
| TG-App1 | EC2-App1 | Host-Based Routing |
| TG-App2 | EC2-App2 | Host-Based Routing |
| TG-API | EC2-API | Path-Based Routing |
| TG-Web | EC2-Web | Path-Based Routing |
| TG-Mobile | EC2-Mobile | Query String Routing |
| TG-Desktop | EC2-Desktop | Query String Routing |

---

### Task 8 — Create Application Load Balancer

| Setting | Value |
| --- | --- |
| Name | My-ALB |
| Type | Internet-Facing |
| Protocol | HTTP |
| Port | 80 |
| Security Group | LB-SG |
| Default Action | Forward to TG-Desktop |

---

### Task 9 — Configure Route 53 DNS Records

| Record Name | Points To |
| --- | --- |
| example.com | My-ALB |
| app1.example.com | My-ALB |
| app2.example.com | My-ALB |

> ℹ All DNS records point to the SAME ALB. The ALB reads the Host Header to differentiate between them.

---

### Task 10 — Configure Host-Based Routing Rules

#### Rule 1 — App1

| Setting | Value |
| --- | --- |
| Host Header | app1.example.com |
| Action | Forward to TG-App1 |
| Priority | 1 |

#### Rule 2 — App2

| Setting | Value |
| --- | --- |
| Host Header | app2.example.com |
| Action | Forward to TG-App2 |
| Priority | 2 |

---

### Task 11 — Configure Path-Based Routing Rules

#### API Rule

| Setting | Value |
| --- | --- |
| Path | /api* |
| Action | Forward to TG-API |
| Priority | 3 |

#### Web Rule

| Setting | Value |
| --- | --- |
| Path | /web* |
| Action | Forward to TG-Web |
| Priority | 4 |

---

### Task 12 — Configure Query String Routing Rules

#### Mobile Query Rule

| Setting | Value |
| --- | --- |
| Query Key | platform |
| Query Value | mobile |
| Action | Forward to TG-Mobile |
| Priority | 7 |

#### Desktop Query Rule

| Setting | Value |
| --- | --- |
| Query Key | platform |
| Query Value | desktop |
| Action | Forward to TG-Desktop |
| Priority | 8 |

---

### Task 13 — Launch EC2-GET (HTTP Method Routing)

**Objective:** Handle GET requests.

| Setting | Value |
| --- | --- |
| Name | EC2-GET |
| AMI | Ubuntu |
| Instance Type | t2.micro |
| Subnet | Public-Subnet-1 |
| Security Group | EC2-SG |

#### User Data

```text
#!/bin/bash
apt update -y
apt install apache2 -y
systemctl start apache2
systemctl enable apache2
cat <<EOF > /var/www/html/index.html
<html>
<body style='background-color:#00BCD4; text-align:center;'>
<h1 style='color:white; margin-top:200px;'>📖 GET Server - Read Operations</h1>
<h2 style='color:white;'>You sent a GET Request!</h2>
<h3 style='color:white;'>This server handles READ operations only</h3>
</body>
</html>
EOF
```

---

### Task 14 — Launch EC2-POST (HTTP Method Routing)

**Objective:** Handle POST requests.

| Setting | Value |
| --- | --- |
| Name | EC2-POST |
| AMI | Ubuntu |
| Instance Type | t2.micro |
| Subnet | Public-Subnet-2 |
| Security Group | EC2-SG |

#### User Data

```text
#!/bin/bash
apt update -y
apt install apache2 -y
systemctl start apache2
systemctl enable apache2
cat <<EOF > /var/www/html/index.html
<html>
<body style='background-color:#F44336; text-align:center;'>
<h1 style='color:white; margin-top:200px;'>✏️ POST Server - Write Operations</h1>
<h2 style='color:white;'>You sent a POST Request!</h2>
<h3 style='color:white;'>This server handles WRITE operations only</h3>
</body>
</html>
EOF
```

---

### Task 15 — Create Target Groups for HTTP Method Routing

| Target Group | Purpose |
| --- | --- |
| TG-GET | GET Requests |
| TG-POST | POST Requests |

---

### Task 16 — Configure HTTP Method Routing Rules

#### GET Rule

| Setting | Value |
| --- | --- |
| HTTP Method | GET |
| Action | Forward to TG-GET |
| Priority | 9 |

#### POST Rule

| Setting | Value |
| --- | --- |
| HTTP Method | POST |
| Action | Forward to TG-POST |
| Priority | 10 |

---

### Task 17 — Test Host-Based Routing

```text
http://app1.example.com  →  Expected: GREEN APP1 Page 🟢
http://app2.example.com  →  Expected: BLUE APP2 Page 🔵
```

**Architecture — Host-Based Routing Test**

```text
  app1.example.com ──Host Header──▶ ALB ──Rule 1 matches──▶ TG-App1 → EC2-App1 🟢
  app2.example.com ──Host Header──▶ ALB ──Rule 2 matches──▶ TG-App2 → EC2-App2 🔵
```

---

### Task 18 — Test Path-Based Routing

```text
http://example.com/api  →  Expected: ORANGE API Page 🟠
http://example.com/web  →  Expected: PURPLE WEB Page 🟣
```

**Architecture — Path-Based Routing Test**

```text
  example.com/api ──▶ ALB ──/api* matches (Priority 3)──▶ TG-API → EC2-API 🟠
  example.com/web ──▶ ALB ──/web* matches (Priority 4)──▶ TG-Web → EC2-Web 🟣
```

---

### Task 19 — Test Query String Routing

```text
http://example.com?platform=mobile   →  Expected: PINK Mobile Page 📱
http://example.com?platform=desktop  →  Expected: GREY Desktop Page 🖥️
```

**Architecture — Query String Routing Test**

```text
  ?platform=mobile  ──▶ ALB ──Query matches (Priority 7)──▶ TG-Mobile  → EC2-Mobile  📱
  ?platform=desktop ──▶ ALB ──Query matches (Priority 8)──▶ TG-Desktop → EC2-Desktop 🖥️
```

---

### Task 20 — Test HTTP Method Routing

```text
curl -X GET  http://example.com  →  Expected: GET Server Page 📖
curl -X POST http://example.com  →  Expected: POST Server Page ✏️
```

**Architecture — HTTP Method Routing Test**

```text
  GET  Request ──▶ ALB ──Method=GET  (Priority 9)──▶  TG-GET  → EC2-GET  📖
  POST Request ──▶ ALB ──Method=POST (Priority 10)──▶ TG-POST → EC2-POST ✏️

  Real-world use: GET = Read servers (cache-optimised)
                 POST = Write servers (DB-write optimised)
```

---

### Routing Methods Summary

| Routing Type | Rule Condition | Priority | Target Group | Status |
| --- | --- | --- | --- | --- |
| Host-Based | app1.example.com | 1 | TG-App1 | ✅ Completed |
| Host-Based | app2.example.com | 2 | TG-App2 | ✅ Completed |
| Path-Based | /api* | 3 | TG-API | ✅ Completed |
| Path-Based | /web* | 4 | TG-Web | ✅ Completed |
| Query String | platform=mobile | 7 | TG-Mobile | ✅ Completed |
| Query String | platform=desktop | 8 | TG-Desktop | ✅ Completed |
| HTTP Method | GET | 9 | TG-GET | ✅ Completed |
| HTTP Method | POST | 10 | TG-POST | ✅ Completed |

```text
✅ Host-Based Routing
✅ Path-Based Routing
✅ Query String Routing
✅ HTTP Method Routing
✅ Route 53 + ALB Integration
✅ Multi-Target Group Architecture
```

---

## AWS NLB Implementation — Real-World Banking TCP Gateway
> Network Load Balancer · Layer 4 · TCP Port 9000

---

## Scenario

This demo demonstrates a real-world TCP-based banking gateway architecture where:

- Application Load Balancer (ALB) cannot be used
- Network Load Balancer (NLB) is required
- Raw TCP traffic is load balanced
- Health checks and failover are demonstrated

**ALB only supports:** HTTP, HTTPS, WebSocket, gRPC

**Our application uses:** Raw TCP traffic on port 9000

> ℹ Therefore: ALB cannot support this architecture. NLB works at Layer 4 (Transport Layer) and supports TCP, UDP, TLS.

**Architecture — NLB Banking Gateway Architecture**

```text
  ATM Client (EC2: 10.0.2.132)
        │  TCP : 9000
        ▼
  Network Load Balancer (banking-nlb)
  DNS: banking-nlb-xxxx.elb.ap-south-1.amazonaws.com
        │
  ──────────────────────────────────
  │                                │
  ▼                                ▼
banking-core-1              banking-core-2
10.0.1.101                  10.0.2.102
TCP Banking Server          TCP Banking Server
AZ: ap-south-1a             AZ: ap-south-1b
```

---

## Step-by-Step Implementation

### Task 1 — Create VPC

| Setting | Value |
| --- | --- |
| VPC Name | Banking-VPC |
| CIDR | 10.0.0.0/16 |

### Task 2 — Create Public Subnets

| Subnet Name | CIDR | Availability Zone |
| --- | --- | --- |
| Public-Subnet-A | 10.0.1.0/24 | ap-south-1a |
| Public-Subnet-B | 10.0.2.0/24 | ap-south-1b |

### Task 3 — Create Internet Gateway

| Setting | Value |
| --- | --- |
| Internet Gateway Name | Banking-IGW |
| Attach to | Banking-VPC |

### Task 4 — Create Route Table

| Destination | Target |
| --- | --- |
| 10.0.0.0/16 | local |
| 0.0.0.0/0 | Banking-IGW |

**Associate Route Table With:** Public-Subnet-A, Public-Subnet-B

### Task 5 — Create Security Groups

#### banking-backend-sg — Attached to banking-core-1 and banking-core-2

| Type | Port | Protocol | Source |
| --- | --- | --- | --- |
| SSH | 22 | TCP | Your Public IP |
| Custom TCP | 9000 | TCP | 0.0.0.0/0 |

#### atm-client-sg — Attached to atm-client

| Type | Port | Protocol | Source |
| --- | --- | --- | --- |
| SSH | 22 | TCP | Your Public IP |

> **Note:** Traditionally: NLB does NOT use Security Groups. Traffic filtering is handled at Backend EC2 Security Groups.

### Task 6 — Create EC2 Instances

| Instance | Purpose | Subnet |
| --- | --- | --- |
| banking-core-1 | Backend TCP Banking Server | Public-Subnet-A |
| banking-core-2 | Backend TCP Banking Server | Public-Subnet-B |
| atm-client | Simulated ATM Client | Any Public Subnet |

**AMI:** Ubuntu 22.04  ·  **Instance Type:** t2.micro  ·  **Public IP:** Enabled

#### User Data — banking-core-1

```text
#!/bin/bash
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
systemctl start banking-server1.service
```

#### User Data — banking-core-2

```text
#!/bin/bash
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
systemctl start banking-server2.service
```

#### User Data — atm-client

```text
#!/bin/bash
apt update -y
apt install netcat-openbsd -y
```

### Task 7 — Verify Backend Servers

SSH into: **atm-client**

```text
nc <BANKING-CORE-1-PUBLIC-IP> 9000
Expected: Connected to Banking Server 1 at Availability Zone A - Transaction Gateway

nc <BANKING-CORE-2-PUBLIC-IP> 9000
Expected: Connected to Banking Server 2 at Availability Zone B - Transaction Gateway
```

### Task 8 — Create Target Group

| Setting | Value |
| --- | --- |
| Target Group Name | banking-tg |
| Target Type | Instances |
| Protocol | TCP |
| Port | 9000 |
| Health Check Protocol | TCP |
| Healthy Threshold | 3 |
| Unhealthy Threshold | 3 |
| Interval | 10s |
| Timeout | 6s |
| Register Targets | banking-core-1, banking-core-2 |

### Task 9 — Create Network Load Balancer

| Setting | Value |
| --- | --- |
| Name | banking-nlb |
| Scheme | Internet-facing |
| Listener Protocol | TCP |
| Listener Port | 9000 |
| Attach Subnets | Public-Subnet-A (ap-south-1a), Public-Subnet-B (ap-south-1b) |
| Attach Target Group | banking-tg |

Wait until status becomes: **Active**

### Task 10 — Test NLB

```text
nc <NLB-DNS> 9000
Expected: Connected to Banking Server 1 ...

nc <NLB-DNS> 9000
Expected: Connected to Banking Server 2 ...
```

#### Live Load Balancing Demo

```text
while true
do
  nc <NLB-DNS> 9000
  sleep 1
done

Expected Output:
Server 1
Server 2
Server 1
Server 2

This demonstrates: TCP load balancing in real time.
```

### Task 11 — Failover Demo

Stop: **banking-core-1**  ·  Wait: 30–40 seconds

```text
nc <NLB-DNS> 9000

Only Server 2 responds.
This demonstrates: automatic health checks and failover.
```

### Task 12 — Source IP Preservation Demo

SSH into backend server **banking-core-1**, install and start tcpdump:

```text
sudo apt install tcpdump -y
sudo tcpdump -i any port 9000
```

On atm-client, check private IP and connect:

```text
hostname -I
# Example: 10.0.2.132

nc <NLB-DNS> 9000
```

Observe tcpdump output:

```text
IP 10.0.2.132.54872 > 10.0.1.25.9000

This proves: NLB preserves the original client IP.
```

---

## Important NLB Concepts

### NLB Works at Layer 4

Supports: TCP, UDP, TLS

### NLB Preserves Source IP

Backend servers can see: **Real Client IP**

Useful in: Banking, Fraud Detection, Security Logging

### NLB is Built For:

- Banking Systems
- Gaming Servers
- Trading Platforms
- IoT Applications
- TCP-Based Applications
- Ultra-Low Latency Workloads

---

> *"Application Load Balancer understands applications. Network Load Balancer understands network traffic."*

---

*Documentation prepared for AWS Load Balancer Case Study Module*
