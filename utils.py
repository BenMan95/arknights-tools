import json

from typing import Callable
from pydantic import BaseModel

import logging
logger = logging.getLogger(__name__)

def cached(cache_path: str, model: BaseModel = None, reload: bool = True):
    def factory(func: Callable[[], any]):
        reloaded = False
        def inner():
            nonlocal reloaded

            result = None

            if reloaded or not reload:
                try:
                    with open(cache_path, 'r') as file:
                        json_data = json.load(file)
                    result = model.model_validate(json_data) if model else json_data
                    return result
                except Exception as e:
                    logger.error(f'Failed to read cache for {func.__name__}')

            result = func()

            try:
                json_data = result.model_dump() if model else result
                with open(cache_path, 'w') as file:
                    json.dump(json_data, file)
                    reloaded = True
            except Exception as e:
                logger.error(f'Failed to write cache for {func.__name__}')

            return result

        return inner

    return factory


