#!/usr/bin/env python3
# /pre_run.py
"""
Pre-run initialization script for Nginx Configerrrrrr
Scans existing Nginx configurations, imports them into the database,
and rewrites configuration files while preserving original server blocks.
"""

import os
import sqlite3
import hashlib
import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# Configuration
NGINX_CONF_DIR = "/etc/nginx/conf.d"
DB_PATH = "backend/nginx_manager.db"
LOCATION_MODIFIERS = {"=", "~", "~*", "^~"}


@dataclass
class ParsedLocation:
    """Parsed nginx location block"""

    path: str
    modifier: str
    content: str
    proxy_pass: str = None
    root: str = None


@dataclass
class ParsedServerBlock:
    """Parsed nginx server block"""

    raw_block: str
    server_names: List[str]
    listen_directives: List[str]
    locations: List[ParsedLocation]
    has_ssl: bool
    source_file: str


@dataclass
class ParsedConfigFile:
    """Represents a source .conf file and its parsed blocks"""

    filename: str
    filepath: str
    content: str
    server_blocks: List[ParsedServerBlock] = field(default_factory=list)


@dataclass
class DomainBundle:
    """Groups server blocks that belong to one domain for DB import"""

    domain_name: str
    server_names: List[str] = field(default_factory=list)
    server_blocks: List[ParsedServerBlock] = field(default_factory=list)


