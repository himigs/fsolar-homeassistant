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
            
            # Se a senha já está encriptada, usar diretamente
            # Senão, avisar que precisa ser encriptada manualmente
            if self.password_encrypted:
                encrypted_password = self.password
                _LOGGER.debug("Using pre-encrypted password")
            else:
                _LOGGER.warning(
                    "Password is not encrypted. For security, please provide "
                    "an encrypted password using the FSolar web interface. "
                    "See documentation for details."
                )
                # Por enquanto, vamos tentar enviar a senha como está
                # (isso provavelmente vai falhar)
                encrypted_password = self.password
            
            payload = {
                "userName": self.username,
                "password": encrypted_password,
                "version": "1.0"
            }
            
            _LOGGER.debug("Attempting login to FSolar API for user: %s", self.username)
            
            async with self.session.post(url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                
                _LOGGER.debug("Login response status: %s", response.status)
                
                # A resposta inclui o token no campo "data.token"
                if isinstance(data, dict):
                    if data.get("code") == 200 and "data" in data:
                        token = data["data"].get("token")
                        if token:
                            # Remover prefixo "Bearer_" se existir
                            self.token = token.replace("Bearer_", "")
                            self.is_authenticated = True
                            _LOGGER.info("Successfully authenticated with FSolar API")
                            return True
                    elif "token" in data:
                        self.token = data["token"].replace("Bearer_", "")
                        self.is_authenticated = True
                        _LOGGER.info("Successfully authenticated with FSolar API")
                        return True
                
                # Às vezes retorna o token diretamente como string
                elif isinstance(data, str):
                    self.token = data.replace("Bearer_", "")
                    self.is_authenticated = True
                    _LOGGER.info("Successfully authenticated with FSolar API")
                    return True
                
                _LOGGER.error("No token received from FSolar API: %s", data)
                return False
                    
        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to authenticate with FSolar API: %s", err)
            self.is_authenticated = False
            return False
        except Exception as err:
            _LOGGER.error("Unexpected error during authentication: %s", err)
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
        
        # Adicionar token de autenticação no header
        if self.token:
            # O token pode ter o prefixo "Bearer_" ou ser enviado diretamente
            if self.token.startswith("Bearer_"):
                headers["Authorization"] = self.token
            else:
                headers["Authorization"] = f"Bearer_{self.token}"
        
        try:
            async with self.session.post(
                url, json=payload or {}, headers=headers
            ) as response:
                # Se token expirado, tentar re-autenticar
                if response.status == 401 or response.status == 403:
                    _LOGGER.warning("Token expired, attempting to re-authenticate")
                    await self.login()
                    if self.token:
                        if self.token.startswith("Bearer_"):
                            headers["Authorization"] = self.token
                        else:
                            headers["Authorization"] = f"Bearer_{self.token}"
                    
                    async with self.session.post(
                        url, json=payload or {}, headers=headers
                    ) as retry_response:
                        retry_response.raise_for_status()
                        return await retry_response.json()
                
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as err:
            _LOGGER.error("API request failed: %s", err)
            raise

    async def get_devices(self) -> list[dict[str, Any]]:
        """Get list of all devices."""
        try:
            # Endpoint correto e payload de paginação
            payload = {
                "pageNum": 1,
                "pageSize": 100,  # Buscar até 100 dispositivos
                "deviceSn": "",
                "status": "",
                "sampleFlag": "",
                "oscFlag": ""
            }
            
            data = await self._make_request("device/list_device_all_type", payload)
            
            _LOGGER.debug("Get devices response: %s", data)
            
            # Extrair lista de dispositivos da resposta
            if isinstance(data, dict):
                if data.get("code") == 200 and "data" in data:
                    device_data = data["data"]
                    # A lista está em data.dataList
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
            _LOGGER.error("Failed to get devices: %s", err)
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
            
            # Extrair dados da resposta
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