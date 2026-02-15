Role: You are a Senior Full-Stack Developer and System Architect.

Project Name: **nginx-configerrrrrr**
Goal: Build a web-based Nginx configuration manager using Python Flask (Backend) and Vue.js (Frontend). The application will run as root on a Linux server to manage `/etc/nginx/conf.d/`.

**Output Requirement:**
Please provide the complete source code. For every single file you generate, the **first line** of the code block must be a comment explicitly stating the file path (e.g., `# /backend/app.py` or ``).

---

### 1. System Architecture & Tech Stack
* **Backend:** Python Flask.
* **Frontend:** Vue.js (Vue 3 + Vite + Element Plus or Tailwind recommended).
* **Database:** SQLite (stored in the application directory).
* **System Access:** The app runs as `root`. It must have permission to read/write `/etc/nginx/conf.d/`, create log directories, and run `nginx -s reload` and `certbot`.

### 2. Database & User Management
* **Users Table:**
    * Superuser: `root_alex`.
    * Default Password: `123456`.
    * **Logic:** Upon first login, if the flag `is_default_password` is true, force the user to change the password before proceeding.
    * **Roles:** The Superuser can create sub-users.
* **Permissions:**
    * Superuser sees and manages ALL domains.
    * Sub-users can only see/edit domains explicitly assigned to them by the Superuser.

### 3. Initialization Script (`pre_run.py`)
Create a standalone script `pre_run.py` to be run before starting the web server.
* **Function:** Scan `/etc/nginx/conf.d/*.conf`.
* **Parsing:** Parse existing Nginx configurations to extract Server Names, Locations, and Proxy rules.
* **Migration:** Import these existing configs into the SQLite database.
* **Mode Setting:** Mark all *existing* imported domains as **"Advanced Mode"**.
* **Standardization:** Re-write the existing `.conf` files to match the "configerrrrrr" standard format (indentation, structure) immediately, ensuring the system starts with a clean state.

### 4. Nginx Configuration Rules (The Core Logic)
Each domain maps to exactly ONE `.conf` file in `/etc/nginx/conf.d/<domain>.conf`.

**A. Global Server Config (Immutable by User):**
* **Logs:** `access_log` and `error_log` must be defined in the `server` block.
    * Path: `/var/log/nginx/<website_name>/access.log` (and error.log).
    * The backend must ensure the directory exists.

**B. Location Block Management:**
* The default location `/` exists by default.
* Users can add new locations (e.g., `/api`).
* **Visual Selector:** Instead of writing Regex manually, provide a UI dropdown for the match type: "Exact Match (=)", "Prefix (^~)", "Regex (~)", "Case-insensitive Regex (~*)", etc.

**C. Configuration Modes (Per Location):**
Every location block has two modes:
1.  **Basic Mode (Default for new domains):**
    * **Fields:** Server Name, Forward Type.
    * **Forward Type - Dynamic:** User enters IP:Port. Generates `proxy_pass`.
    * **Forward Type - Static:** User enters local directory path. Generates `root`.
    * **Template:** In this mode, inject the following **Fixed Parameters** (Standard Template):
        ```nginx
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 1200s;
        proxy_send_timeout 1200s;
        proxy_read_timeout 1200s;
        client_max_body_size 500m;
        client_body_buffer_size 80m;
        keepalive_timeout 300s;
        ```
    * *Note:* If Static type is chosen, remove irrelevant proxy params.

2.  **Advanced Mode (Professional):**
    * Start with the "Standard Template" parameters visible and editable.
    * Provide a "Show More" section (dropdown) to expose other hidden Nginx parameters.
    * **UI:** Provide tooltips/translations explaining what each parameter does.

### 5. Backend API Features
* **CRUD:** Create, Read, Update, Delete domains.
* **Save & Apply:** When saving, regenerate the specific `.conf` file and run `nginx -t` && `nginx -s reload`. Return errors to the UI if `nginx -t` fails.
* **SSL Automation:**
    * Integrate `certbot`.
    * API endpoint to trigger `certbot --nginx -d <domain>`.
    * Ensure non-interactive execution.

### 6. Frontend Features (Vue.js)
* **Login Page:** Handle the `root_alex` forced password change logic.
* **Dashboard:** List domains (filtered by user permissions).
* **Editor:**
    * Visual representation of the Server Block.
    * List of Location Blocks (add/remove supported).
    * Toggle switch inside each Location: "Basic" vs "Advanced".
    * "HTTPS" button to trigger Certbot.
* **User Manager:** (Only visible to `root_alex`) Add users, select which domains they can access (checklist).

### 7. Implementation Steps:
1.  Initialize the project structure.
2.  Write the Backend (`app.py`, `requirements.txt`, and so on like utils).
3.  Write the Frontend (`index.html`, `main.js`, `App.vue` and so on like components, styles, scripts and views).
4.  Provide a `README.md` with instructions on how to install and run.

Please implement the full project structure.