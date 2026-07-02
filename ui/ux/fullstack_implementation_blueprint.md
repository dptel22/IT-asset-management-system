# CognixAsset: Full-Stack Integration Blueprint (FastAPI + Supabase)

This blueprint details how to connect the entire **CognixAsset** frontend (all 12 HTML pages) with a **FastAPI** backend and **Supabase (PostgreSQL)** database. 

It maps every frontend interface to its corresponding database tables, FastAPI endpoints, and template variables, showing you how to turn your static mockups into a secure, functional web application.

---

## 1. Complete Database Schema (PostgreSQL)

To support the features across all 12 pages, your database must have the following tables:

```mermaid
erDiagram
    USERS {
        int id PK
        string email UNIQUE
        string password_hash
        string role "Admin, Staff"
        int employee_id FK
    }
    EMPLOYEES {
        int id PK
        string name
        string email UNIQUE
        string department
        string role
        string status "Active, Suspended"
    }
    ASSETS {
        int id PK
        string tag UNIQUE "e.g., #LP-0421"
        string name
        string category "Laptops, Servers, Monitors, etc."
        string model
        string serial_number
        string status "Available, Assigned, Maintenance"
        date purchase_date
        float value
        string specs "JSON format specs"
    }
    ASSIGNMENTS {
        int id PK
        int asset_id FK
        int employee_id FK
        date assign_date
        date return_date
        string condition_on_assign
    }
    REQUESTS {
        int id PK
        int requester_id FK
        string asset_category
        string reason
        string status "Pending, Approved, Denied"
        date request_date
    }
    MAINTENANCE_LOGS {
        int id PK
        int asset_id FK
        string issue
        string actions_taken
        float cost
        date log_date
        string status "Pending, Completed"
    }
    TRANSFERS {
        int id PK
        int asset_id FK
        string from_dept
        string to_dept
        int approved_by FK
        date transfer_date
    }
    NOTIFICATIONS {
        int id PK
        string message
        string type "critical, warn, info"
        boolean is_read
        date created_at
    }

    EMPLOYEES ||--o| USERS : "has_account"
    EMPLOYEES ||--o{ ASSIGNMENTS : "assigned"
    ASSETS ||--o{ ASSIGNMENTS : "assigned"
    EMPLOYEES ||--o{ REQUESTS : "requests"
    ASSETS ||--o{ MAINTENANCE_LOGS : "logs"
    ASSETS ||--o{ TRANSFERS : "transfers"
```

---

## 2. Directory Layout & Setup

Organize all files inside your workspace using this unified structure:

```
CognixAsset/
│
├── main.py                     # Main server configuration, endpoints, & middleware
├── database.py                 # Supabase session config
├── models.py                   # SQLAlchemy database tables
├── requirements.txt            # Package list
├── .env                        # Connection URI storage
│
├── static/                     # Static files directory
│   └── css/
│       └── style.css           # Single extracted stylesheet (shared by all pages)
│
└── templates/                  # Frontend HTML Pages
    ├── partials/
    │   ├── sidebar.html        # Shared Sidebar layout
    │   └── topbar.html         # Shared Top navigation bar
    ├── index.html              # Login & System Access
    ├── dashboard.html          # Analytics Overview
    ├── inventory.html          # Search & Manage Assets
    ├── asset-detail.html       # Individual asset statistics
    ├── asset-assignment.html   # Assign Asset Form
    ├── employee-directory.html # Directory list
    ├── employee-profile.html   # Profile detail view
    ├── maintenance.html        # Repairs queue
    ├── requests.html           # Request approval manager
    ├── transfers.html          # Inter-department moves
    ├── notifications.html      # Notifications list
    └── reports.html            # Metrics & Analytics exports
```

---

## 3. Page-by-Page Integration Matrix

This table maps each of your 12 HTML frontend pages to their database queries and FastAPI routes:

