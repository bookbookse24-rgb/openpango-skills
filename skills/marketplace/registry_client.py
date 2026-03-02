import sqlite3
import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional
import urllib.request
import urllib.parse
import urllib.error

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SkillRegistry")

class SkillRegistry:
    """
    Client for the OpenPango Decentralized Skill Registry.
    Enables agents to discover, search, and publish skills to the A2A Economy.
    """
    
    DEFAULT_REGISTRY_URL = "https://api.openpango.org/v1/registry"
    
    def __init__(self, db_path: str = None, registry_url: str = None):
        if db_path is None:
            # Default to tracking inside the workspace
            workspace = os.path.expanduser("~/.openclaw/workspace")
            os.makedirs(workspace, exist_ok=True)
            db_path = os.path.join(workspace, "registry_cache.sqlite")
            
        self.db_path = db_path
        self.registry_url = registry_url or self.DEFAULT_REGISTRY_URL
        self._init_db()
        
    def _init_db(self):
        """Initialize the local SQLite cache for skill discovery."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS skills (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    version TEXT,
                    author TEXT,
                    install_uri TEXT NOT NULL,
                    capabilities TEXT,
                    last_updated TIMESTAMP
                )
            ''')
            # Seed with core skills if empty
            cursor = conn.execute("SELECT count(*) FROM skills")
            if cursor.fetchone()[0] == 0:
                self._seed_core_skills(conn)
            conn.commit()

    def _seed_core_skills(self, conn):
        """Seed the db with known core skills to bootstrap discovery."""
        core_skills = [
            ("browser", "Playwright-based persistent daemon.", "1.0", "openpango", "local", "['web/browser', 'web/interaction']"),
            ("memory", "Event-sourced long-horizon task graph.", "1.0", "openpango", "local", "['core/memory', 'core/state']"),
            ("figma", "Figma Design-to-Code API.", "1.0", "moth-asa", "local", "['design/figma', 'code/css']"),
        ]
        conn.executemany(
            "INSERT INTO skills (id, name, description, version, author, install_uri, capabilities, last_updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [(name, name, desc, ver, author, uri, caps, datetime.now().isoformat()) for name, desc, ver, author, uri, caps in core_skills]
        )

    def search(self, query: str = None, capability: str = None) -> List[Dict]:
        """
        Search for skills locally and (optionally) via the remote registry.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            sql = "SELECT * FROM skills WHERE 1=1"
            params = []
            
            if query:
                sql += " AND (name LIKE ? OR description LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
                
            if capability:
                # Basic string match for now; in production use JSON1 extension or FTS
                sql += " AND capabilities LIKE ?"
                params.append(f"%{capability}%")
                
            cursor = conn.execute(sql, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            # Parse capabilities string back to list
            for r in results:
                try:
                    r['capabilities'] = json.loads(r['capabilities'].replace("'", "\""))
                except:
                    r['capabilities'] = []
                    
            return results

    def publish(self, name: str, description: str, version: str, author: str, install_uri: str, capabilities: List[str] = None):
        """
        Publish a new skill to the local cache and the remote registry via API.
        """
        skill_id = f"{author}/{name}".lower().replace(" ", "-")
        now = datetime.now().isoformat()
        caps_json = json.dumps(capabilities or [])
        
        # 1. Save to local dictionary cache
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO skills 
                (id, name, description, version, author, install_uri, capabilities, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (skill_id, name, description, version, author, install_uri, caps_json, now))
            conn.commit()
            
        logger.info(f"Successfully cached skill {skill_id} locally.")
        
        # 2. Attempt push to remote registry (Simulated)
        try:
            self._push_to_remote(skill_id, name, description, version, author, install_uri, capabilities)
            logger.info(f"Successfully published {skill_id} to global registry.")
        except Exception as e:
            logger.warning(f"Failed to push {skill_id} to remote registry: {e}. Available locally.")
            
        return {"id": skill_id, "status": "published"}

    def _push_to_remote(self, skill_id, name, description, version, author, install_uri, capabilities):
        """Mock network request to the central OpenPango registry."""
        payload = json.dumps({
            "id": skill_id, "name": name, "description": description,
            "version": version, "author": author, "install_uri": install_uri,
            "capabilities": capabilities
        }).encode('utf-8')
        
        # We mock the network call handling to demonstrate production intent
        req = urllib.request.Request(self.registry_url, data=payload, headers={'Content-Type': 'application/json'})
        try:
            # We expect this to fail in our local testing if the api isn't up
            urllib.request.urlopen(req, timeout=2)
        except urllib.error.URLError:
            raise Exception("Registry endpoint unreachable")

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenPango Skill Marketplace CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    search_parser = subparsers.add_parser("search", help="Search for a skill")
    search_parser.add_argument("query", type=str, help="Search term")
    
    publish_parser = subparsers.add_parser("publish", help="Publish a skill")
    publish_parser.add_argument("--name", required=True)
    publish_parser.add_argument("--desc", required=True)
    publish_parser.add_argument("--uri", required=True)
    publish_parser.add_argument("--author", required=True)
    
    args = parser.parse_args()
    registry = SkillRegistry()
    
    if args.command == "search":
        results = registry.search(query=args.query)
        print(json.dumps(results, indent=2))
    elif args.command == "publish":
        res = registry.publish(args.name, args.desc, "1.0.0", args.author, args.uri)
        print(json.dumps(res, indent=2))
    else:
        parser.print_help()
