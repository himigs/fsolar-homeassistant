"""Config flow for FSolar integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import FSolarAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
        vol.Optional("password_encrypted", default=True): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    
    # Criar API com os parâmetros corretos
    api = FSolarAPI(
        username=data["username"],
        password=data["password"],
        session=session,
        password_encrypted=data.get("password_encrypted", False)
    )

    # Tentar autenticar
    if not await api.login():
        raise InvalidAuth

    # Buscar informações básicas para validar a conexão
    try:
        devices = await api.get_devices()
        if not devices:
            _LOGGER.warning("No devices found in FSolar account")
    except Exception as err:
        _LOGGER.error("Failed to fetch devices: %s", err)
        raise CannotConnect from err

    # Retornar info que será armazenada no config entry
    return {"title": f"FSolar ({data['username']})"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FSolar."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            # Verificar se já existe uma entrada com este username
            await self.async_set_unique_id(user_input["username"])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for FSolar."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Obter valor atual ou usar padrão
        current_voltage = self.config_entry.options.get("nominal_voltage", "25.6")

        options_schema = vol.Schema(
            {
                vol.Required(
                    "nominal_voltage",
                    default=current_voltage,
                ): vol.In({
                    "12.8": "12V LiFePO₄ (12.8V)",
                    "25.6": "24V LiFePO₄ (25.6V)",
                    "51.2": "48V LiFePO₄ (51.2V)",
                }),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            description_placeholders={
                "info": "Selecione a tensão nominal da sua bateria. Isso será usado para calcular a capacidade em kWh."
            },
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""