#!/usr/bin/env python3
"""Quick endpoint testing script"""
import requests
import json
import sys

print("=" * 70)
print("TESTING JOB FINDER API ENDPOINTS")
print("=" * 70)

base_url = "http://localhost:8000"
tests_passed = 0
tests_failed = 0

# Test 1: Health
print("\n[1/4] Testing Health Endpoint")
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

# Test 2: Get Jobs
print("\n[2/4] Testing Get Jobs Endpoint")
try:
    r = requests.get(f"{base_url}/jobs", timeout=10, params={'skip': 0, 'limit': 5})
    if r.status_code == 200:
        jobs = r.json()
        print(f"  ✓ Status: {r.status_code}")
        print(f"  ✓ Jobs returned: {len(jobs)}")
        if jobs:
            print(f"  ✓ Sample job: {jobs[0].get('title', 'N/A')} at {jobs[0].get('company', 'N/A')}")
        tests_passed += 1
    else:
        print(f"  ✗ Status: {r.status_code}")
        tests_failed += 1
except Exception as e:
    print(f"  ✗ Error: {e}")
    tests_failed += 1

# Test 3: Get Applications
print("\n[3/4] Testing Get Applications Endpoint")
try:
    r = requests.get(f"{base_url}/applications", timeout=10)
    if r.status_code == 200:
        apps = r.json()
        print(f"  ✓ Status: {r.status_code}")
        print(f"  ✓ Applications count: {len(apps)}")
        tests_passed += 1
    else:
        print(f"  ✗ Status: {r.status_code}")
        tests_failed += 1
except Exception as e:
    print(f"  ✗ Error: {e}")
    tests_failed += 1

# Test 4: Auto-Apply Stats
print("\n[4/4] Testing Auto-Apply Stats Endpoint")
try:
    r = requests.get(f"{base_url}/auto-apply/stats", timeout=10)
    if r.status_code == 200:
        stats = r.json()
        print(f"  ✓ Status: {r.status_code}")
        print(f"  ✓ Stats: {json.dumps(stats, indent=4)}")
        tests_passed += 1
    else:
        print(f"  ✗ Status: {r.status_code}")
        tests_failed += 1
except Exception as e:
    print(f"  ✗ Error: {e}")
    tests_failed += 1

# Summary
print("\n" + "=" * 70)
print(f"TEST SUMMARY: {tests_passed} PASSED ✓ | {tests_failed} FAILED ✗")
print("=" * 70)

sys.exit(0 if tests_failed == 0 else 1)
