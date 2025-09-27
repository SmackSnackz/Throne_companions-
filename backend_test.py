import requests
import sys
import json
import time
from datetime import datetime

class ThroneCompanionsAPITester:
    def __init__(self, base_url="https://throne-chat-ai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.companion_ids = ["sophia", "aurora", "vanessa"]
        self.user_token = None
        self.admin_token = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list) and len(response_data) > 0:
                        print(f"   Response: {len(response_data)} items returned")
                    elif isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

            return success, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

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
        """Test JWT token creation for both user and admin"""
        print("\n🔐 Testing JWT Token Creation...")
        
        # Test user token creation
        success, response = self.run_test(
            "Create User Token", 
            "POST", 
            "auth/create-token?email=testuser@example.com&role=user", 
            200
        )
        
        if success and isinstance(response, dict):
            self.user_token = response.get('token')
            print(f"   ✅ User token created: {self.user_token[:20]}...")
            print(f"   Email: {response.get('email')}, Role: {response.get('role')}")
        
        # Test admin token creation
        success, response = self.run_test(
            "Create Admin Token", 
            "POST", 
            "auth/create-token?email=admin@thronecompanions.com&role=admin", 
            200
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
        """Test the new /api/chat endpoint basic functionality"""
        print("\n💬 Testing New Chat Endpoint...")
        
        if not self.user_token:
            print("❌ No user token available for chat testing")
            return False, {}
        
        # Test chat with user token
        headers = {'Authorization': f'Bearer {self.user_token}'}
        test_message = f"Hello! This is a test message at {datetime.now().strftime('%H:%M:%S')}"
        
        # Use query parameters instead of request body
        endpoint = f"chat?companion_id=sophia&message={test_message}&session_id=test_session_basic"
        
        success, response = self.run_test(
            "Chat with User Token", 
            "POST", 
            endpoint, 
            200,
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
        """Test message counting for regular users (should hit limit)"""
        print("\n📊 Testing Message Counting for Regular Users...")
        
        if not self.user_token:
            print("❌ No user token available for message counting test")
            return False, {}
        
        headers = {'Authorization': f'Bearer {self.user_token}'}
        session_id = f"test_session_counting_{int(time.time())}"
        
        # Send multiple messages to test counting
        results = []
        for i in range(25):  # Send more than the 20 message limit
            test_message = f"Test message {i+1}"
            
            # Use query parameters
            endpoint = f"chat?companion_id=sophia&message={test_message}&session_id={session_id}"
            
            success, response = self.run_test(
                f"Message {i+1}/25", 
                "POST", 
                endpoint, 
                200,
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
        """Test admin bypass functionality (unlimited messages)"""
        print("\n👑 Testing Admin Bypass Functionality...")
        
        if not self.admin_token:
            print("❌ No admin token available for bypass testing")
            return False, {}
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        session_id = f"test_session_admin_{int(time.time())}"
        
        # Send multiple messages as admin (should not hit limit)
        results = []
        for i in range(25):  # Send more than the 20 message limit
            test_message = f"Admin test message {i+1}"
            
            # Use query parameters
            endpoint = f"chat?companion_id=aurora&message={test_message}&session_id={session_id}"
            
            success, response = self.run_test(
                f"Admin Message {i+1}/25", 
                "POST", 
                endpoint, 
                200,
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
        """Test session persistence across multiple requests"""
        print("\n🔄 Testing Session Persistence...")
        
        if not self.user_token:
            print("❌ No user token available for session persistence test")
            return False, {}
        
        headers = {'Authorization': f'Bearer {self.user_token}'}
        session_id = f"test_session_persistence_{int(time.time())}"
        
        # Send first message
        success1, response1 = self.run_test(
            "First Message in Session", 
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
            "Second Message in Same Session", 
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
    
    # NEW: Test the new chat endpoint and message tracking functionality
    print("\n" + "🆕 NEW FUNCTIONALITY TESTS" + "=" * 30)
    comprehensive_results = tester.test_chat_endpoint_comprehensive()
    
    # Print comprehensive test results
    print("\n📋 New Functionality Test Results:")
    for test_name, (success, data) in comprehensive_results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    # Check new functionality results
    new_tests_passed = sum(1 for success, _ in comprehensive_results.values() if success)
    new_tests_total = len(comprehensive_results)
    print(f"🆕 New Functionality: {new_tests_passed}/{new_tests_total} tests passed")
    
    if tester.tests_passed == tester.tests_run and new_tests_passed == new_tests_total:
        print("🎉 All tests passed!")
        return 0
    else:
        failed_old = tester.tests_run - tester.tests_passed
        failed_new = new_tests_total - new_tests_passed
        print(f"⚠️  {failed_old + failed_new} tests failed ({failed_old} old, {failed_new} new)")
        return 1

if __name__ == "__main__":
    sys.exit(main())