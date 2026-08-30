#!/usr/bin/env python3
"""
MyAnimeList OAuth2 PKCE Token Generator for ani-sync
Generates access_token and refresh_token easily from the terminal.
"""

import os
import sys
import secrets
import webbrowser
import urllib.parse
import requests

TOKEN_URL = "https://myanimelist.net/v1/oauth2/token"
AUTH_URL = "https://myanimelist.net/v1/oauth2/authorize"

def generate_code_verifier(length=128):
    """Generate a high-entropy cryptographic random string."""
    return secrets.token_urlsafe(length)[:128]

def main():
    print("=" * 55)
    print("      MyAnimeList OAuth2 Setup for ani-sync      ")
    print("=" * 55)
    print("\n1. Go to: https://myanimelist.net/apiconfig")
    print("2. Create a new Client / Application with:")
    print("   - App Type: other")
    print("   - Redirect URL: http://localhost")
    print("=" * 55)
    
    client_id = input("\nEnter your MAL Client ID: ").strip()
    if not client_id:
        sys.exit("Error: Client ID is required.")
        
    client_secret = input("Enter your MAL Client Secret (press Enter if none): ").strip()
    
    code_verifier = generate_code_verifier()
    
    params = {
        "response_type": "code",
        "client_id": client_id,
        "code_challenge": code_verifier,
        "code_challenge_method": "plain",
    }
    
    auth_link = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    
    print("\n" + "-" * 55)
    print("Open the following link in your browser to authorize:")
    print("-" * 55)
    print(auth_link)
    print("-" * 55)
    
    try:
        webbrowser.open(auth_link)
    except Exception:
        pass
        
    print("\nAfter clicking 'Allow', you will be redirected to an address like:")
    print("  http://localhost/?code=AUTHORIZATION_CODE")
    
    auth_code_input = input("\nEnter the 'code' parameter from the redirected URL: ").strip()
    
    # If the user pasted the entire URL by accident, parse the code out
    if "code=" in auth_code_input:
        parsed = urllib.parse.urlparse(auth_code_input)
        query_params = urllib.parse.parse_qs(parsed.query)
        if "code" in query_params:
            auth_code = query_params["code"][0]
        else:
            auth_code = auth_code_input.split("code=")[1].split("&")[0]
    else:
        auth_code = auth_code_input

    if not auth_code:
        sys.exit("Error: Authorization code cannot be empty.")
        
    print("\nExchanging authorization code for tokens...")
    data = {
        "client_id": client_id,
        "grant_type": "authorization_code",
        "code": auth_code,
        "code_verifier": code_verifier,
    }
    if client_secret:
        data["client_secret"] = client_secret
        
    res = requests.post(TOKEN_URL, data=data)
    
    if res.status_code != 200:
        print(f"\n❌ Error ({res.status_code}): {res.text}")
        sys.exit(1)
        
    tokens = res.json()
    refresh_token = tokens.get("refresh_token")
    access_token = tokens.get("access_token")
    
    print("\n" + "=" * 55)
    print("✅ Authorization Successful!")
    print("=" * 55)
    print("\nAdd the following lines to your ~/.bashrc or ~/.zshrc:\n")
    print(f'export MAL_CLIENT_ID="{client_id}"')
    if client_secret:
        print(f'export MAL_CLIENT_SECRET="{client_secret}"')
    else:
        print('export MAL_CLIENT_SECRET=""')
    print(f'export MAL_REFRESH_TOKEN="{refresh_token}"')
    print("\n" + "=" * 55)
    print("Then reload your shell:")
    print("  source ~/.bashrc   # or source ~/.zshrc")
    print("=" * 55)

if __name__ == "__main__":
    main()
