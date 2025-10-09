#!/usr/bin/env python3
"""
Specific test for emergentintegrations LLM functionality as requested in the review.
Tests the key focus areas:
1. Basic API Health Check: GET /api/
2. Tiers Endpoint: GET /api/tiers  
3. JWT Token Creation: POST /api/auth/create-token
4. Chat Endpoint with LLM: POST /api/chat with companion_id="sophia"
5. Memory System Integration: Test memory system endpoints
"""

import requests
import json
import time
from datetime import datetime

class EmergentIntegrationsHealthTest:
    def __init__(self, base_url="https://ai-persona-chat-7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.user_token = None
        self.admin_token = None
        
    def log_test(self, name, success, details=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
        if details:
            print(f"    {details}")
        return success
    
    def test_1_basic_api_health(self):
        """Test 1: Basic API Health Check - GET /api/"""
        print("\n🔍 TEST 1: Basic API Health Check")
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                tiers_available = 'tiers' in data
                message_present = 'message' in data
                details = f"Status: {response.status_code}, Message: {data.get('message', 'N/A')}, Tiers: {tiers_available}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:100]}"
                
            return self.log_test("Basic API Health Check", success, details)
            
        except Exception as e:
            return self.log_test("Basic API Health Check", False, f"Error: {str(e)}")
    
    def test_2_tiers_endpoint(self):
        """Test 2: Tiers Endpoint - GET /api/tiers"""
        print("\n🎯 TEST 2: Tiers Endpoint")
        try:
            response = requests.get(f"{self.api_url}/tiers", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                tier_count = len(data) if isinstance(data, dict) else 0
                tier_names = list(data.keys()) if isinstance(data, dict) else []
                details = f"Status: {response.status_code}, Tiers found: {tier_count} ({', '.join(tier_names)})"
                
                # Verify expected tiers
                expected_tiers = ['novice', 'apprentice', 'regent', 'sovereign']
                missing_tiers = [tier for tier in expected_tiers if tier not in tier_names]
                if missing_tiers:
                    details += f", Missing: {missing_tiers}"
                    success = False
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:100]}"
                
            return self.log_test("Tiers Endpoint", success, details)
            
        except Exception as e:
            return self.log_test("Tiers Endpoint", False, f"Error: {str(e)}")
    
    def test_3_jwt_token_creation(self):
        """Test 3: JWT Token Creation - POST /api/auth/create-token"""
        print("\n🔐 TEST 3: JWT Token Creation")
        try:
            # Test user token creation
            user_response = requests.post(
                f"{self.api_url}/auth/create-token",
                json={"email": "test@example.com", "role": "user"},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            user_success = user_response.status_code == 200
            if user_success:
                user_data = user_response.json()
                self.user_token = user_data.get('token')
                user_details = f"User token created: {self.user_token[:20] if self.user_token else 'None'}..."
            else:
                user_details = f"User token failed: {user_response.status_code} - {user_response.text[:100]}"
            
            # Test admin token creation
            admin_response = requests.post(
                f"{self.api_url}/auth/create-token",
                json={"email": "admin@thronecompanions.com", "role": "admin"},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            admin_success = admin_response.status_code == 200
            if admin_success:
                admin_data = admin_response.json()
                self.admin_token = admin_data.get('token')
                admin_details = f"Admin token created: {self.admin_token[:20] if self.admin_token else 'None'}..."
            else:
                admin_details = f"Admin token failed: {admin_response.status_code} - {admin_response.text[:100]}"
            
            overall_success = user_success and admin_success
            details = f"{user_details} | {admin_details}"
            
            return self.log_test("JWT Token Creation", overall_success, details)
            
        except Exception as e:
            return self.log_test("JWT Token Creation", False, f"Error: {str(e)}")
    
    def test_4_chat_endpoint_llm_integration(self):
        """Test 4: Chat Endpoint with LLM - POST /api/chat with companion_id="sophia" """
        print("\n💬 TEST 4: Chat Endpoint with LLM Integration (companion_id='sophia')")
        
        if not self.user_token:
            return self.log_test("Chat Endpoint LLM Integration", False, "No user token available")
        
        try:
            # Test chat with sophia as requested
            headers = {
                'Authorization': f'Bearer {self.user_token}',
                'Content-Type': 'application/json'
            }
            
            test_message = "Hello Sophia! Can you tell me about yourself and how you can help me today?"
            session_id = f"health_test_{int(time.time())}"
            
            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "companion_id": "sophia",
                    "message": test_message,
                    "session_id": session_id
                },
                headers=headers,
                timeout=30  # Longer timeout for LLM response
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                reply = data.get('reply', '')
                reply_length = len(reply)
                has_meaningful_response = reply_length > 50  # Basic check for meaningful response
                
                # Check for emergentintegrations specific functionality
                response_type = data.get('type', 'unknown')
                session_returned = data.get('session_id', '')
                is_admin = data.get('is_admin', False)
                
                # Verify LLM response quality
                llm_working = (
                    reply_length > 20 and 
                    not reply.startswith("I apologize, but I'm having") and
                    not "technical difficulties" in reply.lower()
                )
                
                details = f"Status: {response.status_code}, Reply length: {reply_length}, LLM working: {llm_working}"
                details += f", Type: {response_type}, Session: {session_returned[:20]}..."
                details += f", Reply preview: '{reply[:100]}...'"
                
                success = success and llm_working
                
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            return self.log_test("Chat Endpoint LLM Integration", success, details)
            
        except Exception as e:
            return self.log_test("Chat Endpoint LLM Integration", False, f"Error: {str(e)}")
    
    def test_5_memory_system_integration(self):
        """Test 5: Memory System Integration"""
        print("\n🧠 TEST 5: Memory System Integration")
        
        if not self.user_token:
            return self.log_test("Memory System Integration", False, "No user token available")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.user_token}',
                'Content-Type': 'application/json'
            }
            
            session_id = f"memory_health_test_{int(time.time())}"
            
            # Send a few messages to create memory
            messages = [
                "I'm feeling excited about learning new things today!",
                "I've been thinking about my personal growth lately.",
                "Thank you for being such a supportive companion."
            ]
            
            chat_success = True
            for i, message in enumerate(messages):
                response = requests.post(
                    f"{self.api_url}/chat",
                    json={
                        "companion_id": "sophia",
                        "message": message,
                        "session_id": session_id,
                        "user_mode": "Friend",
                        "affection_dial": 2
                    },
                    headers=headers,
                    timeout=20
                )
                
                if response.status_code != 200:
                    chat_success = False
                    break
                    
                time.sleep(0.5)  # Small delay between messages
            
            if not chat_success:
                return self.log_test("Memory System Integration", False, "Failed to send chat messages for memory test")
            
            # Test session completion (memory summary generation)
            completion_response = requests.post(
                f"{self.api_url}/session/complete",
                json={
                    "session_id": session_id,
                    "companion_id": "sophia"
                },
                headers=headers,
                timeout=15
            )
            
            completion_success = completion_response.status_code == 200
            
            if completion_success:
                completion_data = completion_response.json()
                status = completion_data.get('status', '')
                summary = completion_data.get('summary', '')
                
                memory_working = (
                    status == 'completed' and 
                    summary and 
                    summary != "No summary generated" and
                    len(summary) > 20
                )
                
                details = f"Status: {completion_response.status_code}, Completion: {status}"
                details += f", Summary generated: {len(summary) > 20}, Summary preview: '{summary[:100]}...'"
                
                success = memory_working
            else:
                details = f"Session completion failed: {completion_response.status_code} - {completion_response.text[:100]}"
                success = False
            
            return self.log_test("Memory System Integration", success, details)
            
        except Exception as e:
            return self.log_test("Memory System Integration", False, f"Error: {str(e)}")
    
    def test_emergentintegrations_no_module_error(self):
        """Verify no ModuleNotFoundError for emergentintegrations"""
        print("\n📦 BONUS TEST: EmergentIntegrations Module Check")
        
        # This test verifies the library is properly imported by checking if chat responses work
        # If there were import errors, the chat endpoint would fail
        
        if not self.user_token:
            return self.log_test("EmergentIntegrations Module Check", False, "No user token available")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.user_token}',
                'Content-Type': 'application/json'
            }
            
            # Simple test message to verify the library is working
            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "companion_id": "sophia",
                    "message": "Quick test - are you working?",
                    "session_id": f"module_test_{int(time.time())}"
                },
                headers=headers,
                timeout=15
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                reply = data.get('reply', '')
                
                # Check if we get a proper LLM response (not a fallback error message)
                no_import_error = (
                    not "ModuleNotFoundError" in reply and
                    not "import" in reply.lower() and
                    not "technical difficulties" in reply.lower() and
                    len(reply) > 10
                )
                
                details = f"Status: {response.status_code}, No import errors: {no_import_error}"
                details += f", Reply: '{reply[:100]}...'"
                
                success = no_import_error
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:100]}"
            
            return self.log_test("EmergentIntegrations Module Check", success, details)
            
        except Exception as e:
            return self.log_test("EmergentIntegrations Module Check", False, f"Error: {str(e)}")

