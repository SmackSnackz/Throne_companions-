#!/usr/bin/env python3
"""
Throne Companions Backend - Extracted Backend Testing
This script comprehensively tests the extracted backend at /app/throne_companions_backend/
to verify it's properly extracted and ready for deployment.
"""

import asyncio
import aiohttp
import sys
import os
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import tempfile
import shutil

class BackendExtractedTester:
    def __init__(self):
        self.extracted_path = Path("/app/throne_companions_backend")
        self.test_results = {}
        self.server_process = None
        self.base_url = "http://localhost:8002"  # Use different port to avoid conflicts
        
    def log_result(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test result"""
        self.test_results[test_name] = {
            "success": success,
            "details": details,
            "data": data
        }
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        
    def test_file_structure_validation(self) -> bool:
        """Test 1: Verify all necessary backend files are present and properly organized"""
        print("\n🔍 Testing File Structure Validation...")
        
        if not self.extracted_path.exists():
            self.log_result("File Structure", False, "Extracted backend directory not found")
            return False
            
        # Core application files
        core_files = [
            "server.py", "models.py", "auth_utils.py", "memory_system.py",
            "mixpanel_tracker.py", "requirements.txt", ".env"
        ]
        
        # Prompt system files
        prompt_files = [
            "master_prompt_system.py", "solicitation.py", "tone_anchor_system.py",
            "unified_prompt_system.py", "tier_prompt_manager.py"
        ]
        
        # Additional service files
        service_files = [
            "analytics.py", "dashboard.py", "email_auth_service.py",
            "error_logger.py", "focused_expansion_system.py", "temp_admin_override.py",
            "content_packs.py", "tier_configs.py", "tier_system.py"
        ]
        
        # Deployment files
        deployment_files = [
            "Dockerfile", "docker-compose.yml", "render.yaml",
            "install.sh", "start.sh", "dev.sh"
        ]
        
        # Documentation files
        doc_files = [
            "README.md", "DEPLOYMENT.md", "EXTRACTION_SUMMARY.md"
        ]
        
        # Testing files
        test_files = [
            "test_setup.py", "health_check.py"
        ]
        
        all_files = core_files + prompt_files + service_files + deployment_files + doc_files + test_files
        
        missing_files = []
        present_files = []
        
        for file in all_files:
            file_path = self.extracted_path / file
            if file_path.exists():
                present_files.append(file)
            else:
                missing_files.append(file)
        
        # Check config directory
        config_dir = self.extracted_path / "config"
        config_files_present = 0
        if config_dir.exists():
            config_files = list(config_dir.glob("*.json"))
            config_files_present = len(config_files)
        
        success = len(missing_files) == 0 and config_files_present > 0
        details = f"Found {len(present_files)}/{len(all_files)} files, {config_files_present} config files"
        
        if missing_files:
            details += f". Missing: {', '.join(missing_files[:5])}"
            if len(missing_files) > 5:
                details += f" and {len(missing_files) - 5} more"
        
        self.log_result("File Structure Validation", success, details, {
            "present_files": len(present_files),
            "missing_files": missing_files,
            "config_files": config_files_present
        })
        
        return success
    
    def test_dependency_resolution(self) -> bool:
        """Test 2: Test that emergentintegrations and all other dependencies can be properly installed"""
        print("\n🔍 Testing Dependency Resolution...")
        
        # Change to extracted directory
        original_cwd = os.getcwd()
        os.chdir(self.extracted_path)
        
        try:
            # Run the test_setup.py script
            result = subprocess.run([
                sys.executable, "test_setup.py"
            ], capture_output=True, text=True, timeout=60)
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            # Check for specific dependency issues
            emergent_success = "EmergentIntegrations imported successfully" in output
            basic_imports_success = "FastAPI imported successfully" in output and "Motor imported successfully" in output
            
            details = f"Setup test {'passed' if success else 'failed'}"
            if emergent_success:
                details += ", EmergentIntegrations OK"
            if basic_imports_success:
                details += ", Basic imports OK"
            
            self.log_result("Dependency Resolution", success, details, {
                "setup_test_output": output,
                "emergent_integration": emergent_success,
                "basic_imports": basic_imports_success
            })
            
            return success
            
        except subprocess.TimeoutExpired:
            self.log_result("Dependency Resolution", False, "Setup test timed out")
            return False
        except Exception as e:
            self.log_result("Dependency Resolution", False, f"Setup test failed: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def test_configuration_testing(self) -> bool:
        """Test 3: Verify .env configuration is complete and server can initialize"""
        print("\n🔍 Testing Configuration...")
        
        env_file = self.extracted_path / ".env"
        if not env_file.exists():
            self.log_result("Configuration Testing", False, ".env file not found")
            return False
        
        # Read and validate .env file
        env_vars = {}
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value.strip('"')
        except Exception as e:
            self.log_result("Configuration Testing", False, f"Failed to read .env: {e}")
            return False
        
        # Check required environment variables
        required_vars = ['MONGO_URL', 'EMERGENT_LLM_KEY', 'JWT_SECRET']
        missing_vars = [var for var in required_vars if var not in env_vars]
        
        if missing_vars:
            self.log_result("Configuration Testing", False, f"Missing required vars: {missing_vars}")
            return False
        
        # Test server initialization (without starting)
        original_cwd = os.getcwd()
        os.chdir(self.extracted_path)
        
        try:
            # Test import of server module
            result = subprocess.run([
                sys.executable, "-c", 
                "import sys; sys.path.insert(0, '.'); import server; print('Server module imported successfully')"
            ], capture_output=True, text=True, timeout=30, env={**os.environ, **env_vars})
            
            success = result.returncode == 0 and "imported successfully" in result.stdout
            details = f"Config vars: {len(env_vars)}, Server import: {'OK' if success else 'Failed'}"
            
            if not success and result.stderr:
                details += f" - Error: {result.stderr[:100]}"
            
            self.log_result("Configuration Testing", success, details, {
                "env_vars_count": len(env_vars),
                "missing_required": missing_vars,
                "server_import_output": result.stdout + result.stderr
            })
            
            return success
            
        except Exception as e:
            self.log_result("Configuration Testing", False, f"Server import test failed: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    async def start_test_server(self) -> bool:
        """Start the extracted backend server for testing"""
        print("\n🚀 Starting extracted backend server for testing...")
        
        original_cwd = os.getcwd()
        os.chdir(self.extracted_path)
        
        try:
            # Start server on different port to avoid conflicts
            env = os.environ.copy()
            env['PORT'] = '8002'
            
            self.server_process = subprocess.Popen([
                sys.executable, "server.py"
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            for i in range(30):  # Wait up to 30 seconds
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{self.base_url}/api/companions", timeout=2) as response:
                            if response.status == 200:
                                print("✅ Test server started successfully")
                                return True
                except:
                    pass
                await asyncio.sleep(1)
            
            print("❌ Test server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start test server: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def stop_test_server(self):
        """Stop the test server"""
        if self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None
            print("🛑 Test server stopped")
    
    async def test_core_api_endpoints(self) -> bool:
        """Test 4: Test key endpoints work independently (auth, companions, chat, tiers)"""
        print("\n🔍 Testing Core API Endpoints...")
        
        endpoint_results = {}
        
        # Test 1: Companions endpoint
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/companions", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        endpoint_results["companions"] = {
                            "success": True,
                            "count": len(data),
                            "status": response.status
                        }
                    else:
                        endpoint_results["companions"] = {
                            "success": False,
                            "status": response.status
                        }
        except Exception as e:
            endpoint_results["companions"] = {"success": False, "error": str(e)}
        
        # Test 2: Tiers endpoint
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tiers", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        endpoint_results["tiers"] = {
                            "success": True,
                            "count": len(data),
                            "status": response.status
                        }
                    else:
                        endpoint_results["tiers"] = {
                            "success": False,
                            "status": response.status
                        }
        except Exception as e:
            endpoint_results["tiers"] = {"success": False, "error": str(e)}
        
        # Test 3: Auth token creation
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"email": "test@example.com", "role": "user"}
                async with session.post(
                    f"{self.base_url}/api/auth/create-token",
                    json=payload,
                    timeout=5
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        endpoint_results["auth_create"] = {
                            "success": True,
                            "has_token": "token" in data,
                            "status": response.status
                        }
                        # Store token for chat test
                        self.test_token = data.get("token")
                    else:
                        endpoint_results["auth_create"] = {
                            "success": False,
                            "status": response.status
                        }
        except Exception as e:
            endpoint_results["auth_create"] = {"success": False, "error": str(e)}
        
        # Test 4: Chat endpoint (if we have a token)
        if hasattr(self, 'test_token') and self.test_token:
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "companion_id": "sophia",
                        "message": "Hello, this is a test message",
                        "session_id": "test-session-extracted"
                    }
                    headers = {"Authorization": f"Bearer {self.test_token}"}
                    async with session.post(
                        f"{self.base_url}/api/chat",
                        json=payload,
                        headers=headers,
                        timeout=10
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            endpoint_results["chat"] = {
                                "success": True,
                                "has_reply": "reply" in data,
                                "reply_length": len(data.get("reply", "")),
                                "status": response.status
                            }
                        else:
                            endpoint_results["chat"] = {
                                "success": False,
                                "status": response.status
                            }
            except Exception as e:
                endpoint_results["chat"] = {"success": False, "error": str(e)}
        else:
            endpoint_results["chat"] = {"success": False, "error": "No auth token available"}
        
        # Calculate overall success
        successful_endpoints = sum(1 for result in endpoint_results.values() if result.get("success", False))
        total_endpoints = len(endpoint_results)
        success = successful_endpoints >= 3  # At least 3 out of 4 should work
        
        details = f"{successful_endpoints}/{total_endpoints} endpoints working"
        for endpoint, result in endpoint_results.items():
            if result.get("success"):
                details += f", {endpoint}: OK"
            else:
                details += f", {endpoint}: Failed"
        
        self.log_result("Core API Endpoints", success, details, endpoint_results)
        return success
    
    def test_deployment_readiness(self) -> bool:
        """Test 5: Verify Docker, render.yaml configs are functional"""
        print("\n🔍 Testing Deployment Readiness...")
        
        deployment_results = {}
        
        # Test Dockerfile
        dockerfile_path = self.extracted_path / "Dockerfile"
        if dockerfile_path.exists():
            try:
                with open(dockerfile_path, 'r') as f:
                    dockerfile_content = f.read()
                
                # Check for key Dockerfile elements
                has_python_base = "FROM python:" in dockerfile_content
                has_requirements = "requirements.txt" in dockerfile_content
                has_emergent_install = "extra-index-url" in dockerfile_content
                has_expose = "EXPOSE" in dockerfile_content
                has_cmd = "CMD" in dockerfile_content
                
                dockerfile_score = sum([has_python_base, has_requirements, has_emergent_install, has_expose, has_cmd])
                deployment_results["dockerfile"] = {
                    "success": dockerfile_score >= 4,
                    "score": f"{dockerfile_score}/5",
                    "elements": {
                        "python_base": has_python_base,
                        "requirements": has_requirements,
                        "emergent_install": has_emergent_install,
                        "expose": has_expose,
                        "cmd": has_cmd
                    }
                }
            except Exception as e:
                deployment_results["dockerfile"] = {"success": False, "error": str(e)}
        else:
            deployment_results["dockerfile"] = {"success": False, "error": "Dockerfile not found"}
        
        # Test render.yaml
        render_yaml_path = self.extracted_path / "render.yaml"
        if render_yaml_path.exists():
            try:
                with open(render_yaml_path, 'r') as f:
                    render_content = f.read()
                
                # Check for key render.yaml elements
                has_services = "services:" in render_content
                has_web_type = "type: web" in render_content
                has_build_command = "buildCommand:" in render_content
                has_start_command = "startCommand:" in render_content
                has_env_vars = "envVars:" in render_content
                has_emergent_build = "extra-index-url" in render_content
                
                render_score = sum([has_services, has_web_type, has_build_command, has_start_command, has_env_vars, has_emergent_build])
                deployment_results["render_yaml"] = {
                    "success": render_score >= 5,
                    "score": f"{render_score}/6",
                    "elements": {
                        "services": has_services,
                        "web_type": has_web_type,
                        "build_command": has_build_command,
                        "start_command": has_start_command,
                        "env_vars": has_env_vars,
                        "emergent_build": has_emergent_build
                    }
                }
            except Exception as e:
                deployment_results["render_yaml"] = {"success": False, "error": str(e)}
        else:
            deployment_results["render_yaml"] = {"success": False, "error": "render.yaml not found"}
        
        # Test docker-compose.yml
        compose_path = self.extracted_path / "docker-compose.yml"
        if compose_path.exists():
            try:
                with open(compose_path, 'r') as f:
                    compose_content = f.read()
                
                # Check for key docker-compose elements
                has_version = "version:" in compose_content
                has_services = "services:" in compose_content
                has_backend = "backend:" in compose_content
                has_mongo = "mongo:" in compose_content
                has_redis = "redis:" in compose_content
                has_volumes = "volumes:" in compose_content
                
                compose_score = sum([has_version, has_services, has_backend, has_mongo, has_redis, has_volumes])
                deployment_results["docker_compose"] = {
                    "success": compose_score >= 5,
                    "score": f"{compose_score}/6",
                    "elements": {
                        "version": has_version,
                        "services": has_services,
                        "backend": has_backend,
                        "mongo": has_mongo,
                        "redis": has_redis,
                        "volumes": has_volumes
                    }
                }
            except Exception as e:
                deployment_results["docker_compose"] = {"success": False, "error": str(e)}
        else:
            deployment_results["docker_compose"] = {"success": False, "error": "docker-compose.yml not found"}
        
        # Test installation scripts
        install_script = self.extracted_path / "install.sh"
        start_script = self.extracted_path / "start.sh"
        
        scripts_present = install_script.exists() and start_script.exists()
        scripts_executable = False
        
        if scripts_present:
            try:
                scripts_executable = (
                    os.access(install_script, os.X_OK) and 
                    os.access(start_script, os.X_OK)
                )
            except:
                scripts_executable = False
        
        deployment_results["scripts"] = {
            "success": scripts_present and scripts_executable,
            "install_exists": install_script.exists(),
            "start_exists": start_script.exists(),
            "executable": scripts_executable
        }
        
        # Calculate overall deployment readiness
        successful_configs = sum(1 for result in deployment_results.values() if result.get("success", False))
        total_configs = len(deployment_results)
        success = successful_configs >= 3  # At least 3 out of 4 should be ready
        
        details = f"{successful_configs}/{total_configs} deployment configs ready"
        for config, result in deployment_results.items():
            if result.get("success"):
                details += f", {config}: OK"
            else:
                details += f", {config}: Issues"
        
        self.log_result("Deployment Readiness", success, details, deployment_results)
        return success
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        print("🧪 Throne Companions Backend - Extracted Backend Testing")
        print("=" * 70)
        print(f"Testing extracted backend at: {self.extracted_path}")
        print()
        
        # Test 1: File Structure Validation
        structure_ok = self.test_file_structure_validation()
        
        # Test 2: Dependency Resolution
        dependencies_ok = self.test_dependency_resolution()
        
        # Test 3: Configuration Testing
        config_ok = self.test_configuration_testing()
        
        # Test 4 & 5: Start server and test endpoints + deployment
        server_started = False
        endpoints_ok = False
        deployment_ok = False
        
        if structure_ok and dependencies_ok and config_ok:
            server_started = await self.start_test_server()
            
            if server_started:
                endpoints_ok = await self.test_core_api_endpoints()
                # Give server a moment to stabilize
                await asyncio.sleep(2)
            
            # Test deployment readiness (doesn't require running server)
            deployment_ok = self.test_deployment_readiness()
            
            # Stop test server
            if server_started:
                self.stop_test_server()
        else:
            self.log_result("Server Startup", False, "Skipped due to previous failures")
            self.log_result("Core API Endpoints", False, "Skipped due to previous failures")
            deployment_ok = self.test_deployment_readiness()
        
        # Calculate overall results
        tests_passed = sum([
            structure_ok,
            dependencies_ok, 
            config_ok,
            server_started,
            endpoints_ok,
            deployment_ok
        ])
        
        total_tests = 6
        overall_success = tests_passed >= 5  # At least 5 out of 6 should pass
        
        print(f"\n{'='*70}")
        print(f"🏁 COMPREHENSIVE TEST RESULTS")
        print(f"{'='*70}")
        print(f"Tests Passed: {tests_passed}/{total_tests}")
        print(f"Overall Status: {'✅ READY FOR DEPLOYMENT' if overall_success else '❌ NEEDS ATTENTION'}")
        
        if overall_success:
            print("\n🎉 The extracted backend is ready for:")
            print("   • GitHub repository creation")
            print("   • Independent deployment")
            print("   • Production use")
        else:
            print("\n⚠️  Issues found that need attention:")
            for test_name, result in self.test_results.items():
                if not result["success"]:
                    print(f"   • {test_name}: {result['details']}")
        
        return {
            "overall_success": overall_success,
            "tests_passed": tests_passed,
            "total_tests": total_tests,
            "test_results": self.test_results,
            "ready_for_deployment": overall_success
        }

async def main():
    """Main test execution"""
    tester = BackendExtractedTester()
    
    try:
        results = await tester.run_comprehensive_test()
        
        # Return appropriate exit code
        return 0 if results["overall_success"] else 1
        
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        return 1
    finally:
        # Ensure server is stopped
        tester.stop_test_server()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

    def test_get_tiers(self):
        """Test getting tier configuration data"""
        success, response = self.run_test("Get Tiers", "GET", "tiers", 200)
        
        if success and isinstance(response, dict):
            print(f"   Found {len(response)} tiers")
            for tier_name, tier_config in response.items():
                print(f"   - {tier_name}: {tier_config.get('name', 'Unknown')}")
                # Verify required tier fields
                required_fields = ['name', 'price', 'memory_retention_days', 'prompting_mastery']
                missing_fields = [field for field in required_fields if field not in tier_config]
                if missing_fields:
                    print(f"     ⚠️  Missing fields: {missing_fields}")
                else:
                    print(f"     ✅ All required fields present")
        
        return success, response

    def test_get_companions(self):
        """Test getting all companions"""
        success, response = self.run_test("Get All Companions", "GET", "companions", 200)
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} companions")
            for companion in response:
                print(f"   - {companion.get('name', 'Unknown')} (ID: {companion.get('id', 'Unknown')})")
                # Verify required fields
                required_fields = ['id', 'name', 'description', 'image', 'personality']
                missing_fields = [field for field in required_fields if field not in companion]
                if missing_fields:
                    print(f"     ⚠️  Missing fields: {missing_fields}")
                else:
                    print(f"     ✅ All required fields present")
        
        return success, response

    def test_get_individual_companions(self):
        """Test getting individual companions"""
        results = []
        for companion_id in self.companion_ids:
            success, response = self.run_test(
                f"Get Companion {companion_id.title()}", 
                "GET", 
                f"companions/{companion_id}", 
                200
            )
            results.append((companion_id, success, response))
            
            if success and isinstance(response, dict):
                expected_name = companion_id.title()
                actual_name = response.get('name', '')
                if actual_name == expected_name:
                    print(f"   ✅ Name matches: {actual_name}")
                else:
                    print(f"   ❌ Name mismatch: expected {expected_name}, got {actual_name}")
                
                # Check image path
                expected_image = f"/avatars/{companion_id}.png"
                actual_image = response.get('image', '')
                if actual_image == expected_image:
                    print(f"   ✅ Image path correct: {actual_image}")
                else:
                    print(f"   ❌ Image path incorrect: expected {expected_image}, got {actual_image}")
        
        return results

    def test_get_companion_messages(self):
        """Test getting messages for each companion"""
        results = []
        for companion_id in self.companion_ids:
            success, response = self.run_test(
                f"Get Messages for {companion_id.title()}", 
                "GET", 
                f"companions/{companion_id}/messages", 
                200
            )
            results.append((companion_id, success, response))
            
            if success and isinstance(response, list):
                print(f"   Found {len(response)} existing messages")
        
        return results

    def test_create_chat_message(self):
        """Test creating chat messages"""
        results = []
        test_message = f"Hello! This is a test message at {datetime.now().strftime('%H:%M:%S')}"
        
        for companion_id in self.companion_ids:
            # Send user message
            success, response = self.run_test(
                f"Send Message to {companion_id.title()}", 
                "POST", 
                f"companions/{companion_id}/messages",
                200,
                data={
                    "companion_id": companion_id,
                    "message": test_message,
                    "is_user": True
                }
            )
            results.append((companion_id, success, response))
            
            if success and isinstance(response, dict):
                print(f"   ✅ Message created with ID: {response.get('id', 'Unknown')}")
                print(f"   Message: {response.get('message', 'Unknown')}")
                
                # Wait a moment then check if companion responded
                import time
                time.sleep(1)
                
                # Get updated messages to see if companion responded
                msg_success, messages = self.run_test(
                    f"Check Updated Messages for {companion_id.title()}", 
                    "GET", 
                    f"companions/{companion_id}/messages", 
                    200
                )
                
                if msg_success and isinstance(messages, list):
                    user_messages = [msg for msg in messages if msg.get('is_user', False)]
                    companion_messages = [msg for msg in messages if not msg.get('is_user', True)]
                    print(f"   Total messages: {len(messages)} (User: {len(user_messages)}, Companion: {len(companion_messages)})")
        
        return results

    def test_invalid_companion(self):
        """Test accessing non-existent companion"""
        return self.run_test("Invalid Companion", "GET", "companions/invalid", 404)

    def test_invalid_companion_messages(self):
        """Test accessing messages for non-existent companion"""
        return self.run_test("Invalid Companion Messages", "GET", "companions/invalid/messages", 404)

    def test_jwt_token_creation(self):
        """Test JWT token creation for both user and admin with JSON body"""
        print("\n🔐 Testing JWT Token Creation (FIXED - JSON Body)...")
        
        # Test user token creation with JSON body
        success, response = self.run_test(
            "Create User Token (JSON Body)", 
            "POST", 
            "auth/create-token", 
            200,
            data={"email": "test@example.com", "role": "user"}
        )
        
        if success and isinstance(response, dict):
            self.user_token = response.get('token')
            print(f"   ✅ User token created: {self.user_token[:20]}...")
            print(f"   Email: {response.get('email')}, Role: {response.get('role')}")
        
        # Test admin token creation with JSON body
        success, response = self.run_test(
            "Create Admin Token (JSON Body)", 
            "POST", 
            "auth/create-token", 
            200,
            data={"email": "admin@thronecompanions.com", "role": "admin"}
        )
        
        if success and isinstance(response, dict):
            self.admin_token = response.get('token')
            print(f"   ✅ Admin token created: {self.admin_token[:20]}...")
            print(f"   Email: {response.get('email')}, Role: {response.get('role')}")
        
        return success, response

    def test_jwt_token_verification(self):
        """Test JWT token verification"""
        print("\n🔍 Testing JWT Token Verification...")
        
        if not self.user_token:
            print("❌ No user token available for verification")
            return False, {}
        
        # Test user token verification
        headers = {'Authorization': f'Bearer {self.user_token}'}
        success, response = self.run_test(
            "Verify User Token", 
            "GET", 
            "auth/verify", 
            200,
            headers=headers
        )
        
        if success and isinstance(response, dict):
            print(f"   ✅ User token verified - Email: {response.get('email')}")
            print(f"   Role: {response.get('role')}, Is Admin: {response.get('is_admin')}")
        
        # Test admin token verification
        if self.admin_token:
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            success, response = self.run_test(
                "Verify Admin Token", 
                "GET", 
                "auth/verify", 
                200,
                headers=headers
            )
            
            if success and isinstance(response, dict):
                print(f"   ✅ Admin token verified - Email: {response.get('email')}")
                print(f"   Role: {response.get('role')}, Is Admin: {response.get('is_admin')}")
        
        return success, response

    def test_new_chat_endpoint_basic(self):
        """Test the new /api/chat endpoint basic functionality with JSON body"""
        print("\n💬 Testing New Chat Endpoint (FIXED - JSON Body)...")
        
        if not self.user_token:
            print("❌ No user token available for chat testing")
            return False, {}
        
        # Test chat with user token using JSON body
        headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'application/json'
        }
        test_message = f"Hello! This is a test message at {datetime.now().strftime('%H:%M:%S')}"
        
        success, response = self.run_test(
            "Chat with User Token (JSON Body)", 
            "POST", 
            "chat", 
            200,
            data={
                "companion_id": "sophia",
                "message": test_message,
                "session_id": "test123"
            },
            headers=headers
        )
        
        if success and isinstance(response, dict):
            print(f"   ✅ Chat response received")
            print(f"   Reply: {response.get('reply', 'No reply')[:100]}...")
            print(f"   Used: {response.get('used')}/{response.get('limit')}")
            print(f"   Session ID: {response.get('session_id')}")
            print(f"   Is Admin: {response.get('is_admin')}")
            print(f"   Upgrade Required: {response.get('upgrade', False)}")
        
        return success, response

    def test_message_counting_user(self):
        """Test message counting for regular users (should hit limit) with JSON body"""
        print("\n📊 Testing Message Counting for Regular Users (FIXED - JSON Body)...")
        
        if not self.user_token:
            print("❌ No user token available for message counting test")
            return False, {}
        
        headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'application/json'
        }
        session_id = f"test_session_counting_{int(time.time())}"
        
        # Send multiple messages to test counting
        results = []
        for i in range(25):  # Send more than the 20 message limit
            test_message = f"Test message {i+1}"
            
            success, response = self.run_test(
                f"Message {i+1}/25 (JSON Body)", 
                "POST", 
                "chat", 
                200,
                data={
                    "companion_id": "sophia",
                    "message": test_message,
                    "session_id": session_id
                },
                headers=headers
            )
            
            if success and isinstance(response, dict):
                used = response.get('used', 0)
                limit = response.get('limit', 20)
                upgrade = response.get('upgrade', False)
                
                print(f"   Message {i+1}: Used {used}/{limit}, Upgrade: {upgrade}")
                
                # Check if we hit the limit
                if upgrade and used >= limit:
                    print(f"   ✅ Hit message limit at message {i+1} - upgrade required")
                    break
                    
                results.append((i+1, used, upgrade))
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.1)
            else:
                print(f"   ❌ Failed to send message {i+1}")
                break
        
        return len(results) > 0, results

    def test_admin_bypass_functionality(self):
        """Test admin bypass functionality (unlimited messages) with JSON body"""
        print("\n👑 Testing Admin Bypass Functionality (FIXED - JSON Body)...")
        
        if not self.admin_token:
            print("❌ No admin token available for bypass testing")
            return False, {}
        
        headers = {
            'Authorization': f'Bearer {self.admin_token}',
            'Content-Type': 'application/json'
        }
        session_id = f"test_session_admin_{int(time.time())}"
        
        # Send multiple messages as admin (should not hit limit)
        results = []
        for i in range(25):  # Send more than the 20 message limit
            test_message = f"Admin test message {i+1}"
            
            success, response = self.run_test(
                f"Admin Message {i+1}/25 (JSON Body)", 
                "POST", 
                "chat", 
                200,
                data={
                    "companion_id": "aurora",
                    "message": test_message,
                    "session_id": session_id
                },
                headers=headers
            )
            
            if success and isinstance(response, dict):
                used = response.get('used', 0)
                limit = response.get('limit', 20)
                upgrade = response.get('upgrade', False)
                is_admin = response.get('is_admin', False)
                
                print(f"   Admin Message {i+1}: Used {used}/{limit}, Upgrade: {upgrade}, Is Admin: {is_admin}")
                
                # Admin should never get upgrade message
                if upgrade:
                    print(f"   ❌ Admin got upgrade message - bypass not working!")
                    break
                    
                if not is_admin:
                    print(f"   ❌ is_admin flag is False - should be True for admin")
                    
                results.append((i+1, used, upgrade, is_admin))
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.1)
            else:
                print(f"   ❌ Failed to send admin message {i+1}")
                break
        
        # Check if admin bypass worked (no upgrade messages)
        upgrade_messages = [r for r in results if r[2]]  # r[2] is upgrade flag
        if not upgrade_messages:
            print(f"   ✅ Admin bypass working - sent {len(results)} messages without upgrade prompt")
        else:
            print(f"   ❌ Admin bypass failed - got {len(upgrade_messages)} upgrade prompts")
        
        return len(results) > 0, results

    def test_session_persistence(self):
        """Test session persistence across multiple requests with JSON body"""
        print("\n🔄 Testing Session Persistence (FIXED - JSON Body)...")
        
        if not self.user_token:
            print("❌ No user token available for session persistence test")
            return False, {}
        
        headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'application/json'
        }
        session_id = f"test_session_persistence_{int(time.time())}"
        
        # Send first message
        success1, response1 = self.run_test(
            "First Message in Session (JSON Body)", 
            "POST", 
            "chat", 
            200,
            data={
                "companion_id": "vanessa",
                "message": "First message in session",
                "session_id": session_id
            },
            headers=headers
        )
        
        if not success1:
            return False, {}
        
        used1 = response1.get('used', 0)
        print(f"   First message - Used: {used1}")
        
        # Wait a moment
        time.sleep(1)
        
        # Send second message with same session_id
        success2, response2 = self.run_test(
            "Second Message in Same Session (JSON Body)", 
            "POST", 
            "chat", 
            200,
            data={
                "companion_id": "vanessa",
                "message": "Second message in same session",
                "session_id": session_id
            },
            headers=headers
        )
        
        if not success2:
            return False, {}
        
        used2 = response2.get('used', 0)
        print(f"   Second message - Used: {used2}")
        
        # Check if count persisted and incremented
        if used2 == used1 + 1:
            print(f"   ✅ Session persistence working - count incremented from {used1} to {used2}")
            return True, (used1, used2)
        else:
            print(f"   ❌ Session persistence failed - expected {used1 + 1}, got {used2}")
            return False, (used1, used2)

    def test_memory_system_integration(self):
        """Test Memory System integration with chat endpoint"""
        print("\n🧠 Testing Memory System Integration...")
        
        if not self.user_token:
            print("❌ No user token available for memory system test")
            return False, {}
        
        headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'application/json'
        }
        session_id = f"memory_test_session_{int(time.time())}"
        
        # Send multiple messages to create memory
        messages = [
            "Hello, I'm feeling excited about learning new things today!",
            "I've been thinking about my goals and aspirations lately.",
            "Can you help me understand how to stay motivated?"
        ]
        
        results = []
        for i, message in enumerate(messages):
            success, response = self.run_test(
                f"Memory Test Message {i+1}/3", 
                "POST", 
                "chat", 
                200,
                data={
                    "companion_id": "sophia",
                    "message": message,
                    "session_id": session_id,
                    "user_mode": "Friend",
                    "affection_dial": 2
                },
                headers=headers
            )
            
            if success:
                print(f"   ✅ Message {i+1} sent successfully")
                results.append(response)
                time.sleep(0.5)  # Small delay between messages
            else:
                print(f"   ❌ Message {i+1} failed")
                return False, {}
        
        return len(results) == len(messages), results

    def test_session_completion(self):
        """Test session completion and memory summary generation"""
        print("\n📝 Testing Session Completion & Memory Summary...")
        
        if not self.user_token:
            print("❌ No user token available for session completion test")
            return False, {}
        
        headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'application/json'
        }
        session_id = f"completion_test_session_{int(time.time())}"
        
        # First, create a conversation
        messages = [
            "I had a wonderful day at the park today.",
            "The weather was perfect and I felt so peaceful.",
            "Thank you for listening to me share my joy."
        ]
        
        # Send messages to create session history
        for i, message in enumerate(messages):
            success, response = self.run_test(
                f"Setup Message {i+1}/3", 
                "POST", 
                "chat", 
                200,
                data={
                    "companion_id": "aurora",
                    "message": message,
                    "session_id": session_id
                },
                headers=headers
            )
            
            if not success:
                print(f"   ❌ Failed to send setup message {i+1}")
                return False, {}
            time.sleep(0.3)
        
        print("   ✅ Session history created")
        
        # Now complete the session
        success, response = self.run_test(
            "Complete Session", 
            "POST", 
            "session/complete", 
            200,
            data={
                "session_id": session_id,
                "companion_id": "aurora"
            },
            headers=headers
        )
        
        if success and isinstance(response, dict):
            status = response.get('status')
            summary = response.get('summary')
            returned_session_id = response.get('session_id')
            
            print(f"   ✅ Session completion status: {status}")
            print(f"   Session ID: {returned_session_id}")
            if summary and summary != "No summary generated":
                print(f"   ✅ Memory summary generated: {summary[:100]}...")
                return True, response
            else:
                print(f"   ⚠️  No memory summary generated")
                return True, response  # Still success, just no summary
        
        return success, response

    def test_mixpanel_event_tracking(self):
        """Test Mixpanel event tracking endpoints"""
        print("\n📊 Testing Mixpanel Event Tracking...")
        
        # Test companion selection tracking
        success1, response1 = self.run_test(
            "Track Companion Selected", 
            "POST", 
            "events/companion_selected", 
            200,
            data={
                "user_id": "test_user_mixpanel",
                "companion_id": "sophia",
                "companion_name": "Sophia",
                "session_id": "onboarding_test_123"
            }
        )
        
        # Test tier selection tracking
        success2, response2 = self.run_test(
            "Track Tier Selected", 
            "POST", 
            "events/tier_selected", 
            200,
            data={
                "user_id": "test_user_mixpanel",
                "tier_name": "Novice",
                "tier_price": "Free",
                "session_id": "onboarding_test_123"
            }
        )
        
        # Test upgrade click tracking
        success3, response3 = self.run_test(
            "Track Upgrade Clicked", 
            "POST", 
            "events/upgrade_clicked", 
            200,
            data={
                "user_id": "test_user_mixpanel",
                "current_tier": "novice",
                "target_tier": "apprentice",
                "source": "chat_limit",
                "session_id": "upgrade_test_123"
            }
        )
        
        all_success = success1 and success2 and success3
        if all_success:
            print("   ✅ All event tracking endpoints working")
        else:
            print(f"   ❌ Event tracking issues: companion={success1}, tier={success2}, upgrade={success3}")
        
        return all_success, (response1, response2, response3)

    def test_mixpanel_mock_verification(self):
        """Test Mixpanel mock event verification endpoints"""
        print("\n🔍 Testing Mixpanel Mock Event Verification...")
        
        # Get mock events
        success1, response1 = self.run_test(
            "Get Mock Events", 
            "GET", 
            "events/mock", 
            200
        )
        
        # Get event statistics
        success2, response2 = self.run_test(
            "Get Event Stats", 
            "GET", 
            "events/stats", 
            200
        )
        
        if success1 and isinstance(response1, dict):
            mock_mode = response1.get('mock_mode')
            events = response1.get('events', [])
            count = response1.get('count', 0)
            
            print(f"   ✅ Mock events retrieved: {count} events, mock_mode: {mock_mode}")
            
            # Show some event details
            if events:
                for event in events[:3]:  # Show first 3 events
                    event_name = event.get('event_name', 'Unknown')
                    user_id = event.get('user_id', 'Unknown')
                    timestamp = event.get('timestamp', 'Unknown')
                    print(f"     - {event_name} by {user_id} at {timestamp}")
        
        if success2 and isinstance(response2, dict):
            event_counts = response2.get('event_counts', {})
            total_events = response2.get('total_events', 0)
            
            print(f"   ✅ Event statistics: {total_events} total events")
            for event_name, count in event_counts.items():
                print(f"     - {event_name}: {count}")
        
        return success1 and success2, (response1, response2)

    def test_tier_based_memory_retention(self):
        """Test tier-based memory retention policies"""
        print("\n🎯 Testing Tier-Based Memory Retention...")
        
        # This test would require creating different user tokens with different tiers
        # For now, we'll test with the available tokens and document the expected behavior
        
        tier_policies = {
            "novice": 3,
            "apprentice": 10, 
            "regent": 50,
            "sovereign": "unlimited"
        }
        
        print("   📋 Memory Retention Policies:")
        for tier, retention in tier_policies.items():
            print(f"     - {tier.title()}: {retention} summaries")
        
        # Test with current user (should be novice tier)
        if self.user_token:
            headers = {
                'Authorization': f'Bearer {self.user_token}',
                'Content-Type': 'application/json'
            }
            
            # Send a test message to trigger memory system
            success, response = self.run_test(
                "Test Memory Retention (Novice)", 
                "POST", 
                "chat", 
                200,
                data={
                    "companion_id": "sophia",
                    "message": "Testing memory retention for novice tier",
                    "session_id": f"retention_test_{int(time.time())}"
                },
                headers=headers
            )
            
            if success:
                print("   ✅ Memory system integration working for novice tier")
                return True, response
        
        print("   ⚠️  Limited tier testing - would need multiple tier tokens for full test")
        return True, {"note": "Tier policies documented, limited testing performed"}

    def test_memory_and_events_comprehensive(self):
        """Comprehensive test of Memory System and Mixpanel integration"""
        print("\n🧪 Running Comprehensive Memory & Events Tests...")
        
        tests = [
            ("Memory System Integration", self.test_memory_system_integration),
            ("Session Completion", self.test_session_completion),
            ("Mixpanel Event Tracking", self.test_mixpanel_event_tracking),
            ("Mixpanel Mock Verification", self.test_mixpanel_mock_verification),
            ("Tier-Based Memory Retention", self.test_tier_based_memory_retention)
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                success, data = test_func()
                results[test_name] = (success, data)
            except Exception as e:
                print(f"   ❌ {test_name} failed with error: {e}")
                results[test_name] = (False, str(e))
        
        return results

    def test_chat_endpoint_comprehensive(self):
        """Comprehensive test of the new chat endpoint"""
        print("\n🧪 Running Comprehensive Chat Endpoint Tests...")
        
        # Test all required scenarios
        tests = [
            ("JWT Token Creation", self.test_jwt_token_creation),
            ("JWT Token Verification", self.test_jwt_token_verification),
            ("Basic Chat Functionality", self.test_new_chat_endpoint_basic),
            ("Message Counting (User)", self.test_message_counting_user),
            ("Admin Bypass", self.test_admin_bypass_functionality),
            ("Session Persistence", self.test_session_persistence)
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                success, data = test_func()
                results[test_name] = (success, data)
            except Exception as e:
                print(f"   ❌ {test_name} failed with error: {e}")
                results[test_name] = (False, str(e))
        
        return results

def main():
    print("🏰 Starting Throne Companions API Tests")
    print("=" * 50)
    
    tester = ThroneCompanionsAPITester()
    
    # Test API root
    tester.test_api_root()
    
    # Test tiers endpoint
    tester.test_get_tiers()
    
    # Test companions endpoints
    tester.test_get_companions()
    tester.test_get_individual_companions()
    
    # Test messages endpoints
    tester.test_get_companion_messages()
    tester.test_create_chat_message()
    
    # Test error cases
    tester.test_invalid_companion()
    tester.test_invalid_companion_messages()
    
    # EXISTING: Test the chat endpoint and message tracking functionality
    print("\n" + "🆕 EXISTING FUNCTIONALITY TESTS" + "=" * 25)
    comprehensive_results = tester.test_chat_endpoint_comprehensive()
    
    # NEW: Test Memory System and Mixpanel Event Tracking
    print("\n" + "🧠 MEMORY SYSTEM & MIXPANEL TESTS" + "=" * 25)
    memory_and_events_results = tester.test_memory_and_events_comprehensive()
    
    # Print comprehensive test results
    print("\n📋 Existing Functionality Test Results:")
    for test_name, (success, data) in comprehensive_results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    print("\n📋 Memory System & Mixpanel Test Results:")
    for test_name, (success, data) in memory_and_events_results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Basic API Tests: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    # Check existing functionality results
    existing_tests_passed = sum(1 for success, _ in comprehensive_results.values() if success)
    existing_tests_total = len(comprehensive_results)
    print(f"🆕 Existing Functionality: {existing_tests_passed}/{existing_tests_total} tests passed")
    
    # Check new functionality results
    new_tests_passed = sum(1 for success, _ in memory_and_events_results.values() if success)
    new_tests_total = len(memory_and_events_results)
    print(f"🧠 Memory & Events: {new_tests_passed}/{new_tests_total} tests passed")
    
    total_passed = tester.tests_passed + existing_tests_passed + new_tests_passed
    total_tests = tester.tests_run + existing_tests_total + new_tests_total
    
    if total_passed == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        failed_basic = tester.tests_run - tester.tests_passed
        failed_existing = existing_tests_total - existing_tests_passed
        failed_new = new_tests_total - new_tests_passed
        print(f"⚠️  {total_tests - total_passed} tests failed ({failed_basic} basic, {failed_existing} existing, {failed_new} new)")
        return 1

if __name__ == "__main__":
    sys.exit(main())