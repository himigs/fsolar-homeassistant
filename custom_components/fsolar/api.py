"""FSolar API Client - Hybrid Mode."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class FSolarAPI:
    """FSolar API Client with support for pre-encrypted passwords."""

    def __init__(
        self, 
        username: str, 
        password: str, 
        session: aiohttp.ClientSession,
        password_encrypted: bool = False
    ) -> None:
        """Initialize the API client.
        
        Args:
            username: FSolar username (email)
            password: Password (plain or encrypted)
            session: aiohttp client session
            password_encrypted: If True, password is already RSA encrypted
        """
        self.username = username
        self.password = password
        self.session = session
        self.password_encrypted = password_encrypted
        self.base_url = "https://shine-api.felicitysolar.com"
        self.token: str | None = None
        self.is_authenticated = False

    async def login(self) -> bool:
        """Authenticate with FSolar API and get access token."""
        try:
            url = f"{self.base_url}/userlogin"
            
            # If the password is already encrypted, use it directly
            if self.password_encrypted:
                encrypted_password = self.password
                _LOGGER.debug("Using pre-encrypted password")
            else:
                _LOGGER.debug("Auto-encrypting plain password with RSA")
                try:
                    from cryptography.hazmat.primitives import serialization
                    from cryptography.hazmat.primitives.asymmetric import padding
                    from cryptography.hazmat.backends import default_backend
                    import base64
                    
                    # Static RSA public key from the FelicitySolar portal
                    PUB_KEY_STR = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnAJE68pjWZmtSg6ZJs9FZugJXC6bBSluTW6mJttOLOaljrdErVnM5DNN+YFzpB9pAysTErjY1bnSVuEwQSwptnqUji7Ch2qMj2n+0eCp8p6vtSh7/tFr2ul8nDRtkoswLANAIwtUk/G85ipMpmY1W642LImnEJmGkkddlbjbjxJTZWR5hc/d9cPWb+AR77LxFFrMik3c+44v1kQlIPFP6EjIbOvt/Lv7fHWD9JI/YzN4y1gK7C/VQdNGuikQyNg+5W3rg9ecYf9I5uLAQwY/hxeI3lbNsErebqKe2EbJ8AwcNIC0lDBz53Sq0ML89QapEuy3fB+upuctxLULVDCbNwIDAQAB"
                    
                    public_key_bytes = base64.b64decode(PUB_KEY_STR)
                    public_key = serialization.load_der_public_key(public_key_bytes, backend=default_backend())
                    
                    encrypted = public_key.encrypt(
                        self.password.encode('utf-8'),
                        padding.PKCS1v15()
                    )
                    encrypted_password = base64.b64encode(encrypted).decode('utf-8')
                except ImportError:
                    _LOGGER.error("Cryptography library is missing. Cannot encrypt password natively.")
                    encrypted_password = self.password
                except Exception as e:
                    _LOGGER.error("Error encrypting password: %s", e)
                    encrypted_password = self.password
            
            payload = {
                "userName": self.username.strip(),
                "password": encrypted_password.strip(),
                "version": "1.0"
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "lang": "pt_BR",
            }
            
            _LOGGER.debug("Attempting login to FSolar API with payload: %s", payload)
            
            async with self.session.post(url, json=payload, headers=headers, ssl=False) as response:
                response.raise_for_status()
                data = await response.json()
                
                _LOGGER.debug("Login response status: %s, data: %s", response.status, data)
                
                # The response includes the token in data.token
                if isinstance(data, dict):
                    if data.get("code") == 200 and "data" in data:
                        token = data["data"].get("token")
                        if token:
                            # Strip "Bearer_" prefix if present
                            self.token = token.replace("Bearer_", "")
                            self.is_authenticated = True
                            _LOGGER.info("Successfully authenticated with FSolar API")
                            return True
                    elif "token" in data:
                        self.token = data["token"].replace("Bearer_", "")
                        self.is_authenticated = True
                        _LOGGER.info("Successfully authenticated with FSolar API")
                        return True
                
                # Sometimes the token is returned directly as a string
                elif isinstance(data, str):
                    self.token = data.replace("Bearer_", "")
                    self.is_authenticated = True
                    _LOGGER.info("Successfully authenticated with FSolar API")
                    return True
                
                _LOGGER.warning("No token received from FSolar API: %s", data)
                return False
                    
        except aiohttp.ClientError as err:
            _LOGGER.warning("Failed to authenticate with FSolar API (ClientError): %s", err)
            self.is_authenticated = False
            return False
        except Exception as err:
            _LOGGER.warning("Unexpected error during authentication: %s", err)
            self.is_authenticated = False
            return False

    async def _make_request(
        self, endpoint: str, payload: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Make an authenticated request to the FSolar API."""
        if not self.is_authenticated:
            await self.login()

        url = f"{self.base_url}/{endpoint}"
        headers = {}

        # Add authentication token to request headers
        if self.token:
            # The token may include a "Bearer_" prefix or be sent as-is
            if self.token.startswith("Bearer_"):
                headers["Authorization"] = self.token
            else:
                headers["Authorization"] = f"Bearer_{self.token}"
        
        try:
            async with self.session.post(
                url, json=payload or {}, headers=headers, ssl=False
            ) as response:
                # Re-authenticate if token has expired
                if response.status == 401 or response.status == 403:
                    _LOGGER.warning("Token expired, attempting to re-authenticate")
                    await self.login()
                    if self.token:
                        if self.token.startswith("Bearer_"):
                            headers["Authorization"] = self.token
                        else:
                            headers["Authorization"] = f"Bearer_{self.token}"
                    
                    async with self.session.post(
                        url, json=payload or {}, headers=headers, ssl=False
                    ) as retry_response:
                        retry_response.raise_for_status()
                        return await retry_response.json()
                
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as err:
            _LOGGER.warning("API request failed (network error): %s", err)
            raise

    async def get_devices(self) -> list[dict[str, Any]]:
        """Get list of all devices."""
        try:
            # Endpoint correto e payload de paginação
            payload = {
                "pageNum": 1,
                "pageSize": 100,  # Fetch up to 100 devices
                "deviceSn": "",
                "status": "",
                "sampleFlag": "",
                "oscFlag": ""
            }
            
            data = await self._make_request("device/list_device_all_type", payload)
            
            _LOGGER.debug("Get devices response: %s", data)
            
            # Extract device list from response
            if isinstance(data, dict):
                if data.get("code") == 200 and "data" in data:
                    device_data = data["data"]
                    # Device list is nested under data.dataList
                    if isinstance(device_data, dict) and "dataList" in device_data:
                        devices = device_data["dataList"]
                        _LOGGER.info("Found %d devices", len(devices))
                        return devices
                    elif isinstance(device_data, list):
                        return device_data
            elif isinstance(data, list):
                return data
            
            _LOGGER.warning("Unexpected device list format: %s", data)
            return []
            
        except Exception as err:
            _LOGGER.warning("Failed to get devices (network error): %s", err)
            return []

    async def get_battery_data(self, device_sn: str, device_type: str = "OC") -> dict[str, Any]:
        """Get battery data for a specific device."""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            payload = {
                "deviceSn": device_sn,
                "deviceType": device_type,
                "dateStr": current_time
            }
            
            data = await self._make_request("device/get_device_snapshot", payload)
            
            _LOGGER.debug("Battery data for %s: %s", device_sn, data)
            
            # Extract data from response
            if isinstance(data, dict):
                if data.get("code") == 200 and "data" in data:
                    return data["data"]
                return data
            
            return data
            
        except Exception as err:
            _LOGGER.error("Failed to get battery data for device %s: %s", device_sn, err)
            return {}

    async def get_device_realtime(self, device_sn: str) -> dict[str, Any]:
        """Get real-time device data."""
        try:
            payload = {"deviceSn": device_sn}
            data = await self._make_request("device/get_device_realtime", payload)
            
            if isinstance(data, dict) and data.get("code") == 200:
                return data.get("data", {})
            return data
            
        except Exception as err:
            _LOGGER.error("Failed to get realtime data for device %s: %s", device_sn, err)
            return {}

    async def get_battery_history(
        self, device_sn: str, start_date: str, end_date: str, device_type: str = "OC"
    ) -> dict[str, Any]:
        """Get historical battery data."""
        try:
            payload = {
                "deviceSn": device_sn,
                "deviceType": device_type,
                "startDate": start_date,
                "endDate": end_date
            }
            
            data = await self._make_request("device/get_device_history", payload)
            
            if isinstance(data, dict) and data.get("code") == 200:
                return data.get("data", {})
            return data
            
        except Exception as err:
            _LOGGER.error("Failed to get battery history: %s", err)
            return {}