class NginxConfigParser:
    """Parse existing Nginx configuration files"""

    def __init__(self, filepath):
        self.filepath = filepath
        self.content = self._read_file()

    def _read_file(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {self.filepath}: {e}")
            return ""

    def parse_server_blocks(self):
        """Parse all server blocks from the file"""
        server_blocks = []

        for _header, inner_content, raw_block in self._extract_blocks(self.content, "server"):
            server_names = self._extract_server_names(inner_content)
            listen_directives = self._extract_directive_values(inner_content, "listen")
            locations = self._extract_locations(inner_content)
            has_ssl = self._has_ssl(inner_content, listen_directives)

            server_blocks.append(
                ParsedServerBlock(
                    raw_block=raw_block.strip(),
                    server_names=server_names,
                    listen_directives=listen_directives,
                    locations=locations,
                    has_ssl=has_ssl,
                    source_file=self.filepath,
                )
            )

        return server_blocks

    def _extract_locations(self, server_content):
        """Extract location blocks from one server block"""
        locations = []

        for header, inner_content, _raw_block in self._extract_blocks(server_content, "location"):
            modifier, path = self._parse_location_header(header)
            cleaned_content = inner_content.strip()

            locations.append(
                ParsedLocation(
                    path=path,
                    modifier=modifier,
                    content=cleaned_content,
                    proxy_pass=self._extract_first_directive_value(cleaned_content, "proxy_pass"),
                    root=self._extract_first_directive_value(cleaned_content, "root"),
                )
            )

        return locations

    def _parse_location_header(self, header):
        normalized = re.sub(r"\s+", " ", header.strip())
        if not normalized:
            return "", "/"

        parts = normalized.split(" ", 1)
        if parts[0] in LOCATION_MODIFIERS:
            modifier = parts[0]
            path = parts[1].strip() if len(parts) > 1 else "/"
            return modifier, path

        return "", normalized

    def _extract_server_names(self, content):
        values = self._extract_directive_values(content, "server_name")
        server_names = []

        for value in values:
            for name in value.split():
                name = name.strip()
                if name and name not in server_names:
                    server_names.append(name)

        return server_names

    def _extract_directive_values(self, content, directive_name):
        content_without_comments = self._strip_comments(content)
        pattern = rf"^\s*{re.escape(directive_name)}\s+([^;]+);"
        matches = re.findall(pattern, content_without_comments, re.MULTILINE)
        return [m.strip() for m in matches if m.strip()]

    def _extract_first_directive_value(self, content, directive_name):
        values = self._extract_directive_values(content, directive_name)
        return values[0] if values else None

    def _has_ssl(self, content, listen_directives):
        for directive in listen_directives:
            if re.search(r"(^|\s)ssl(\s|$)", directive):
                return True

        content_without_comments = self._strip_comments(content)
        if re.search(r"^\s*ssl_certificate(_key)?\s+[^;]+;", content_without_comments, re.MULTILINE):
            return True

        return False

    def _extract_blocks(self, content, keyword):
        """Extract blocks like `server { ... }` or `location ... { ... }`"""
        blocks = []
        cursor = 0
        pattern = re.compile(rf"^\s*{re.escape(keyword)}\b", re.MULTILINE)

        while True:
            match = pattern.search(content, cursor)
            if not match:
                break

            brace_start = self._find_opening_brace(content, match.end())
            if brace_start == -1:
                cursor = match.end()
                continue

            brace_end = self._find_matching_brace(content, brace_start)
            if brace_end == -1:
                cursor = brace_start + 1
                continue

            header = content[match.end():brace_start]
            inner_content = content[brace_start + 1:brace_end]
            raw_block = content[match.start():brace_end + 1]

            blocks.append((header, inner_content, raw_block))
            cursor = brace_end + 1

        return blocks

    def _find_opening_brace(self, content, start_idx):
        """Find block opening brace after a directive keyword"""
        in_comment = False

        for i in range(start_idx, len(content)):
            ch = content[i]

            if in_comment:
                if ch == "\n":
                    in_comment = False
                continue

            if ch == "#":
                in_comment = True
                continue

            if ch == ";":
                return -1

            if ch == "{":
                return i

            if ch == "}":
                return -1

        return -1

    def _find_matching_brace(self, content, opening_idx):
        """Find matching closing brace for a block"""
        depth = 0
        in_comment = False

        for i in range(opening_idx, len(content)):
            ch = content[i]

            if in_comment:
                if ch == "\n":
                    in_comment = False
                continue

            if ch == "#":
                in_comment = True
                continue

            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return i

        return -1

    def _strip_comments(self, content):
        """Remove inline comments for directive extraction"""
        lines = []

        for line in content.splitlines():
            if "#" in line:
                line = line[:line.index("#")]
            lines.append(line)

        return "\n".join(lines)


def _derive_domain_name(server_names, fallback_name):
    """Pick a stable domain key for DB and generated conf naming"""
    for raw_name in server_names:
        name = raw_name.strip()
        if not name or name == "_":
            continue
        if name.startswith("*."):
            name = name[2:]
        elif name.startswith("."):
            name = name[1:]
        return name or fallback_name
    return fallback_name


def _pick_main_server_block(server_blocks):
    """Choose the block that best represents app traffic for location import"""
    if not server_blocks:
        return None

    return max(
        server_blocks,
        key=lambda block: (
            1 if block.locations else 0,
            len(block.locations),
            1 if block.has_ssl else 0,
            len(block.listen_directives),
        ),
    )


def _build_domain_bundles(parsed_files):
    """Group parsed server blocks by domain name"""
    bundles = {}

    for parsed_file in parsed_files:
        fallback_name = os.path.splitext(parsed_file.filename)[0]

        for server_block in parsed_file.server_blocks:
            domain_name = _derive_domain_name(server_block.server_names, fallback_name)

            if domain_name not in bundles:
                bundles[domain_name] = DomainBundle(domain_name=domain_name)

            bundle = bundles[domain_name]
            bundle.server_blocks.append(server_block)

            for server_name in server_block.server_names:
                if server_name not in bundle.server_names:
                    bundle.server_names.append(server_name)

    return bundles


def _disable_conf_file(filepath):
    """Rename old .conf to .conf.disabled (or .conf.disabled.N)"""
    disabled_path = f"{filepath}.disabled"
    if not os.path.exists(disabled_path):
        os.rename(filepath, disabled_path)
        return disabled_path

    suffix = 1
    while True:
        candidate = f"{disabled_path}.{suffix}"
        if not os.path.exists(candidate):
            os.rename(filepath, candidate)
            return candidate
        suffix += 1


def initialize_database():
    """Create database schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_superuser BOOLEAN DEFAULT 0,
            is_default_password BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Domains table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            server_name TEXT NOT NULL,
            listen_port TEXT DEFAULT '80',
            ssl_enabled BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Locations table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain_id INTEGER NOT NULL,
            path TEXT NOT NULL,
            match_modifier TEXT DEFAULT '',
            mode TEXT DEFAULT 'basic',
            forward_type TEXT DEFAULT 'dynamic',
            proxy_pass TEXT,
            root_path TEXT,
            config_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE
        )
    """
    )

    # User-Domain permissions table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_domain_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            domain_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
            UNIQUE(user_id, domain_id)
        )
    """
    )

    # Create default superuser
    password_hash = hashlib.sha256("123456".encode()).hexdigest()
    cursor.execute(
        """
        INSERT OR IGNORE INTO users (username, password_hash, is_superuser, is_default_password)
        VALUES (?, ?, 1, 1)
    """,
        ("root_alex", password_hash),
    )

    conn.commit()
    conn.close()
    print("Database initialized")


def scan_and_import_configs() -> Tuple[List[ParsedConfigFile], Dict[str, DomainBundle]]:
    """Scan /etc/nginx/conf.d/ and import existing configurations"""
    if not os.path.exists(NGINX_CONF_DIR):
        print(f"Warning: {NGINX_CONF_DIR} does not exist")
        return [], {}

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    conf_files = sorted(f for f in os.listdir(NGINX_CONF_DIR) if f.endswith(".conf"))
    print(f"\nScanning {len(conf_files)} configuration files...")

    parsed_files = []

    for conf_file in conf_files:
        filepath = os.path.join(NGINX_CONF_DIR, conf_file)
        print(f"\nProcessing: {conf_file}")

        parser = NginxConfigParser(filepath)
        server_blocks = parser.parse_server_blocks()

        parsed_file = ParsedConfigFile(
            filename=conf_file,
            filepath=filepath,
            content=parser.content,
            server_blocks=server_blocks,
        )
        parsed_files.append(parsed_file)

        if not server_blocks:
            print("  No server blocks found, will preserve file content as-is")
            continue

        print(f"  Server blocks: {len(server_blocks)}")
        for idx, block in enumerate(server_blocks, start=1):
            names = " ".join(block.server_names) if block.server_names else "(none)"
            listen = ", ".join(block.listen_directives) if block.listen_directives else "(none)"
            print(
                f"    [{idx}] server_name: {names} | listen: {listen} | "
                f"SSL: {block.has_ssl} | locations: {len(block.locations)}"
            )

    domain_bundles = _build_domain_bundles(parsed_files)

    print(f"\nImporting {len(domain_bundles)} domain bundles into database...")
    for domain_name in sorted(domain_bundles.keys()):
        bundle = domain_bundles[domain_name]
        main_block = _pick_main_server_block(bundle.server_blocks)
        if not main_block:
            continue

        listen_port = main_block.listen_directives[0] if main_block.listen_directives else "80"
        ssl_enabled = any(block.has_ssl for block in bundle.server_blocks)
        server_name = " ".join(bundle.server_names) if bundle.server_names else domain_name

        print(f"  Domain: {domain_name}")
        print(f"  Listen: {listen_port}")
        print(f"  SSL: {ssl_enabled}")
        print(f"  Imported locations from main block: {len(main_block.locations)}")

        try:
            cursor.execute(
                """
                INSERT INTO domains (name, server_name, listen_port, ssl_enabled)
                VALUES (?, ?, ?, ?)
            """,
                (domain_name, server_name, listen_port, ssl_enabled),
            )

            domain_id = cursor.lastrowid

            for loc in main_block.locations:
                if loc.proxy_pass:
                    forward_type = "dynamic"
                elif loc.root:
                    forward_type = "static"
                else:
                    forward_type = "dynamic"

                cursor.execute(
                    """
                    INSERT INTO locations (domain_id, path, match_modifier, mode,
                                          forward_type, proxy_pass, root_path, config_content)
                    VALUES (?, ?, ?, 'advanced', ?, ?, ?, ?)
                """,
                    (
                        domain_id,
                        loc.path,
                        loc.modifier,
                        forward_type,
                        loc.proxy_pass,
                        loc.root,
                        loc.content,
                    ),
                )

            if not main_block.locations:
                cursor.execute(
                    """
                    INSERT INTO locations (domain_id, path, mode, forward_type)
                    VALUES (?, '/', 'basic', 'dynamic')
                """,
                    (domain_id,),
                )

            print("  Imported successfully")

        except sqlite3.IntegrityError:
            print(f"  Domain {domain_name} already exists, skipping")
        except Exception as e:
            print(f"  Error importing: {e}")

    conn.commit()
    conn.close()
    return parsed_files, domain_bundles


def standardize_configs(parsed_files):
    """
    Rewrite conf files while preserving original content.
    Old .conf files are renamed to .disabled* before new files are moved in.
    """
    print(f"\nStandardizing {len(parsed_files)} configuration files...")

    if not parsed_files:
        return

    temp_outputs = []

    for parsed_file in parsed_files:
        conf_path = parsed_file.filepath
        temp_path = f"{conf_path}.pre_run_tmp"
        content = parsed_file.content
        if content and not content.endswith("\n"):
            content += "\n"

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(content)
            temp_outputs.append((conf_path, temp_path))
            print(f"  Prepared {parsed_file.filename}")
        except Exception as e:
            print(f"  Error preparing {parsed_file.filename}: {e}")

    print("\nDisabling old .conf files...")
    disabled_paths = {}

    for conf_path, _temp_path in temp_outputs:
        try:
            disabled_path = _disable_conf_file(conf_path)
            disabled_paths[conf_path] = disabled_path
            print(f"  Disabled {os.path.basename(conf_path)} -> {os.path.basename(disabled_path)}")
        except Exception as e:
            print(f"  Error disabling {os.path.basename(conf_path)}: {e}")

    print("\nWriting new .conf files...")
    for conf_path, temp_path in temp_outputs:
        if conf_path not in disabled_paths:
            try:
                os.remove(temp_path)
            except OSError:
                pass
            continue

        try:
            os.replace(temp_path, conf_path)
            print(f"  Wrote {os.path.basename(conf_path)}")
        except Exception as e:
            print(f"  Error writing {os.path.basename(conf_path)}: {e}")


def create_log_directories():
    """Create log directories for all domains"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM domains")
    domains = cursor.fetchall()

    print("\nCreating log directories...")

    for (domain_name,) in domains:
        log_dir = f"/var/log/nginx/{domain_name}"
        try:
            os.makedirs(log_dir, exist_ok=True)
            print(f"  Created {log_dir}")
        except Exception as e:
            print(f"  Error creating {log_dir}: {e}")

    conn.close()


def main():
    """Main execution"""
    print("=" * 60)
    print("Nginx Configerrrrrr - Pre-Run Initialization")
    print("=" * 60)

    os.makedirs("backend", exist_ok=True)

    print("\n[1/4] Initializing database...")
    initialize_database()

    print("\n[2/4] Scanning existing Nginx configurations...")
    parsed_files, _domain_bundles = scan_and_import_configs()

    print("\n[3/4] Standardizing configuration files...")
    standardize_configs(parsed_files)

    print("\n[4/4] Creating log directories...")
    create_log_directories()

    print("\n" + "=" * 60)
    print("Pre-run initialization completed successfully!")
    print("=" * 60)
    print("\nYou can now start the backend server:")
    print("  cd backend && python3 app.py")
    print("\nDefault login credentials:")
    print("  Username: root_alex")
    print("  Password: 123456")
    print("  (You will be forced to change this on first login)")


if __name__ == "__main__":
    main()
