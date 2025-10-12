#!/bin/bash
# Test script to verify deployment readiness

echo "🧪 Testing Deployment Readiness"
echo "================================"

# Test 1: Check if emergentintegrations is installable
echo ""
echo "Test 1: Checking emergentintegrations package..."
pip index versions emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Package accessible from custom index"
else
    echo "❌ Package NOT accessible"
    exit 1
fi

# Test 2: Check if package is installed
echo ""
echo "Test 2: Verifying package installation..."
pip show emergentintegrations > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Package installed successfully"
    pip show emergentintegrations | grep "Version:"
else
    echo "❌ Package NOT installed"
    exit 1
fi

# Test 3: Test imports
echo ""
echo "Test 3: Testing Python imports..."
python3 -c "from emergentintegrations.llm.chat import LlmChat, UserMessage; print('✅ Imports successful')" 2>&1
if [ $? -eq 0 ]; then
    echo "✅ All imports working"
else
    echo "❌ Import errors detected"
    exit 1
fi

# Test 4: Check Dockerfile
echo ""
echo "Test 4: Verifying Dockerfile configuration..."
if grep -q "extra-index-url.*d33sy5i8bnduwe.cloudfront.net" /app/Dockerfile; then
    echo "✅ Dockerfile has correct custom index URL"
else
    echo "❌ Dockerfile missing custom index URL"
    exit 1
fi

# Test 5: Check render.yaml
echo ""
echo "Test 5: Verifying render.yaml configuration..."
if grep -q "extra-index-url.*d33sy5i8bnduwe.cloudfront.net" /app/render.yaml; then
    echo "✅ render.yaml has correct custom index URL"
else
    echo "❌ render.yaml missing custom index URL"
    exit 1
fi

# Test 6: Check requirements.txt
echo ""
echo "Test 6: Verifying requirements.txt..."
if grep -q "emergentintegrations==0.1.0" /app/backend/requirements.txt; then
    echo "✅ emergentintegrations in requirements.txt"
else
    echo "❌ emergentintegrations missing from requirements.txt"
    exit 1
fi

# Test 7: Test backend server imports
echo ""
echo "Test 7: Testing backend server module imports..."
cd /app/backend && python3 -c "
import sys
sys.path.insert(0, '/app/backend')
from emergentintegrations.llm.chat import LlmChat, UserMessage
import server
from memory_system import MemorySystem
from unified_prompt_system import UnifiedPromptSystem
from master_prompt_system import MasterPromptSystem
print('✅ All server modules import successfully')
" 2>&1 | grep "✅"

if [ $? -eq 0 ]; then
    echo "✅ Backend server ready for deployment"
else
    echo "❌ Backend server has import issues"
    exit 1
fi

echo ""
echo "================================"
echo "🎉 All Deployment Tests Passed!"
echo "================================"
echo ""
echo "Next Steps:"
echo "1. Commit changes: git add . && git commit -m 'Fix: emergentintegrations deployment'"
echo "2. Push to GitHub: git push origin main"
echo "3. Deploy on Render.com"
echo "4. Monitor build logs for successful package installation"
echo ""
echo "Expected in Render logs:"
echo "  ✓ Successfully installed emergentintegrations-0.1.0"
echo "  ✓ Backend server starting on port 8001"
echo ""
