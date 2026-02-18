import logging
import types
from typing import Any

from elasticsearch7 import Elasticsearch as Es7, helpers as helper_es7
from elasticsearch8 import Elasticsearch as Es8, helpers as helper_es8
from requests import get as requests_get
from requests.auth import HTTPBasicAuth
from typica.connection import ESConnectionMeta

from src.configs import project_meta

LOGGER = logging.getLogger(project_meta.name)


class ESConnector:
    _meta: ESConnectionMeta
    _client: Es7 | Es8
    _helpers: types.ModuleType

    @property
    def endpoint_uri(self):
        return f"http://{self._meta.host}:{self._meta.port}"

    def __init__(self, meta: ESConnectionMeta):
        self._meta = meta

    def __enter__(self) -> "ESConnector":
        self.connect()
        return self

    def _build_client_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        if self._meta.cloud_id:
            kwargs["cloud_id"] = self._meta.cloud_id
        else:
            kwargs["hosts"] = self.endpoint_uri

        if self._meta.api_key:
            kwargs["api_key"] = self._meta.api_key
        elif self._meta.username:
            kwargs["basic_auth"] = (self._meta.username, self._meta.password)

        if self._meta.verify_ssl:
            kwargs["ca_certs"] = self._meta.ca_file
            kwargs["client_cert"] = self._meta.client_cert
            kwargs["client_key"] = self._meta.client_key

        return kwargs

    def get_version(self) -> str | None:
        """Fetch the Elasticsearch server version."""
        try:
            auth = None
            if self._meta.username and self._meta.password:
                auth = HTTPBasicAuth(self._meta.username, self._meta.password)

            response = requests_get(self.endpoint_uri, auth=auth, timeout=10)
            response.raise_for_status()
            json_response = response.json()

            return json_response.get("version", {}).get("number")
        except Exception as e:
            LOGGER.error("Failed to fetch Elasticsearch version.")
            raise e

    def connect(self) -> None:
        if hasattr(self, "_client") and self._client:
            return self._client
        try:
            kwargs = self._build_client_kwargs()
            version = self.get_version()
            if version and version.startswith("8"):
                self._client = Es8(**kwargs)
                self._helpers = helper_es8
            else:
                self._client = Es7(**kwargs)
                self._helpers = helper_es7

            LOGGER.info("Elasticsearch client initialized")
        except Exception as e:
            LOGGER.exception("Failed to create Elasticsearch client")
            raise e

        return self._client

    def _is_unhealthy(self, force: bool = True) -> bool:
        """Check Elasticsearch health status."""
        try:
            auth = None
            if self._meta.username and self._meta.password:
                auth = HTTPBasicAuth(self._meta.username, self._meta.password)

            response = requests_get(
                f"{self.endpoint_uri}/_cluster/health",
                auth=auth,
                timeout=10,
            )
            response.raise_for_status()
            status = response.json().get("status")
        except Exception as e:
            LOGGER.warning(f"[Health Check Error] {e}")
            return True
        return status == "red" if force else status != "green"

    def close(self):
        if hasattr(self, "_client") and self._client:
            try:
                self._client.close()
                LOGGER.info("Elasticsearch client closed")
            except Exception:
                LOGGER.exception("Error closing Elasticsearch client")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
