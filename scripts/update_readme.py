#!/usr/bin/env python3
"""
Local script to update README.md file with various options.
Can be run manually or integrated into pre-commit hooks.
"""

import argparse
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class ReadmeUpdater:
    def __init__(self, readme_path: str = "README.md"):
        self.readme_path = Path(readme_path)
        self.content = self._read_readme()
    
    def _read_readme(self) -> str:
        """Read the current README content."""
        if self.readme_path.exists():
            return self.readme_path.read_text()
        return ""
    
    def _write_readme(self, content: str) -> None:
        """Write updated content to README."""
        self.readme_path.write_text(content)
    
    def update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        if '*Last updated:' in self.content:
            self.content = re.sub(
                r'\*Last updated:.*?\*',
                f'*Last updated: {timestamp}*',
                self.content
            )
        else:
            self.content += f'\n\n---\n\n*Last updated: {timestamp}*\n'
        
        print(f"✅ Updated timestamp to {timestamp}")
    
    def update_toc(self) -> None:
        """Update or generate table of contents."""
        # Remove existing TOC
        self.content = re.sub(
            r'## Table of Contents.*?(?=##)',
            '',
            self.content,
            flags=re.DOTALL
        )
        
        # Extract headers
        headers = re.findall(r'^(#{2,6})\s+(.+)$', self.content, re.MULTILINE)
        
        # Generate new TOC
        toc = '## Table of Contents\n\n'
        for level, title in headers:
            if title not in ['Table of Contents']:
                depth = len(level) - 2
                indent = '  ' * depth
                anchor = title.lower()
                anchor = re.sub(r'[^a-z0-9\s-]', '', anchor)
                anchor = re.sub(r'\s+', '-', anchor)
                toc += f'{indent}- [{title}](#{anchor})\n'
        
        # Insert TOC after main heading
        lines = self.content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('# ') and i > 0:
                insert_pos = i + 1
                while insert_pos < len(lines) and not lines[insert_pos].strip():
                    insert_pos += 1
                break
        
        lines.insert(insert_pos, '')
        lines.insert(insert_pos + 1, toc.rstrip())
        lines.insert(insert_pos + 2, '')
        
        self.content = '\n'.join(lines)
        print("✅ Updated table of contents")
    
    def update_badges(self) -> None:
        """Update or add status badges."""
        badges = [
            "![Python](https://img.shields.io/badge/python-3.9+-blue.svg)",
            "![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)",
            "![Tests](https://img.shields.io/badge/tests-passing-green.svg)",
            "![License](https://img.shields.io/badge/license-MIT-blue.svg)"
        ]
        
        badge_section = '\n'.join(badges) + '\n\n'
        
        # Find position after main title
        lines = self.content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('# '):
                # Check if badges already exist
                if i + 1 < len(lines) and '![' in lines[i + 1]:
                    # Replace existing badges
                    j = i + 1
                    while j < len(lines) and (lines[j].startswith('![') or not lines[j].strip()):
                        j += 1
                    lines[i+1:j] = [''] + badge_section.strip().split('\n') + ['']
                else:
                    # Insert new badges
                    lines.insert(i + 1, '')
                    lines.insert(i + 2, badge_section.strip())
                break
        
        self.content = '\n'.join(lines)
        print("✅ Updated badges")
    
    def update_api_endpoints(self) -> None:
        """Extract and update API endpoints from code."""
        endpoints = []
        
        # Find all route files
        routes_dir = Path('app/routes')
        if routes_dir.exists():
            for route_file in routes_dir.glob('*.py'):
                with open(route_file, 'r') as f:
                    content = f.read()
                
                # Extract routes
                route_pattern = r'@router\.([a-z]+)\(["\'](.*?)["\'](.*?)\)'
                matches = re.findall(route_pattern, content, re.DOTALL)
                
                for method, path, _ in matches:
                    endpoints.append({
                        'method': method.upper(),
                        'path': path,
                        'file': route_file.stem
                    })
        
        if endpoints:
            # Group by file
            grouped = {}
            for ep in endpoints:
                file = ep['file']
                if file not in grouped:
                    grouped[file] = []
                grouped[file].append(f"- `{ep['method']} {ep['path']}`")
            
            # Generate markdown
            endpoints_md = "## API Endpoints\n\n"
            for file, routes in grouped.items():
                endpoints_md += f"### {file.title()}\n\n"
                endpoints_md += '\n'.join(routes) + '\n\n'
            
            # Update or add section
            if '## API Endpoints' in self.content:
                self.content = re.sub(
                    r'## API Endpoints.*?(?=##|\Z)',
                    endpoints_md,
                    self.content,
                    flags=re.DOTALL
                )
            else:
                # Add before Testing section
                self.content = self.content.replace('## Testing', endpoints_md + '## Testing')
            
            print(f"✅ Updated API endpoints ({len(endpoints)} routes found)")
    
    def update_dependencies(self) -> None:
        """Update dependencies section from requirements.txt."""
        if not Path('requirements.txt').exists():
            print("⚠️  requirements.txt not found")
            return
        
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        # Parse dependencies
        deps = []
        for req in requirements:
            if req and not req.startswith('#'):
                # Extract package name
                match = re.match(r'^([a-zA-Z0-9-_]+)', req)
                if match:
                    deps.append(match.group(1))
        
        if deps:
            deps_list = '\n'.join([f"- {dep}" for dep in deps[:10]])  # Top 10
            deps_section = f"### Key Dependencies\n\n{deps_list}\n\nSee `requirements.txt` for full list.\n\n"
            
            # Update or add section
            if '### Key Dependencies' in self.content:
                self.content = re.sub(
                    r'### Key Dependencies.*?(?=###|\Z)',
                    deps_section,
                    self.content,
                    flags=re.DOTALL
                )
            else:
                # Add after Features
                self.content = self.content.replace('## Quick Start', deps_section + '## Quick Start')
            
            print(f"✅ Updated dependencies ({len(deps)} packages)")
    
    def format_readme(self) -> None:
        """Apply consistent formatting."""
        # Ensure consistent spacing
        self.content = re.sub(r'\n{3,}', '\n\n', self.content)
        
        # Ensure headers have proper spacing
        self.content = re.sub(r'\n(#{1,6}\s)', r'\n\n\1', self.content)
        self.content = re.sub(r'^(#{1,6}\s)', r'\1', self.content)
        
        # Ensure code blocks have proper spacing
        self.content = re.sub(r'\n```', r'\n\n```', self.content)
        self.content = re.sub(r'```\n(?!\n)', r'```\n\n', self.content)
        
        # Remove trailing whitespace
        lines = self.content.split('\n')
        lines = [line.rstrip() for line in lines]
        self.content = '\n'.join(lines)
        
        # Ensure file ends with newline
        if not self.content.endswith('\n'):
            self.content += '\n'
        
        print("✅ Applied formatting")
    
    def validate(self) -> List[str]:
        """Validate README for common issues."""
        issues = []
        
        # Check for broken internal links
        internal_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', self.content)
        headers = re.findall(r'^#{1,6}\s+(.+)$', self.content, re.MULTILINE)
        anchors = []
        for header in headers:
            anchor = header.lower()
            anchor = re.sub(r'[^a-z0-9\s-]', '', anchor)
            anchor = re.sub(r'\s+', '-', anchor)
            anchors.append(anchor)
        
        for text, link in internal_links:
            if link not in anchors:
                issues.append(f"Broken anchor link: #{link}")
        
        # Check for TODO items
        todos = re.findall(r'TODO:.*$', self.content, re.MULTILINE)
        for todo in todos:
            issues.append(f"Found TODO: {todo}")
        
        # Check for missing sections
        expected_sections = ['## Features', '## Installation', '## Usage']
        for section in expected_sections:
            if section not in self.content:
                issues.append(f"Missing section: {section}")
        
        if issues:
            print("⚠️  Validation issues found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ Validation passed")
        
        return issues
    
    def save(self) -> None:
        """Save the updated README."""
        self._write_readme(self.content)
        print(f"💾 Saved changes to {self.readme_path}")


