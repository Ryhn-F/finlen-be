import json
import logging
import os
from pathlib import Path
from typing import Any
import firebase_admin
from firebase_admin import credentials, firestore

from finlen_be.core.config import settings

logger = logging.getLogger(__name__)

_firebase_app: firebase_admin.App | None = None
_firestore_client: Any | None = None


def initialize_firebase() -> firebase_admin.App | None:
    """Initialize Firebase Admin SDK centrally (idempotent)."""
    global _firebase_app, _firestore_client
    
    if _firebase_app is not None:
        return _firebase_app

    # Check if already initialized by another module
    try:
        _firebase_app = firebase_admin.get_app()
        _firestore_client = firestore.client(app=_firebase_app)
        return _firebase_app
    except ValueError:
        pass

    # 1. Try file path (check candidate locations)
    candidate_paths = []
    if settings.FIREBASE_CREDENTIALS_PATH:
        candidate_paths.append(Path(settings.FIREBASE_CREDENTIALS_PATH))
    # Workspace root resolution (finlen-be/src/serviceAccountKey.json)
    package_dir = Path(__file__).resolve().parent
    candidate_paths.append(package_dir.parents[1] / "src" / "serviceAccountKey.json")
    candidate_paths.append(package_dir.parent / "serviceAccountKey.json")
    candidate_paths.append(Path("src/serviceAccountKey.json").resolve())
    candidate_paths.append(Path("../serviceAccountKey.json").resolve())

    resolved_path: Path | None = None
    for cp in candidate_paths:
        if cp.is_file():
            resolved_path = cp
            break

    if resolved_path:
        try:
            cred = credentials.Certificate(str(resolved_path))
            _firebase_app = firebase_admin.initialize_app(cred)
            _firestore_client = firestore.client(app=_firebase_app)
            logger.info("Firebase initialized using service account file at %s", resolved_path)
            return _firebase_app
        except Exception as e:
            logger.error("Failed to initialize Firebase from file %s: %s", resolved_path, e)

    # 2. Try environment variables
    if settings.FIREBASE_PROJECT_ID and settings.FIREBASE_PRIVATE_KEY and settings.FIREBASE_CLIENT_EMAIL:
        try:
            cert_dict = {
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID or "",
                "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "client_id": settings.FIREBASE_CLIENT_ID or "",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            cred = credentials.Certificate(cert_dict)
            _firebase_app = firebase_admin.initialize_app(cred)
            _firestore_client = firestore.client(app=_firebase_app)
            logger.info("Firebase initialized using environment variable credentials.")
            return _firebase_app
        except Exception as e:
            logger.error("Failed to initialize Firebase from environment variables: %s", e)

    logger.warning(
        "Firebase credentials not found or could not be loaded. Firestore features will be mock/disabled."
    )
    return None


def get_firestore_client() -> Any:
    """Get the Firestore client singleton."""
    global _firestore_client
    if _firestore_client is None:
        initialize_firebase()
    return _firestore_client
