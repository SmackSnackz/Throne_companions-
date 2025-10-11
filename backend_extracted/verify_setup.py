#!/usr/bin/env python3
"""
Verification script to check if backend is properly set up for deployment.
Run this before deploying to catch any configuration issues.
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, required=True):
    """Check if a file exists"""
    exists = Path(filepath).exists()
    status = "✅" if exists else ("❌" if required else "⚠️")
    req_text = "Required" if required else "Optional"
    print(f"{status} {filepath} ({req_text})")
    return exists

def check_env_variable(var_name, required=True):
    """Check if an environment variable is set"""
    value = os.getenv(var_name)
    exists = value is not None and value != ""
    status = "✅" if exists else ("❌" if required else "⚠️")
    req_text = "Required" if required else "Optional"
    print(f"{status} {var_name} ({req_text})")
    return exists

def main():
    print("=" * 60)
    print("Throne Companions Backend - Deployment Verification")
    print("=" * 60)
    print()
    
    # Check Python files
    print("📁 Checking Core Python Files:")
    python_files = [
        ("server.py", True),
        ("models.py", True),
        ("auth_utils.py", True),
        ("memory_system.py", True),
        ("master_prompt_system.py", True),
    ]
    
    for file, required in python_files:
        check_file_exists(file, required)
    print()
    
    # Check config files
    print("⚙️  Checking Configuration Files:")
    config_files = [
        ("config/prompt_system.config.json", True),
        ("config/solicitation.config.json", True),
        ("config/tier_prompts.config.json", True),
        ("config/tone_anchors.config.json", True),
    ]
    
    for file, required in config_files:
        check_file_exists(file, required)
    print()
    
    # Check deployment files
    print("🚀 Checking Deployment Files:")
    deployment_files = [
        ("requirements.txt", True),
        ("Dockerfile", True),
        ("render.yaml", True),
        (".env.example", True),
        (".gitignore", True),
    ]
    
    for file, required in deployment_files:
        check_file_exists(file, required)
    print()
    
    # Check environment variables (from .env file if present)
    print("🔐 Checking Environment Variables:")
    if Path(".env").exists():
        from dotenv import load_dotenv
        load_dotenv()
        
        env_vars = [
            ("MONGO_URL", True),
            ("JWT_SECRET", True),
            ("EMERGENT_LLM_KEY", True),
            ("MIXPANEL_TOKEN", False),
            ("SENDGRID_API_KEY", False),
            ("ADMIN_EMAIL", False),
        ]
        
        for var, required in env_vars:
            check_env_variable(var, required)
    else:
        print("⚠️  .env file not found (will need to set on Render)")
    print()
    
    # Check if emergentintegrations is in requirements
    print("📦 Checking Dependencies:")
    if Path("requirements.txt").exists():
        with open("requirements.txt") as f:
            reqs = f.read()
            if "emergentintegrations" in reqs:
                print("✅ emergentintegrations in requirements.txt")
            else:
                print("❌ emergentintegrations NOT in requirements.txt")
                
            if "fastapi" in reqs:
                print("✅ fastapi in requirements.txt")
            else:
                print("❌ fastapi NOT in requirements.txt")
                
            if "motor" in reqs:
                print("✅ motor (MongoDB) in requirements.txt")
            else:
                print("❌ motor NOT in requirements.txt")
    print()
    
    # Final verdict
    print("=" * 60)
    print("Verification Complete!")
    print("=" * 60)
    print()
    print("📋 Next Steps:")
    print("1. Review any ❌ items above and fix them")
    print("2. Commit and push to GitHub")
    print("3. Deploy on Render.com")
    print("4. Set environment variables in Render dashboard")
    print()
    print("For detailed instructions, see:")
    print("  - README.md")
    print("  - GITHUB_DEPLOYMENT.md")
    print("  - DEPLOYMENT_CHECKLIST.md")
    print()

if __name__ == "__main__":
    main()
