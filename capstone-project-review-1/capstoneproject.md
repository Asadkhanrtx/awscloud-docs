# Saista Bakers — AWS Capstone Project Documentation

**Domain:** saistabakers.com | **Region:** ap-south-1 (Mumbai) | **Platform:** AWS

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Application Architecture](#2-application-architecture)
3. [AWS Infrastructure Overview](#3-aws-infrastructure-overview)
4. [Network Design — VPC & Subnets](#4-network-design--vpc--subnets)
5. [Security Groups](#5-security-groups)
6. [AWS Services Used — Definitions & Role](#6-aws-services-used--definitions--role)
7. [Deployment Architecture Diagram](#7-deployment-architecture-diagram)
8. [Step-by-Step Deployment Guide](#8-step-by-step-deployment-guide)
9. [Fresh Deployment Quick Reference](#9-fresh-deployment-quick-reference)
10. [Troubleshooting](#10-troubleshooting)
11. [Port Reference](#11-port-reference)

---

## 1. Project Overview

**Saista Bakers** is a full-stack bakery e-commerce platform where:

- Customers browse products, build a cart, place orders, make payments, and receive invoice emails
- Admins manage products, view orders, update statuses, and email customers directly

**Tech Stack:**

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 SPA, React Router DOM, Axios |
| Backend | Python FastAPI (3 microservices) |
| Database | MySQL 8.0 (single shared DB) |
| Auth | JWT HS256 tokens (shared SECRET_KEY) |
| Email | Gmail SMTP via smtplib (STARTTLS port 587) |
| Web Server | Nginx (frontend static + backend proxy) |
| Process Manager | systemd (manages 3 FastAPI processes) |

---

## 2. Application Architecture

### Services & Ports

| Service | Port | Responsibility |
|---------|------|---------------|
| User Service | 5001 | Auth (signup/login/JWT), product catalog, admin dashboard, SMTP emails |
| Order Service | 5002 | Cart management, order lifecycle, custom cake requests |
| Payment Service | 5003 | Payment processing, invoice generation, invoice emails |
| React Frontend | — | SPA served as static files via Nginx |
| MySQL | 3306 | Single shared database `saista_bakers` |

### Database Tables

```
users           → id, username, email, password_hash, full_name, role, created_at
products        → id, name, description, category, price, image_url, available
orders          → id, user_id, total_price, status, delivery_address, delivery_date,
                  payment_mode, payment_status, invoice_sent, created_at
order_items     → id, order_id, product_id, quantity, price_at_purchase
custom_orders   → id, user_id, pound, flavour, description, estimated_price,
                  final_price, delivery_date, status, created_at
```

### Order Status Lifecycle

```
cart → pending → confirmed → completed
                           ↘ cancelled
```

### How Services Communicate

```
Browser (React SPA)
    │
    ├── /api/users/*   ──► User Service (port 5001)
    ├── /api/orders/*  ──► Order Service (port 5002)
    └── /api/payment/* ──► Payment Service (port 5003)

All 3 services ──► MySQL (saista_bakers database)

User Service    ──► Gmail SMTP (admin emails)
Payment Service ──► Gmail SMTP (invoice emails on payment)

JWT: User Service ISSUES token → Order & Payment Services VERIFY locally
     (shared SECRET_KEY — no HTTP call between services for auth)
```

### Customer Journey

```
1. Signup/Login  → User Service → users table → JWT issued
2. Browse        → User Service → products table
3. Add to Cart   → Order Service → orders (status=cart) + order_items rows
4. Place Order   → Order Service → status changes cart → pending
5. Pay           → Payment Service → validates order → status → confirmed
                 → generates invoice number (SB-XXXXXXXX)
                 → sends HTML invoice email via Gmail SMTP
```

---

## 3. AWS Infrastructure Overview

### Full Traffic Flow

```
Internet
    │
    ▼
Route 53 (saistabakers.com)
    │  A record alias → ALB DNS
    ▼
WAF (Web Application Firewall)
    │  AWS Managed Rules applied
    ▼
ALB — saista-alb (Internet-facing, ap-south-1)
    │  HTTPS:443 with ACM SSL certificate
    │  HTTP:80 → redirects to HTTPS
    │
    ├── Path: /api/*  (Priority 1) ──────────► tg-saista-backend
    │                                              ├─ Backend EC2-1 (AZ-a, 10.0.3.x)
    │                                              └─ Backend EC2-2 (AZ-b, 10.0.4.x)
    │                                                   │  Nginx :80 (prefix stripping)
    │                                                   ├─ /api/users/*   → :5001 (User Service)
    │                                                   ├─ /api/orders/*  → :5002 (Order Service)
    │                                                   └─ /api/payment/* → :5003 (Payment Service)
    │                                                        │
    │                                                    RDS MySQL (10.0.6.x)
    │
    └── Path: /*    (Default)  ─────────────► tg-saista-frontend
                                                ├─ Frontend EC2-1 (AZ-a, 10.0.1.x)
                                                └─ Frontend EC2-2 (AZ-b, 10.0.2.x)
                                                     Nginx :80 → React build (/var/www/html)

ALB Access Logs ──► S3 Bucket (saista-alb-logs)
```

---

## 4. Network Design — VPC & Subnets

**VPC:** `saista-prod-vpc` | CIDR: `10.0.0.0/16` | Region: `ap-south-1` (Mumbai)

### Subnets

| Subnet Name | CIDR | Type | AZ | What Runs Here |
|-------------|------|------|----|----------------|
| frontend-subnet-1 | 10.0.1.0/24 | Public | AZ-a | Frontend EC2-1, Bastion Host |
| frontend-subnet-2 | 10.0.2.0/24 | Public | AZ-b | Frontend EC2-2 |
| application-subnet-1 | 10.0.3.0/24 | Private | AZ-a | Backend EC2-1 |
| application-subnet-2 | 10.0.4.0/24 | Private | AZ-b | Backend EC2-2 |
| database-subnet | 10.0.6.0/24 | Private | AZ-a | RDS MySQL |

### Gateways

| Gateway | Location | Purpose |
|---------|----------|---------|
| Internet Gateway | Attached to VPC | Allows public subnets to reach the internet |
| NAT Gateway | frontend-subnet-1 (10.0.1.x) | Allows private subnets to reach internet (outbound only — for apt, pip) |

### Route Tables

| Route Table | Associated Subnets | Routes |
|-------------|-------------------|--------|
| rt-public | frontend-subnet-1, frontend-subnet-2 | 0.0.0.0/0 → Internet Gateway |
| rt-private | application-subnet-1, application-subnet-2, database-subnet | 0.0.0.0/0 → NAT Gateway |

### Bastion Host

- **Instance:** t3.micro, Ubuntu 22.04, in `frontend-subnet-1` (10.0.1.x)
- **Purpose:** Single SSH entry point into private subnets
- **Usage:** SSH to Bastion → then SSH from Bastion to backend EC2 private IPs
- **Security:** Only port 22 allowed, only from your IP (`sg-bastion`)
- Backend and RDS are never directly exposed to the internet

---

## 5. Security Groups

| Security Group | Inbound Rules | Purpose |
|---------------|--------------|---------|
| `sg-alb` | TCP 80 from 0.0.0.0/0 · TCP 443 from 0.0.0.0/0 | ALB internet traffic |
| `sg-frontend` | TCP 80 from `sg-alb` · TCP 22 from `sg-bastion` | Frontend EC2s |
| `sg-backend` | TCP 80 from `sg-alb` · TCP 22 from `sg-bastion` | Backend EC2s |
| `sg-rds` | TCP 3306 from `sg-backend` | RDS MySQL — no internet access |
| `sg-bastion` | TCP 22 from your-IP/32 | Bastion — only your IP |

All security groups allow all outbound traffic.

**Defence in depth:** Each layer only accepts traffic from the layer directly above it. RDS can never be reached from the internet — it can only receive connections from `sg-backend` instances.

---

## 6. AWS Services Used — Definitions & Role

### Route 53
**What it is:** AWS's managed DNS (Domain Name System) service. Translates human-readable domain names (saistabakers.com) into IP addresses.

**How we used it:**
- Domain purchased from **Hostinger** — we then created a **Hosted Zone** in Route 53 for `saistabakers.com`
- Route 53 gave us 4 **nameserver records** (NS records) — we pasted these into Hostinger's DNS settings, handing DNS control over to AWS
- Created an **A record** as an **Alias** pointing `saistabakers.com` → ALB DNS name (no IP needed — alias updates automatically when ALB scales)
- Added **CNAME records** issued by ACM for SSL certificate domain validation

---

### ACM (AWS Certificate Manager)
**What it is:** AWS service that provisions, manages, and auto-renews free SSL/TLS certificates.

**How we used it:**
- Requested a public certificate for `saistabakers.com` and `*.saistabakers.com`
- ACM gave CNAME validation records → added them to Route 53 hosted zone → ACM verified ownership and issued the certificate
- Certificate attached to the ALB HTTPS listener (port 443) — all traffic between browser and ALB is now encrypted
- Auto-renews before expiry — no manual intervention needed

---

### WAF (AWS Web Application Firewall)
**What it is:** A firewall that monitors and filters HTTP/HTTPS requests at the application layer (Layer 7). Protects against common web exploits.

**How we used it:**
- Created a **Web ACL** and associated it with the ALB
- Enabled **AWS Managed Rule Groups:**
  - `AWSManagedRulesCommonRuleSet` — blocks SQL injection, XSS, bad bots
  - `AWSManagedRulesKnownBadInputsRuleSet` — blocks known malicious input patterns
  - `AWSManagedRulesAmazonIpReputationList` — blocks IPs with bad reputation (scrapers, bots)
- WAF sits in front of the ALB — malicious requests are blocked before they ever reach the EC2s
- Provides request logging for security auditing

**Why needed for Saista Bakers:**
- Public e-commerce site with login and payment flows — a prime target for SQL injection and credential stuffing
- WAF managed rules provide instant protection without writing custom rules

---

### ALB (Application Load Balancer)
**What it is:** A Layer 7 (HTTP/HTTPS-aware) load balancer that distributes incoming traffic across multiple targets based on rules.

**How we used it:**
- **Internet-facing** — has a public DNS name, sits in both public subnets
- **HTTPS listener (443):** Main listener with ACM certificate attached
- **HTTP listener (80):** Redirects all traffic to HTTPS (301 redirect)
- **Path-based routing rules:**
  - Priority 1: `/api/*` → `tg-saista-backend` (all API calls go to backend EC2s)
  - Default: `/*` → `tg-saista-frontend` (everything else goes to frontend EC2s)
- **Health checks:** Continuously polls each target — unhealthy instances are removed automatically
- **Access logs → S3:** Every request logged with IP, timestamp, path, response code

---

### EC2 (Elastic Compute Cloud)
**What it is:** AWS's virtual machine service. You choose OS, CPU, RAM, storage and get a running server.

**How we used it:**
- **Frontend EC2s (t3.micro):** Ubuntu 22.04 in public subnets AZ-a and AZ-b. Runs Nginx serving the React build from `/var/www/html/`
- **Backend EC2s (t3.small):** Ubuntu 22.04 in private subnets AZ-a and AZ-b. Runs Nginx (API router) + 3 FastAPI services managed by systemd
- **Bastion Host (t3.micro):** Ubuntu 22.04 in public subnet — SSH gateway into private EC2s
- All EC2s launched from custom AMIs for fast, consistent scaling

---

### AMI (Amazon Machine Image)
**What it is:** A snapshot of an EC2 instance (OS + installed software + configuration). Used to launch identical copies.

**How we used it:**
- After fully configuring one backend EC2 (Python, venvs, deps, Nginx, systemd, .env), we created `saista-backend-ami`
- After fully configuring one frontend EC2 (Node.js, npm build, Nginx), we created `saista-frontend-ami`
- Auto Scaling Groups use these AMIs to launch new instances that are production-ready from the first second

---

### Auto Scaling Group (ASG)
**What it is:** Automatically manages a fleet of EC2 instances — launches replacements when instances fail, and scales in/out based on capacity settings.

**How we used it:**
- **Frontend ASG:** Min 2 / Max 2 — always 2 frontend instances across AZ-a and AZ-b
- **Backend ASG:** Min 2 / Max 2 — always 2 backend instances across AZ-a and AZ-b
- If any EC2 is marked unhealthy by the ALB, the ASG terminates it and launches a fresh one from the AMI
- Attached to respective target groups so new instances are registered with ALB automatically

---

### RDS (Relational Database Service)
**What it is:** AWS's managed database service. Handles backups, patching, failover, and replication automatically.

**How we used it:**
- Engine: **MySQL 8.0**
- DB identifier: `saista-bakers-db`
- Single database: `saista_bakers` — shared by all 3 backend services
- Placed in `database-subnet` (10.0.6.0/24) with **no public access**
- DB Subnet Group spans application-subnet-1 and application-subnet-2 for Multi-AZ readiness
- Only `sg-backend` instances can connect (port 3306) — complete network isolation
- Schema created and seeded automatically by `migrate_db.py` on first backend EC2 start

---

### S3 (Simple Storage Service)
**What it is:** AWS's object storage service. Stores files as objects in "buckets" — infinitely scalable, durable, cheap.

**How we used it:**
- Created bucket: `saista-alb-logs`
- ALB configured to deliver **access logs** to this bucket every 5 minutes
- Each log file contains: timestamp, client IP, request path, response code, latency, backend IP
- Used for: security audits, debugging 4xx/5xx errors, traffic analysis
- Bucket policy restricts access — only the ALB delivery service can write, only your account can read

---

### NAT Gateway
**What it is:** Allows instances in private subnets to initiate outbound internet connections (e.g., download packages) without having a public IP or being reachable from the internet.

**How we used it:**
- Placed in `frontend-subnet-1` (public subnet) with an Elastic IP
- Backend EC2s in private subnets route their outbound traffic through NAT Gateway
- Allows: `apt install`, `pip install`, GitHub clone, Gmail SMTP outbound — all without exposing EC2s

---

### systemd
**What it is:** Linux's system and service manager. Manages background processes (start, stop, restart, auto-start on boot).

**How we used it:**
- Three service unit files: `saista-user.service`, `saista-order.service`, `saista-payment.service`
- Each service: starts uvicorn, restarts automatically within 5 seconds if it crashes, starts on EC2 boot
- User Service runs `migrate_db.py` as `ExecStartPre` — ensures schema is always up to date before the API starts accepting requests

---

### Nginx
**What it is:** High-performance web server and reverse proxy.

**How we used it — two separate roles:**
- **Frontend Nginx:** Serves the React build as static files from `/var/www/html/`. Handles React Router with `try_files $uri /index.html` so page refreshes don't 404
- **Backend Nginx:** Receives requests from the ALB and routes them internally to the correct FastAPI service — strips the `/api/service` prefix before forwarding:
  - `/api/users/*` → strips prefix → `localhost:5001`
  - `/api/orders/*` → strips prefix → `localhost:5002`
  - `/api/payment/*` → strips prefix → `localhost:5003`

---

## 7. Deployment Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           INTERNET                                       │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │      Route 53         │
                    │  saistabakers.com     │
                    │  A alias → ALB DNS    │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │         WAF           │
                    │  AWS Managed Rules    │
                    │  (SQL injection, XSS, │
                    │   bad bots, bad IPs)  │
                    └───────────┬───────────┘
                                │
┌───────────────────────────────▼────────────────────────────────────────┐
│              saista-prod-vpc  10.0.0.0/16  (ap-south-1)                │
│                                                                         │
│  ┌──────────────── PUBLIC SUBNETS ────────────────────────────────┐    │
│  │                                                                 │    │
│  │  10.0.1.0/24 (AZ-a)          10.0.2.0/24 (AZ-b)              │    │
│  │  ┌────────────────┐           ┌────────────────┐               │    │
│  │  │ ALB Node AZ-a  │           │ ALB Node AZ-b  │               │    │
│  │  └───────┬────────┘           └────────┬───────┘               │    │
│  │          └──────── saista-alb ─────────┘                       │    │
│  │               HTTPS:443 (ACM cert)                              │    │
│  │               HTTP:80 → redirect HTTPS                          │    │
│  │               /api/* → tg-saista-backend (Priority 1)          │    │
│  │               /*     → tg-saista-frontend (Default)            │    │
│  │               Logs → S3: saista-alb-logs                       │    │
│  │                                                                 │    │
│  │  ┌─────────────────┐          ┌─────────────────┐              │    │
│  │  │  Frontend EC2-1 │          │  Frontend EC2-2 │              │    │
│  │  │  t3.micro       │          │  t3.micro       │              │    │
│  │  │  Ubuntu 22.04   │          │  Ubuntu 22.04   │              │    │
│  │  │  Nginx → React  │          │  Nginx → React  │              │    │
│  │  │  /var/www/html  │          │  /var/www/html  │              │    │
│  │  │  sg-frontend    │          │  sg-frontend    │              │    │
│  │  └─────────────────┘          └─────────────────┘              │    │
│  │           ▲ ASG: saista-frontend-asg (min 2 / max 2)           │    │
│  │                                                                 │    │
│  │  ┌──────────────┐    ┌──────────┐                              │    │
│  │  │ Bastion Host │    │   NAT    │                              │    │
│  │  │ t3.micro     │    │ Gateway  │                              │    │
│  │  │ sg-bastion   │    │ + EIP    │                              │    │
│  │  └──────┬───────┘    └────┬─────┘                              │    │
│  └─────────┼────────────────┼────────────────────────────────────┘    │
│            │ SSH             │ outbound                                 │
│  ┌─────────┼────────── PRIVATE SUBNETS (APPLICATION) ───────────────┐  │
│  │         │                                                          │  │
│  │  10.0.3.0/24 (AZ-a)          10.0.4.0/24 (AZ-b)                 │  │
│  │  ┌──────▼──────────┐         ┌────────────────┐                  │  │
│  │  │  Backend EC2-1  │         │  Backend EC2-2  │                  │  │
│  │  │  t3.small       │         │  t3.small       │                  │  │
│  │  │  Ubuntu 22.04   │         │  Ubuntu 22.04   │                  │  │
│  │  │  sg-backend     │         │  sg-backend     │                  │  │
│  │  │  ┌───────────┐  │         │  ┌───────────┐  │                  │  │
│  │  │  │   Nginx   │  │         │  │   Nginx   │  │                  │  │
│  │  │  │   :80     │  │         │  │   :80     │  │                  │  │
│  │  │  └─────┬─────┘  │         │  └─────┬─────┘  │                  │  │
│  │  │  ┌─────▼──────┐ │         │  ┌─────▼──────┐ │                  │  │
│  │  │  │User  :5001 │ │         │  │User  :5001 │ │                  │  │
│  │  │  │Order :5002 │ │         │  │Order :5002 │ │                  │  │
│  │  │  │Pay   :5003 │ │         │  │Pay   :5003 │ │                  │  │
│  │  │  │(systemd)   │ │         │  │(systemd)   │ │                  │  │
│  │  │  └────────────┘ │         │  └────────────┘ │                  │  │
│  │  └─────────────────┘         └────────────────┘                  │  │
│  │         ▲ ASG: saista-backend-asg (min 2 / max 2)                │  │
│  │                        │                                          │  │
│  └────────────────────────┼─────────────────────────────────────────┘  │
│                           │ MySQL :3306                                  │
│  ┌────────────────────────▼──── PRIVATE SUBNET (DATABASE) ───────────┐  │
│  │                                                                    │  │
│  │  10.0.6.0/24 (AZ-a)                                               │  │
│  │  ┌──────────────────────────────────────┐                         │  │
│  │  │  RDS MySQL 8.0                       │                         │  │
│  │  │  saista-bakers-db                    │                         │  │
│  │  │  DB: saista_bakers                   │                         │  │
│  │  │  sg-rds (3306 from sg-backend only)  │                         │  │
│  │  │                                      │                         │  │
│  │  │  Tables: users, products, orders,    │                         │  │
│  │  │          order_items, custom_orders  │                         │  │
│  │  └──────────────────────────────────────┘                         │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   Gmail SMTP :587      │
                    │   (external service)   │
                    │   Invoice emails       │
                    │   Admin emails         │
                    └───────────────────────┘

                    ┌───────────────────────┐
                    │   S3: saista-alb-logs  │
                    │   ALB access logs      │
                    │   every 5 minutes      │
                    └───────────────────────┘
```

---

## 8. Step-by-Step Deployment Guide

### Pre-requisites

- AWS account with admin access
- Domain `saistabakers.com` registered on Hostinger
- GitHub repo with project code
- Key pair created in ap-south-1

---

### Phase 1 — Network Setup

#### Create VPC
- CIDR: `10.0.0.0/16`, Name: `saista-prod-vpc`
- Enable DNS resolution and DNS hostnames

#### Create Subnets
| Name | CIDR | AZ | Public |
|------|------|----|--------|
| frontend-subnet-1 | 10.0.1.0/24 | ap-south-1a | Yes |
| frontend-subnet-2 | 10.0.2.0/24 | ap-south-1b | Yes |
| application-subnet-1 | 10.0.3.0/24 | ap-south-1a | No |
| application-subnet-2 | 10.0.4.0/24 | ap-south-1b | No |
| database-subnet | 10.0.6.0/24 | ap-south-1a | No |

#### Create Internet Gateway
- Name: `saista-igw` → Attach to `saista-prod-vpc`

#### Create NAT Gateway
- Subnet: `frontend-subnet-1` → Allocate new Elastic IP → Create

#### Create Route Tables
- **rt-public:** Add route `0.0.0.0/0 → saista-igw` → Associate: frontend-subnet-1, frontend-subnet-2
- **rt-private:** Add route `0.0.0.0/0 → NAT Gateway` → Associate: application-subnet-1, application-subnet-2, database-subnet

#### Create Security Groups
Create all 5 security groups with rules from [Section 5](#5-security-groups).

---

### Phase 2 — SSL Certificate (ACM)

1. **AWS Console → ACM → Request certificate → Public**
2. Domain names: `saistabakers.com` and `*.saistabakers.com`
3. Validation: **DNS validation**
4. ACM gives you CNAME records → add them to Route 53 hosted zone
5. Wait ~5 minutes → status shows **Issued**

---

### Phase 3 — Route 53 & Domain

1. **Route 53 → Create Hosted Zone → Domain: `saistabakers.com`**
2. Copy the 4 NS (nameserver) records Route 53 gives you
3. Go to **Hostinger DNS settings** → replace nameservers with Route 53's NS records
4. Wait 1–24 hours for DNS propagation

---

### Phase 4 — S3 Bucket for ALB Logs

1. **S3 → Create bucket → Name: `saista-alb-logs`**
2. Region: `ap-south-1`
3. Block all public access: **On**
4. Add bucket policy allowing the ALB delivery service to write:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::718504428378:root"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::saista-alb-logs/AWSLogs/*"
    }
  ]
}
```

> Note: `718504428378` is the ELB service account ID for ap-south-1. Replace if using a different region.

---

### Phase 5 — RDS MySQL

1. **RDS → Create database → MySQL 8.0**
   - DB identifier: `saista-bakers-db`
   - Master username: `admin`
   - Master password: *(note it down)*
   - Initial DB name: `saista_bakers`
   - VPC: `saista-prod-vpc`
   - DB Subnet Group: create new → select application-subnet-1 + application-subnet-2
   - Public access: **No**
   - Security group: `sg-rds`

2. Wait for status **Available** (~5 min)
3. Copy the **Endpoint** from Connectivity tab

---

### Phase 6 — Backend EC2 Setup

#### Launch Backend EC2-1

- AMI: Ubuntu 22.04 LTS
- Instance type: `t3.small`
- Subnet: `application-subnet-1`
- Auto-assign public IP: No
- Security group: `sg-backend`
- Storage: 20 GB gp3

#### SSH via Bastion

```bash
# First SSH to bastion
ssh -i your-key.pem ubuntu@<bastion-public-ip>

# Then from bastion to backend EC2
ssh -i your-key.pem ubuntu@<backend-private-ip>
```

#### Clone and Run Setup Script

```bash
sudo apt update -qq && sudo apt install -y git
git clone https://github.com/<your-username>/<your-repo>.git
cd saista-helm-chart-1
bash infra/backend-setup.sh
```

The script automatically:
- Installs Python 3.11 (deadsnakes PPA)
- Creates virtualenvs for all 3 services
- Installs pip dependencies
- Copies `.env.example` → `.env` (credentials pre-baked in)
- Configures backend Nginx with prefix stripping
- Installs and enables systemd service units
- Runs `migrate_db.py` (creates tables, seeds admin + products)
- Starts all 3 services
- Prints health check for ports 5001, 5002, 5003

> **Default admin credentials seeded:** `asadadmin` / `Asad@1234`

#### Create Backend AMI

EC2 Console → Select Backend EC2-1 → Actions → Image and templates → Create image → Name: `saista-backend-ami`

---

### Phase 7 — Frontend EC2 Setup

#### Launch Frontend EC2-1

- AMI: Ubuntu 22.04 LTS
- Instance type: `t3.micro`
- Subnet: `frontend-subnet-1`
- Auto-assign public IP: Yes
- Security group: `sg-frontend`
- Storage: 20 GB gp3

#### SSH and Run Setup Script

```bash
ssh -i your-key.pem ubuntu@<frontend-public-ip>
sudo apt update -qq && sudo apt install -y git
git clone https://github.com/<your-username>/<your-repo>.git
cd saista-helm-chart-1
bash infra/frontend-setup.sh
```

The script automatically:
- Installs Node.js 18
- Runs `npm install` + `CI=false npm run build`
- Deploys build to `/var/www/html/`
- Configures Nginx for React SPA (try_files for client-side routing)
- Verifies all product images return 200

#### Create Frontend AMI

EC2 Console → Select Frontend EC2-1 → Actions → Image and templates → Create image → Name: `saista-frontend-ami`

---

### Phase 8 — Application Load Balancer

#### Create Target Groups

**Frontend TG:**
- Name: `tg-saista-frontend` · Protocol: HTTP · Port: 80
- Health check path: `/` · Healthy: 2 / Unhealthy: 3 / Interval: 30s
- Register: Frontend EC2-1

**Backend TG:**
- Name: `tg-saista-backend` · Protocol: HTTP · Port: 80
- Health check path: `/api/users/health` · Healthy: 2 / Unhealthy: 3 / Interval: 30s
- Register: Backend EC2-1

#### Create ALB

1. EC2 → Load Balancers → Create → Application Load Balancer
2. Name: `saista-alb` · Scheme: Internet-facing · IPv4
3. VPC: `saista-prod-vpc`
4. Mappings: `frontend-subnet-1` (AZ-a) + `frontend-subnet-2` (AZ-b)
5. Security group: `sg-alb`
6. Listener HTTPS:443 → ACM certificate → Default: Forward to `tg-saista-frontend`
7. Listener HTTP:80 → Redirect to HTTPS (301)
8. Enable access logs → S3 bucket: `saista-alb-logs`

#### Add Path Routing Rule

Listeners → HTTPS:443 → Manage rules → Add rule:
- Name: `api-backend`
- Condition: Path → `/api/*`
- Action: Forward to `tg-saista-backend`
- Priority: **1**

---

### Phase 9 — WAF

1. **AWS Console → WAF & Shield → Create Web ACL**
2. Name: `saista-waf` · Resource type: Regional resources (ALB) · Region: ap-south-1
3. Associate with: `saista-alb`
4. Add managed rule groups:
   - `AWS-AWSManagedRulesCommonRuleSet` — SQL injection, XSS, bad inputs
   - `AWS-AWSManagedRulesKnownBadInputsRuleSet` — known attack patterns
   - `AWS-AWSManagedRulesAmazonIpReputationList` — known bad IPs, bots
5. Default action: **Allow** (managed rules block what matches)
6. Enable CloudWatch metrics + sampling

---

### Phase 10 — Route 53 A Record

1. Route 53 → Hosted zone `saistabakers.com` → Create record
2. Record name: (leave blank for root domain)
3. Record type: **A**
4. Alias: **Yes** → Route traffic to: ALB → `saista-alb` DNS name
5. Save

Now `https://saistabakers.com` routes through WAF → ALB → EC2s.

---

### Phase 11 — Auto Scaling Groups

#### Launch Templates

**Frontend LT:**
- Name: `lt-saista-frontend` · AMI: `saista-frontend-ami`
- Instance type: `t3.micro` · Security group: `sg-frontend`

**Backend LT:**
- Name: `lt-saista-backend` · AMI: `saista-backend-ami`
- Instance type: `t3.small` · Security group: `sg-backend`

#### Auto Scaling Groups

**Frontend ASG:**
- Launch template: `lt-saista-frontend`
- Subnets: `frontend-subnet-1` + `frontend-subnet-2`
- Attach to: `tg-saista-frontend`
- Desired: 2 · Min: 2 · Max: 2 · Health check: ELB · Grace: 60s

**Backend ASG:**
- Launch template: `lt-saista-backend`
- Subnets: `application-subnet-1` + `application-subnet-2`
- Attach to: `tg-saista-backend`
- Desired: 2 · Min: 2 · Max: 2 · Health check: ELB · Grace: 90s

After ASG launches new instances and they show **healthy** in target groups, you can terminate the original EC2-1 instances.

---

### Phase 12 — End-to-End Test

```bash
# Replace with your ALB DNS or domain
ALB=https://saistabakers.com

# 1. Frontend loads
curl -I $ALB/

# 2. API health checks
curl $ALB/api/users/health
curl $ALB/api/orders/health
curl $ALB/api/payment/health

# 3. Signup
curl -X POST $ALB/api/users/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test@1234","full_name":"Test User"}'

# 4. Login — capture token
TOKEN=$(curl -s -X POST $ALB/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test@1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 5. List products
curl $ALB/api/users/products

# 6. Add to cart
curl -X POST $ALB/api/orders/cart \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"product_id":1,"quantity":1}'
```

**Browser tests:**
- `https://saistabakers.com` → React app loads with products and images
- `https://saistabakers.com/admin/login` → Admin login → `asadadmin` / `Asad@1234`

---

## 9. Fresh Deployment Quick Reference

When starting from scratch (new RDS, new environment), only these 4 values change:

| What | Where to update |
|------|----------------|
| RDS endpoint (`DB_HOST`) | `saista-user/src/.env.example`, `saista-order/src/.env.example`, `saista-payment/src/.env.example` |
| RDS password (`DB_PASSWORD`) | Same 3 files above |
| Gmail App Password (`SMTP_PASSWORD`) | `saista-user/src/.env.example` and `saista-payment/src/.env.example` |
| ALB DNS | Route 53 A record alias target |

### Steps

**Step 1 — Create new RDS** (Mumbai, MySQL 8.0, saista_bakers DB, backend subnets, no public access) → copy endpoint

**Step 2 — Update 3 files** in repo:

```
saista-user/src/.env.example    → DB_HOST, DB_PASSWORD, SMTP_PASSWORD
saista-order/src/.env.example   → DB_HOST, DB_PASSWORD
saista-payment/src/.env.example → DB_HOST, DB_PASSWORD, SMTP_PASSWORD
```

Everything else (DB_USER, DB_NAME, DB_PORT, SECRET_KEY, SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SMTP_USER) stays the same.

**Step 3 — Push repo**

```bash
git add saista-user/src/.env.example saista-order/src/.env.example saista-payment/src/.env.example
git commit -m "update credentials for new deployment"
git push
```

**Step 4 — Launch Backend EC2** (Ubuntu 22.04, t3.small, application-subnet-1, sg-backend)

```bash
ssh -i your-key.pem ubuntu@<bastion-ip>
ssh -i your-key.pem ubuntu@<backend-private-ip>
sudo apt update -qq && sudo apt install -y git
git clone https://github.com/<your-username>/<your-repo>.git
cd saista-helm-chart-1
bash infra/backend-setup.sh
```

**Step 5 — Launch Frontend EC2** (Ubuntu 22.04, t3.micro, frontend-subnet-1, sg-frontend)

```bash
ssh -i your-key.pem ubuntu@<frontend-public-ip>
sudo apt update -qq && sudo apt install -y git
git clone https://github.com/<your-username>/<your-repo>.git
cd saista-helm-chart-1
bash infra/frontend-setup.sh
```

**Step 6 — Create ALB**
- 2 target groups: `tg-saista-frontend` (health: `/`) and `tg-saista-backend` (health: `/api/users/health`)
- Internet-facing ALB across both public subnets, sg-alb
- HTTPS:443 with ACM cert → default → `tg-saista-frontend`
- HTTP:80 → redirect to HTTPS
- Rule: `/api/*` → `tg-saista-backend` (Priority 1)
- Enable access logs → `saista-alb-logs` S3 bucket

**Step 7 — Attach WAF**
- Associate `saista-waf` Web ACL with new ALB

**Step 8 — Route 53**
- Update A record alias to point to new ALB DNS

**Step 9 — Create AMIs + ASGs**
- Backend AMI → `lt-saista-backend` → Backend ASG (min 2 / max 2, application subnets)
- Frontend AMI → `lt-saista-frontend` → Frontend ASG (min 2 / max 2, frontend subnets)

---

## 10. Troubleshooting

### Service not starting on backend EC2

```bash
sudo journalctl -u saista-user --no-pager -n 50
sudo journalctl -u saista-order --no-pager -n 50
sudo journalctl -u saista-payment --no-pager -n 50
```

### Cannot connect to RDS

```bash
# From backend EC2
nc -zv YOUR_RDS_ENDPOINT 3306
# "Connection succeeded" = SG and routing are correct
# Hangs = sg-rds missing inbound from sg-backend
```

### ALB returns 502

FastAPI service is down but Nginx is up:

```bash
sudo systemctl status saista-user saista-order saista-payment
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health
```

### ALB target shows unhealthy

```bash
# Check Nginx is running and health endpoint responds
curl http://localhost:80/api/users/health
sudo systemctl status nginx
```

### Images return 404

```bash
ls /var/www/html/images/gallery/
# If missing:
sudo cp -r /home/ubuntu/saista-helm-chart-1/saista-frontend/public/images /var/www/html/
sudo systemctl reload nginx
```

### WAF blocking legitimate requests

- WAF & Shield → Web ACLs → `saista-waf` → Sampled requests → check which rule is blocking
- Switch rule action from **Block** to **Count** temporarily to debug without breaking the site

---

## 11. Port Reference

| Component | Port | Location |
|-----------|------|---------|
| ALB | 443 (HTTPS), 80 (redirect) | Internet-facing |
| Frontend Nginx | 80 | Frontend EC2s (public subnets) |
| Backend Nginx | 80 | Backend EC2s (private subnets) |
| user-service | 5001 | Backend EC2 internal only |
| order-service | 5002 | Backend EC2 internal only |
| payment-service | 5003 | Backend EC2 internal only |
| RDS MySQL | 3306 | Private — sg-backend access only |
| Gmail SMTP | 587 | External — outbound from backend EC2 via NAT |
| Bastion SSH | 22 | Public — your IP only |