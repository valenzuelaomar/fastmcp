"""Tests for Google OAuth provider."""

import os
from unittest.mock import patch

import pytest

from fastmcp.server.auth.providers.google import GoogleProvider


class TestGoogleProvider:
    """Test Google OAuth provider functionality."""

    def test_init_with_explicit_params(self):
        """Test GoogleProvider initialization with explicit parameters."""
        provider = GoogleProvider(
            client_id="123456789.apps.googleusercontent.com",
            client_secret="GOCSPX-test123",
            base_url="https://myserver.com",
            required_scopes=["openid", "email", "profile"],
        )

        assert provider._upstream_client_id == "123456789.apps.googleusercontent.com"
        assert provider._upstream_client_secret.get_secret_value() == "GOCSPX-test123"
        assert str(provider.base_url) == "https://myserver.com/"

    @pytest.mark.parametrize(
        "scopes_env",
        [
            "openid,https://www.googleapis.com/auth/userinfo.email",
            '["openid", "https://www.googleapis.com/auth/userinfo.email"]',
        ],
    )
    def test_init_with_env_vars(self, scopes_env):
        """Test GoogleProvider initialization from environment variables."""
        with patch.dict(
            os.environ,
            {
                "FASTMCP_SERVER_AUTH_GOOGLE_CLIENT_ID": "env123.apps.googleusercontent.com",
                "FASTMCP_SERVER_AUTH_GOOGLE_CLIENT_SECRET": "GOCSPX-env456",
                "FASTMCP_SERVER_AUTH_GOOGLE_BASE_URL": "https://envserver.com",
                "FASTMCP_SERVER_AUTH_GOOGLE_REQUIRED_SCOPES": scopes_env,
            },
        ):
            provider = GoogleProvider()

            assert provider._upstream_client_id == "env123.apps.googleusercontent.com"
            assert (
                provider._upstream_client_secret.get_secret_value() == "GOCSPX-env456"
            )
            assert str(provider.base_url) == "https://envserver.com/"
            assert provider._token_validator.required_scopes == [
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
            ]

    def test_init_missing_client_id_raises_error(self):
        """Test that missing client_id raises ValueError."""
        # Clear environment variables to test proper error handling
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="client_id is required"):
                GoogleProvider(client_secret="GOCSPX-test123")

    def test_init_missing_client_secret_raises_error(self):
        """Test that missing client_secret raises ValueError."""
        # Clear environment variables to test proper error handling
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="client_secret is required"):
                GoogleProvider(client_id="123456789.apps.googleusercontent.com")

    def test_init_defaults(self):
        """Test that default values are applied correctly."""
        provider = GoogleProvider(
            client_id="123456789.apps.googleusercontent.com",
            client_secret="GOCSPX-test123",
        )

        # Check defaults
        assert str(provider.base_url) == "http://localhost:8000/"
        assert provider._redirect_path == "/auth/callback"
        # Google provider has ["openid"] as default but we can't easily verify without accessing internals

    def test_oauth_endpoints_configured_correctly(self):
        """Test that OAuth endpoints are configured correctly."""
        provider = GoogleProvider(
            client_id="123456789.apps.googleusercontent.com",
            client_secret="GOCSPX-test123",
            base_url="https://myserver.com",
        )

        # Check that endpoints use Google's OAuth2 endpoints
        assert (
            provider._upstream_authorization_endpoint
            == "https://accounts.google.com/o/oauth2/v2/auth"
        )
        assert (
            provider._upstream_token_endpoint == "https://oauth2.googleapis.com/token"
        )
        # Google provider doesn't currently set a revocation endpoint
        assert provider._upstream_revocation_endpoint is None

    def test_google_specific_scopes(self):
        """Test handling of Google-specific scope formats."""
        # Just test that the provider accepts Google-specific scopes without error
        provider = GoogleProvider(
            client_id="123456789.apps.googleusercontent.com",
            client_secret="GOCSPX-test123",
            required_scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
        )

        # Provider should initialize successfully with these scopes
        assert provider is not None