| Page Name | FastAPI GET Router | Query Logic (SQLAlchemy) | Template Variables (`Jinja2`) | Form Submissions (POST) |
| :--- | :--- | :--- | :--- | :--- |
| **1. Login (`index.html`)** | `/` | None (Static form) | `error` (if auth fails) | `/login` (checks email/pass, creates JWT cookie) |
| **2. Dashboard (`dashboard.html`)** | `/dashboard` | Count assets by status; Get latest 5 maintenance & assignments. | `stats`, `user`, `recent_activities` | None |
| **3. Inventory (`inventory.html`)** | `/inventory` | List all assets (supports search/filter query strings). | `assets`, `search_query`, `category_filter` | `/assets/add` (registers new asset) |
| **4. Asset Details (`asset-detail.html`)** | `/assets/{id}` | Find asset by ID; Get full assignment and repair history. | `asset`, `history`, `repairs` | `/assets/{id}/update` (edits specifications) |
| **5. Assign Asset (`asset-assignment.html`)** | `/assign` | Fetch list of `Available` assets and list of `Active` employees. | `available_assets`, `employees` | `/assign` (inserts new row into `assignments`) |
| **6. Employee Directory** | `/employees` | List all employees and count their assigned assets. | `employees` | `/employees/add` (registers new employee) |
| **7. Employee Profile** | `/employees/{id}` | Find employee by ID; List active assignments and requests. | `employee`, `assigned_assets`, `requests` | `/employees/{id}/update` (edits department/status) |
| **8. Maintenance (`maintenance.html`)** | `/maintenance` | List all repair logs sorted by status and date. | `logs`, `pending_cost` | `/maintenance/add` (creates new repair job) |
| **9. Requests (`requests.html`)** | `/requests` | Fetch requests where status is `Pending`. | `pending_requests` | `/requests/{id}/approve` (updates status) |
| **10. Transfers (`transfers.html`)** | `/transfers` | List logs of department transfers. | `transfers` | `/transfers/create` (moves asset to new dept) |
| **11. Notifications** | `/notifications` | Select all notifications. | `notifications` | `/notifications/{id}/read` (marks as read) |
| **12. Reports (`reports.html`)** | `/reports` | Compute value depreciation; Count assets by department. | `dept_stats`, `value_stats` | `/reports/export` (downloads spreadsheet) |

---

## 4. Frontend-to-Backend Connection Guide

Here is how to refactor your static elements into dynamic, server-populated fields.

### 1. Login Handler (`index.html` -> `/login`)
In your login form, configure the input tags and action targets:

**Refactored HTML Form (`templates/index.html`):**
```html
<form action="/login" method="POST" class="login-form">
  {% if error %}
    <div class="alert alert-error">{{ error }}</div>
  {% endif %}
  <div class="input-group">
    <label>Email Address</label>
    <input type="email" name="username" required placeholder="name@company.com">
  </div>
  <div class="input-group">
    <label>Password</label>
    <input type="password" name="password" required placeholder="••••••••">
  </div>
  <button type="submit" class="btn btn-primary">Authenticate</button>
</form>
```

**FastAPI Login Route (`main.py`):**
```python
from fastapi import Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
import jwt # PyJWT package

SECRET_KEY = "your-jwt-secret-key"

@app.post("/login")
def login(response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    # 1. Look up user
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user or not verify_password(password, user.password_hash):
        # Return to login page showing error message
        return templates.TemplateResponse("index.html", {"request": {}, "error": "Invalid email or password."})
    
    # 2. Generate Session Token (JWT)
    token = jwt.encode({"user_id": user.id, "role": user.role}, SECRET_KEY, algorithm="HS256")
    
    # 3. Save as HTTP-Only Cookie (highly secure!)
    redirect = RedirectResponse(url="/dashboard", status_code=303)
    redirect.set_cookie(key="session_token", value=token, httponly=True)
    return redirect
```

---

### 2. Loading the Dynamic Asset Grid (`inventory.html`)
In your inventory table, we replace the static mockup rows with a simple Jinja2 loop.

**Dynamic HTML Grid (`templates/inventory.html`):**
```html
<tbody class="table-body">
  {% for asset in assets %}
    <tr>
      <td class="font-data">{{ asset.tag }}</td>
      <td>
        <!-- Clickable link to detail page -->
        <a href="/assets/{{ asset.id }}" style="color: var(--text-primary); text-decoration: none;">
          <strong>{{ asset.name }}</strong>
        </a>
      </td>
      <td>{{ asset.category }}</td>
      <td>{{ asset.model }}</td>
      <td>
        <!-- Dynamic badge color based on status -->
        <span class="badge {% if asset.status == 'Available' %}badge-active{% elif asset.status == 'Assigned' %}badge-neutral{% else %}badge-warn{% endif %}">
          {{ asset.status }}
        </span>
      </td>
      <td>
        <a href="/assets/{{ asset.id }}" class="btn-action"><i data-lucide="eye"></i></a>
      </td>
    </tr>
  {% else %}
    <tr>
      <td colspan="6" style="text-align: center; color: var(--text-secondary);">No assets registered.</td>
    </tr>
  {% endfor %}
</tbody>
```

