import json
import logging
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


def cached(cache_path: str, model: type[BaseModel] | None = None, reload: bool = True):
    def factory(func: Callable[[], Any]):
        reloaded = False

        def inner():
            nonlocal reloaded

            if reloaded or not reload:
                try:
                    with open(cache_path, 'r') as file:
                        json_data = json.load(file)
                    return model.model_validate(json_data) if model else json_data
                except Exception:
                    logger.exception(f'Failed to read cache for {func.__name__}')

            result = func()

            try:
                json_data = result.model_dump() if model else result
                with open(cache_path, 'w') as file:
                    json.dump(json_data, file)
                    reloaded = True
            except Exception:
                logger.exception(f'Failed to write cache for {func.__name__}')

            return result

        return inner

    return factory
