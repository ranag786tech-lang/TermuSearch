# Add this to your crawler logic
project_entry = {
    "title": repo_name,
    "description": repo_desc,
    "tech_stack": ["Python", "JavaScript"], # Detect based on file extensions
    "last_updated": last_commit_date,
    "url": repo_url,
    "category": "Nexus" if "nexus" in repo_name.lower() else "General"
}