**FastAPI Fetch Inventory Route (`main.py`):**
```python
@app.get("/inventory", response_class=HTMLResponse)
def get_inventory(request: Request, search: str = None, category: str = None, db: Session = Depends(database.get_db)):
    query = db.query(models.Asset)
    
    # Add optional filters
    if search:
        query = query.filter(models.Asset.name.ilike(f"%{search}%") | models.Asset.tag.ilike(f"%{search}%"))
    if category:
        query = query.filter(models.Asset.category == category)
        
    assets = query.all()
    
    return templates.TemplateResponse("inventory.html", {
        "request": request,
        "assets": assets,
        "search_query": search or "",
        "category_filter": category or ""
    })
```

---

### 3. Assigning an Asset (`asset-assignment.html`)
To assign an asset, the form needs to load active employees and available hardware dynamically from Supabase, select them, and link them together.

**Dynamic Form Elements (`templates/asset-assignment.html`):**
```html
<form action="/assign" method="POST">
  <div class="form-group">
    <label>Select Asset</label>
    <select name="asset_id" required>
      <option value="">-- Choose Hardware --</option>
      {% for asset in available_assets %}
        <option value="{{ asset.id }}">{{ asset.tag }} - {{ asset.name }}</option>
      {% endfor %}
    </select>
  </div>

  <div class="form-group">
    <label>Assign To Employee</label>
    <select name="employee_id" required>
      <option value="">-- Choose Employee --</option>
      {% for employee in employees %}
        <option value="{{ employee.id }}">{{ employee.name }} ({{ employee.department }})</option>
      {% endfor %}
    </select>
  </div>

  <button type="submit" class="btn btn-primary">Confirm Assignment</button>
</form>
```

**FastAPI Assignment Submitter (`main.py`):**
```python
@app.post("/assign")
def assign_asset(asset_id: int = Form(...), employee_id: int = Form(...), db: Session = Depends(database.get_db)):
    # 1. Create assignment log
    assignment = models.Assignment(
        asset_id=asset_id,
        employee_id=employee_id,
        assign_date=datetime.date.today()
    )
    db.add(assignment)

    # 2. Update asset status to 'Assigned'
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if asset:
        asset.status = "Assigned"

    db.commit()
    return RedirectResponse(url="/inventory", status_code=303)
```

---

## 5. Security & Session Handling

To ensure unauthorized users cannot bypass the login page:

1. **Verify Session Middleware**: Write a dependency to verify the HTTP-Only JWT cookie.
2. **Access Control**: Apply this dependency to all protected routes (`/dashboard`, `/inventory`, etc.).

```python
from fastapi import Cookie, HTTPException

def get_current_user(session_token: str = Cookie(None)):
    if not session_token:
        # Redirect back to login page
        raise HTTPException(status_code=307, detail="Not authenticated")
    try:
        payload = jwt.decode(session_token, SECRET_KEY, algorithms=["HS256"])
        return payload # Returns user_id and role
    except jwt.PyJWTError:
        raise HTTPException(status_code=307, detail="Invalid session")
```

---

## 6. Phase-by-Phase Execution Plan

To execute this plan smoothly:

* [ ] **Phase 1: Database Provisioning**: Register on Supabase and run SQL queries to generate database tables.
* [ ] **Phase 2: Local Refactoring**: Extract CSS styles from pages, create EJS/Jinja templates, and set up your directories.
* [ ] **Phase 3: Core API Routing**: Code `database.py`, `models.py`, and `main.py` routes for Login, Dashboard, and Inventory.
* [ ] **Phase 4: Operations Features**: Implement Assignment, Maintenance logging, and Department Transfers.
* [ ] **Phase 5: Refinement**: Add live searching using HTMX to the inventory grid, set up JWT auth middlewares, and test.
