#!/usr/bin/env python3
"""
Throne Companions Backend - Setup Test
This script verifies that all dependencies and configurations are properly set up.
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_python_version():
    """Test Python version"""
    print("Testing Python version...")
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ required. Current:", sys.version)
        return False
    print(f"✓ Python {sys.version.split()[0]} (>= 3.11 required)")
    return True

def test_basic_imports():
    """Test basic Python imports"""
    print("\nTesting basic imports...")
    
    try:
        import fastapi
        print("✓ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import pymongo
        print("✓ PyMongo imported successfully")
    except ImportError as e:
        print(f"❌ PyMongo import failed: {e}")
        return False
    
    try:
        import motor
        print("✓ Motor imported successfully")
    except ImportError as e:
        print(f"❌ Motor import failed: {e}")
        return False
        
    return True

def test_emergent_integration():
    """Test emergentintegrations import"""
    print("\nTesting emergentintegrations...")
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        print("✓ EmergentIntegrations imported successfully")
        return True
    except ImportError as e:
        print(f"❌ EmergentIntegrations import failed: {e}")
        print("   To fix: pip install --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ emergentintegrations")
        return False

def test_environment_variables():
    """Test if environment variables are configured"""
    print("\nTesting environment configuration...")
    
    # Load .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        print("✓ .env file found")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✓ Environment variables loaded from .env")
        except ImportError:
            print("❌ python-dotenv not installed")
            return False
    else:
        print("⚠ .env file not found - using system environment")
    
    required_vars = [
        'MONGO_URL',
        'EMERGENT_LLM_KEY',
        'JWT_SECRET'
    ]
    
    optional_vars = [
        'DB_NAME',
        'CORS_ORIGINS',
        'ADMIN_EMAILS',
        'FREE_TIER_MESSAGE_LIMIT',
        'REDIS_URL'
    ]
    
    missing_required = []
    for var in required_vars:
        if os.environ.get(var):
            print(f"✓ {var} is set")
        else:
            print(f"❌ {var} is missing (required)")
            missing_required.append(var)
    
    for var in optional_vars:
        if os.environ.get(var):
            print(f"✓ {var} is set")
        else:
            print(f"⚠ {var} not set (optional)")
    
    return len(missing_required) == 0

def test_app_structure():
    """Test application module structure"""
    print("\nTesting application structure...")
    
    required_files = [
        'server.py',
        'models.py',
        'auth_utils.py',
        'memory_system.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"✓ {file} found")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)
    
    config_dir = Path('config')
    if config_dir.exists():
        print("✓ config/ directory found")
    else:
        print("❌ config/ directory missing")
        missing_files.append('config/')
    
    return len(missing_files) == 0

def test_app_imports():
    """Test application module imports"""
    print("\nTesting application imports...")
    
    # Set required environment variables for testing
    os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017')
    os.environ.setdefault('DB_NAME', 'test_database')
    os.environ.setdefault('EMERGENT_LLM_KEY', 'test-key')
    os.environ.setdefault('JWT_SECRET', 'test-secret')
    os.environ.setdefault('CORS_ORIGINS', '*')
    
    try:
        import models
        print("✓ models.py imported successfully")
    except Exception as e:
        print(f"❌ models.py import failed: {e}")
        return False
    
    try:
        import auth_utils
        print("✓ auth_utils.py imported successfully")
    except Exception as e:
        print(f"❌ auth_utils.py import failed: {e}")
        return False
    
    try:
        import memory_system
        print("✓ memory_system.py imported successfully")
    except Exception as e:
        print(f"❌ memory_system.py import failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("Throne Companions Backend - Setup Test")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_basic_imports,
        test_emergent_integration,
        test_app_structure,
        test_app_imports,
        test_environment_variables
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Ensure MongoDB is running")
        print("2. Run: python server.py")
        print("3. Visit: http://localhost:8001/docs")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