def main():
    parser = argparse.ArgumentParser(description='Update README.md file')
    parser.add_argument('--all', action='store_true', help='Run all updates')
    parser.add_argument('--timestamp', action='store_true', help='Update timestamp')
    parser.add_argument('--toc', action='store_true', help='Update table of contents')
    parser.add_argument('--badges', action='store_true', help='Update badges')
    parser.add_argument('--endpoints', action='store_true', help='Update API endpoints')
    parser.add_argument('--deps', action='store_true', help='Update dependencies')
    parser.add_argument('--format', action='store_true', help='Format README')
    parser.add_argument('--validate', action='store_true', help='Validate README')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without saving')
    
    args = parser.parse_args()
    
    # If no specific options, show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    updater = ReadmeUpdater()
    
    # Store original content for dry run
    original_content = updater.content
    
    # Run requested updates
    if args.all or args.timestamp:
        updater.update_timestamp()
    
    if args.all or args.toc:
        updater.update_toc()
    
    if args.all or args.badges:
        updater.update_badges()
    
    if args.all or args.endpoints:
        updater.update_api_endpoints()
    
    if args.all or args.deps:
        updater.update_dependencies()
    
    if args.all or args.format:
        updater.format_readme()
    
    if args.all or args.validate:
        updater.validate()
    
    # Save or show diff
    if args.dry_run:
        print("\n📋 Preview of changes (dry run):")
        print("=" * 50)
        # Simple diff display
        if original_content != updater.content:
            print("Changes would be made to README.md")
            print("Run without --dry-run to apply changes")
        else:
            print("No changes would be made")
    else:
        if original_content != updater.content:
            updater.save()
        else:
            print("ℹ️  No changes needed")


if __name__ == "__main__":
    main()