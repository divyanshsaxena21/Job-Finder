#!/usr/bin/env python3
"""Comprehensive API testing with authentication"""
import requests
import json
import sys
from datetime import datetime

print("=" * 70)
print("COMPREHENSIVE JOB FINDER API TESTING")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

base_url = "http://localhost:8000"
tests_passed = 0
tests_failed = 0
auth_token = None

# Step 1: Health Check
print("\n[1/6] Testing Health Endpoint")
try:
    r = requests.get(f"{base_url}/health", timeout=5)
    if r.status_code == 200:
        print(f"  ✓ Status: {r.status_code}")
        print(f"  ✓ Response: {r.json()}")
        tests_passed += 1
    else:
        print(f"  ✗ Status: {r.status_code}")
        tests_failed += 1
except Exception as e:
    print(f"  ✗ Error: {e}")
    tests_failed += 1

# Step 2: Register Test User
print("\n[2/6] Registering Test User")
try:
    r = requests.post(f"{base_url}/auth/register", 
                     json={
                         'name': f'Test User {datetime.now().timestamp()}',
                         'email': f'test{datetime.now().timestamp()}@test.com',
                         'password': 'Test123!@#'
                     }, 
                     timeout=5)
    if r.status_code == 200:
        response = r.json()
        auth_token = response['access_token']
        print(f"  ✓ Status: {r.status_code}")
        print(f"  ✓ Token received: {auth_token[:50]}...")
        print(f"  ✓ User ID: {response['user']['_id']}")
        tests_passed += 1
    else:
        print(f"  ✗ Status: {r.status_code}")
        print(f"  ✗ Response: {r.text[:100]}")
        tests_failed += 1
except Exception as e:
    print(f"  ✗ Error: {e}")
    tests_failed += 1

# Setup headers with auth token
headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}

# Step 3: Get Jobs
print("\n[3/6] Testing Get Jobs Endpoint")
try:
    r = requests.get(f"{base_url}/jobs", 
                    headers=headers,
                    timeout=10, 
                    params={'skip': 0, 'limit': 5})
    if r.status_code == 200:
        jobs = r.json()
        print(f"  ✓ Status: {r.status_code}")
        print(f"  ✓ Jobs returned: {len(jobs)}")
        if jobs:
            job = jobs[0]
            print(f"  ✓ Sample job:")
            print(f"    - Title: {job.get('title', 'N/A')}")
            print(f"    - Company: {job.get('company', 'N/A')}")
            print(f"    - Source: {job.get('source', 'N/A')}")
        tests_passed += 1
    else:
        print(f"  ✗ Status: {r.status_code}")
        print(f"  ✗ Response: {r.text[:100]}")
        tests_failed += 1
except Exception as e:
    print(f"  ✗ Error: {e}")
    tests_failed += 1

# Step 4: Get Applications
print("\n[4/6] Testing Get Applications Endpoint")
try:
    r = requests.get(f"{base_url}/applications", 
                    headers=headers,
                    timeout=10)
    if r.status_code == 200:
        apps = r.json()
        print(f"  ✓ Status: {r.status_code}")
        print(f"  ✓ Applications count: {len(apps)}")
        tests_passed += 1
    else:
        print(f"  ✗ Status: {r.status_code}")
        print(f"  ✗ Response: {r.text[:100]}")
        tests_failed += 1
except Exception as e:
    print(f"  ✗ Error: {e}")
    tests_failed += 1

# Step 5: Get User Preferences
print("\n[5/6] Testing User Preferences Endpoint")
try:
    r = requests.get(f"{base_url}/preferences", 
                    headers=headers,
                    timeout=10)
    if r.status_code == 200:
        prefs = r.json()
        print(f"  ✓ Status: {r.status_code}")
        print(f"  ✓ Preferences retrieved")
        print(f"  ✓ Job titles: {len(prefs.get('job_titles', []))} configured")
        tests_passed += 1
    else:
        print(f"  ✗ Status: {r.status_code}")
        print(f"  ✗ Response: {r.text[:100]}")
        tests_failed += 1
except Exception as e:
    print(f"  ✗ Error: {e}")
    tests_failed += 1

# Step 6: Get Auto-Apply Stats
print("\n[6/6] Testing Auto-Apply Stats Endpoint")
try:
    r = requests.get(f"{base_url}/auto-apply/stats", 
                    headers=headers,
                    timeout=10)
    if r.status_code == 200:
        stats = r.json()
        print(f"  ✓ Status: {r.status_code}")
        print(f"  ✓ Auto-Apply Stats:")
        print(f"    - Total applications: {stats.get('total_applications', 0)}")
        print(f"    - Success rate: {stats.get('success_rate', 0):.1f}%")
        print(f"    - Last run: {stats.get('last_run', 'Never')}")
        tests_passed += 1
    else:
        print(f"  ✗ Status: {r.status_code}")
        print(f"  ✗ Response: {r.text[:100]}")
        tests_failed += 1
except Exception as e:
    print(f"  ✗ Error: {e}")
    tests_failed += 1

# Summary
print("\n" + "=" * 70)
print(f"TEST SUMMARY: {tests_passed} PASSED ✓ | {tests_failed} FAILED ✗")
if tests_failed == 0:
    print("🎉 ALL TESTS PASSED - BACKEND FULLY OPERATIONAL")
else:
    print(f"⚠️  {tests_failed} test(s) failed - Please review errors above")
print("=" * 70)

sys.exit(0 if tests_failed == 0 else 1)
