from app.repositories.user_repo import UserRepository
from app.models.user import User
from app.auth.jwt import create_access_token, create_refresh_token
from app.auth.auth import hash_password

import secrets


class GoogleService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def login_or_register(self, user_info: dict):
        # Google OIDC standard claims 'sub' as the subject identifier (Google ID).
        # We also check 'id' just in case of non-standard responses.
        google_id = user_info.get("sub") or user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name") or (email.split("@")[0] if email else "User")
        avatar = user_info.get("picture")

        print(f"[DEBUG] Google Auth attempt for email: {email}, google_id: {google_id}")

        if not google_id:
            print("[ERROR] Google Auth failed: No 'sub' or 'id' in user_info")
            raise Exception("No google_id found in Google response")

        user = await self.repo.get_by_google_id(google_id)

        if not user:
            # Fallback to email to link existing accounts
            user = await self.repo.get_by_email(email)
            if user:
                 print(f"[DEBUG] Found existing user by email: {email}. Linking Google ID.")

        if user:
            updated = False

            # Security check: if user ALREADY has a different google_id
            if user.google_id and user.google_id != google_id:
                print(f"[ERROR] Google ID mismatch for {email}. Existing: {user.google_id}, New: {google_id}")
                raise Exception("This email is already linked to a different Google account.")
            
            # Link Google ID if missing
            if not user.google_id:
                user.google_id = google_id
                updated = True
                print(f"[DEBUG] Updated google_id for user: {email}")
            
            # Automatically verify user if they log in via Google
            if not user.is_verified:
                user.is_verified = True
                updated = True
                print(f"[DEBUG] Marked user verified via Google: {email}")

            # Update profile info if changed
            if avatar and user.avatar != avatar:
                user.avatar = avatar
                updated = True
            if name and user.name != name:
                user.name = name
                updated = True
            
            if updated:
                user = await self.repo.update(user)
                print(f"[DEBUG] User {email} updated successfully in DB.")
            else:
                print(f"[DEBUG] User {email} login successful, no updates needed.")

        else:
            # Create new user
            print(f"[DEBUG] Creating new user via Google: {email}")
            random_password = secrets.token_urlsafe(24)

            user = User(
                name=name,
                email=email,
                password=hash_password(random_password),
                avatar=avatar,
                google_id=google_id,
                is_verified=True
            )

            user = await self.repo.create(user)
            print(f"[DEBUG] New user {email} created successfully with ID {user.id}")

        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user,
        }
    
    async def link_google(self, user, google_id:str):
        existing = await self.repo.get_by_google_id(google_id)

        if existing:
            raise Exception("Google already used")
        
        if user.google_id:
            raise Exception("Already linked")
        
        user.google_id = google_id
        user = await self.repo.update(user)

        return user
