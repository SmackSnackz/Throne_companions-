import requests
import sys
import json
from datetime import datetime

class ThroneCompanionsAPITester:
    def __init__(self, base_url="https://throne-chat-ai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.companion_ids = ["sophia", "aurora", "vanessa"]

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

def main():
    print("🏰 Starting Throne Companions API Tests")
    print("=" * 50)
    
    tester = ThroneCompanionsAPITester()
    
    # Test API root
    tester.test_api_root()
    
    # Test companions endpoints
    tester.test_get_companions()
    tester.test_get_individual_companions()
    
    # Test messages endpoints
    tester.test_get_companion_messages()
    tester.test_create_chat_message()
    
    # Test error cases
    tester.test_invalid_companion()
    tester.test_invalid_companion_messages()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())