#!/usr/bin/env python3
"""
Throne Companions Backend - Health Check
This script performs a comprehensive health check of the running application.
"""

import asyncio
import aiohttp
import sys
import os
from typing import Dict, Any
import json

async def check_server_status(base_url: str) -> Dict[str, Any]:
    """Check if the server is responding"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/api/companions", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "healthy",
                        "response_code": response.status,
                        "companions_count": len(data)
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "response_code": response.status,
                        "error": f"HTTP {response.status}"
                    }
    except Exception as e:
        return {
            "status": "unreachable",
            "error": str(e)
        }

async def check_auth_endpoint(base_url: str) -> Dict[str, Any]:
    """Check authentication endpoint"""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"email": "test@example.com", "role": "user"}
            async with session.post(
                f"{base_url}/api/auth/create-token",
                json=payload,
                timeout=5
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "healthy",
                        "response_code": response.status,
                        "has_token": "token" in data
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "response_code": response.status
                    }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

async def check_ai_functionality(base_url: str) -> Dict[str, Any]:
    """Check AI chat functionality"""
    try:
        # First get a token
        async with aiohttp.ClientSession() as session:
            # Create token
            auth_payload = {"email": "test@example.com", "role": "user"}
            async with session.post(
                f"{base_url}/api/auth/create-token",
                json=auth_payload,
                timeout=5
            ) as auth_response:
                if auth_response.status != 200:
                    return {
                        "status": "auth_failed",
                        "error": "Could not create test token"
                    }
                
                auth_data = await auth_response.json()
                token = auth_data.get("token")
                
                # Test chat endpoint
                chat_payload = {
                    "companion_id": "sophia",
                    "message": "Hello, this is a health check test",
                    "session_id": "health-check-session"
                }
                
                headers = {"Authorization": f"Bearer {token}"}
                async with session.post(
                    f"{base_url}/api/chat",
                    json=chat_payload,
                    headers=headers,
                    timeout=10
                ) as chat_response:
                    if chat_response.status == 200:
                        data = await chat_response.json()
                        return {
                            "status": "healthy",
                            "response_code": chat_response.status,
                            "has_reply": "reply" in data,
                            "ai_response_length": len(data.get("reply", ""))
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "response_code": chat_response.status
                        }
                        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

async def check_database_connection(base_url: str) -> Dict[str, Any]:
    """Check database connectivity through API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/api/tiers", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "healthy",
                        "response_code": response.status,
                        "tiers_loaded": len(data) > 0
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "response_code": response.status
                    }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

async def run_health_checks(base_url: str = "http://localhost:8001"):
    """Run all health checks"""
    print("Throne Companions Backend - Health Check")
    print("=" * 50)
    print(f"Testing server at: {base_url}")
    print()
    
    checks = {
        "Server Status": check_server_status,
        "Authentication": check_auth_endpoint,
        "Database Connection": check_database_connection,
        "AI Functionality": check_ai_functionality
    }
    
    results = {}
    
    for check_name, check_func in checks.items():
        print(f"Testing {check_name}...", end=" ")
        result = await check_func(base_url)
        results[check_name] = result
        
        if result["status"] == "healthy":
            print("✓ Healthy")
        elif result["status"] in ["unhealthy", "error", "unreachable", "auth_failed"]:
            print(f"❌ {result['status'].title()}")
            if "error" in result:
                print(f"   Error: {result['error']}")
        else:
            print(f"⚠ {result['status']}")
    
    print()
    print("Detailed Results:")
    print("=" * 30)
    for check_name, result in results.items():
        print(f"{check_name}: {json.dumps(result, indent=2)}")
        print()
    
    # Overall health assessment
    healthy_count = sum(1 for r in results.values() if r["status"] == "healthy")
    total_count = len(results)
    
    print(f"Overall Health: {healthy_count}/{total_count} checks passed")
    
    if healthy_count == total_count:
        print("✓ All systems operational")
        return True
    elif healthy_count >= total_count * 0.75:
        print("⚠ Most systems operational (minor issues)")
        return True
    else:
        print("❌ Critical issues detected")
        return False

def main():
    """Main entry point"""
    # Allow custom URL via command line
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"
    
    try:
        result = asyncio.run(run_health_checks(base_url))
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\nHealth check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\nHealth check failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
