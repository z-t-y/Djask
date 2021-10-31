import os
import os.path as path
import typing as t

from apiflask import APIFlask
from apiflask.exceptions import HTTPError

from .extensions import bootstrap, compress, csrf, db
from .types import Config, ErrorResponse


def _check_empty(data: t.Any) -> t.Any:
    return data if data else ""


class Djask(APIFlask):
    def __init__(
        self,
        import_name: t.Optional[str],
        config: t.Optional[Config] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*[import_name, *args], **kwargs)
        self.config.setdefault("ADMIN_SITE", False)
        self.config.setdefault("ADMIN_MODEL_MAP", {})
        self.config.setdefault("SECRET_KEY", "djask_secret_key")
        self.secret_key = os.getenv("SECRET_KEY", "djask_secret_key")
        if config:  # pragma: no cover
            for k, v in config.items():
                self.config[k] = v
        self.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.template_folder = path.abspath(
            path.join(path.dirname(__file__), "templates")
        )

        self._register_extensions()

    def _register_extensions(self) -> None:
        """Register the built-in extensions"""
        for ext in (
            bootstrap,
            compress,
            csrf,
            db,
        ):
            ext.init_app(self)
        self.db = db

    @staticmethod
    def _error_handler(error: HTTPError) -> ErrorResponse:
        """Override the default error handler in APIFlask"""
        status_code, message = (
            _check_empty(error.status_code),
            _check_empty(error.message),
        )
        detail = error.detail
        body = f"{status_code} {message}{'<br />'+detail if detail else ''}"
        return body, error.status_code, error.headers
