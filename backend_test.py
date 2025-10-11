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