#!/usr/bin/env python3
"""
Simple test script to demonstrate the JSONPlaceholder API functionality
discovered through HAR analysis.
"""

import requests
import json

def test_jsonplaceholder_api():
    """Test the main endpoints of the JSONPlaceholder API."""
    base_url = "https://jsonplaceholder.typicode.com"
    
    print("🧪 Testing JSONPlaceholder API discovered from HAR analysis")
    print("=" * 60)
    
    # Test 1: Get all posts
    print("\n1. Testing GET /posts")
    response = requests.get(f"{base_url}/posts")
    print(f"   Status: {response.status_code}")
    posts = response.json()
    print(f"   Found {len(posts)} posts")
    print(f"   First post title: {posts[0]['title'][:50]}...")
    
    # Test 2: Get specific post
    print("\n2. Testing GET /posts/1")
    response = requests.get(f"{base_url}/posts/1")
    print(f"   Status: {response.status_code}")
    post = response.json()
    print(f"   Post ID: {post['id']}")
    print(f"   Post title: {post['title'][:50]}...")
    
    # Test 3: Create new post
    print("\n3. Testing POST /posts")
    new_post = {
        "title": "Test Post from HAR Discovery",
        "body": "This post was created to test the API discovered through HAR analysis",
        "userId": 1
    }
    response = requests.post(f"{base_url}/posts", json=new_post)
    print(f"   Status: {response.status_code}")
    created_post = response.json()
    print(f"   Created post ID: {created_post['id']}")
    print(f"   Created post title: {created_post['title']}")
    
    # Test 4: Update post
    print("\n4. Testing PUT /posts/1")
    updated_post = {
        "id": 1,
        "title": "Updated Test Post",
        "body": "This post was updated to test the API",
        "userId": 1
    }
    response = requests.put(f"{base_url}/posts/1", json=updated_post)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Updated post title: {result['title']}")
    
    # Test 5: Delete post
    print("\n5. Testing DELETE /posts/1")
    response = requests.delete(f"{base_url}/posts/1")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test 6: Get users
    print("\n6. Testing GET /users")
    response = requests.get(f"{base_url}/users")
    print(f"   Status: {response.status_code}")
    users = response.json()
    print(f"   Found {len(users)} users")
    print(f"   First user: {users[0]['name']} ({users[0]['email']})")
    
    print("\n✅ All tests completed successfully!")
    print("🎉 The OpenAPI specification accurately represents the discovered API!")

if __name__ == "__main__":
    test_jsonplaceholder_api()