def main():
    print("🏰 EmergentIntegrations Health Test - Throne Companions API")
    print("=" * 70)
    print("Testing key focus areas as requested:")
    print("1. Basic API Health Check")
    print("2. Tiers Endpoint") 
    print("3. JWT Token Creation")
    print("4. Chat Endpoint with LLM (companion_id='sophia')")
    print("5. Memory System Integration")
    print("=" * 70)
    
    tester = EmergentIntegrationsHealthTest()
    
    # Run all tests in sequence
    results = []
    results.append(tester.test_1_basic_api_health())
    results.append(tester.test_2_tiers_endpoint())
    results.append(tester.test_3_jwt_token_creation())
    results.append(tester.test_4_chat_endpoint_llm_integration())
    results.append(tester.test_5_memory_system_integration())
    results.append(tester.test_emergentintegrations_no_module_error())
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 HEALTH TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "Basic API Health Check",
        "Tiers Endpoint", 
        "JWT Token Creation",
        "Chat Endpoint with LLM (sophia)",
        "Memory System Integration",
        "EmergentIntegrations Module Check"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("=" * 70)
    print(f"📊 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - EmergentIntegrations LLM integration is working correctly!")
        print("✅ No ModuleNotFoundError detected")
        print("✅ LLM responses are being generated successfully") 
        print("✅ All core endpoints are responding properly")
        print("✅ Memory system components are functional")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed - Issues detected with EmergentIntegrations integration")
        return 1

if __name__ == "__main__":
    exit(main())