import json

def cached(cache_path):
    def factory(func):

        def inner(*args, **kwargs):
            read_cache = kwargs.get('read_cache', True)
            write_cache = False
            result = None

            if read_cache:
                try:
                    with open(cache_path, 'r') as file:
                        result = json.load(file)
                except Exception as e:
                    print(f'Failed to read cache for {func.__name__}: {e}')

            if not result:
                result = func(*args, **kwargs)
                write_cache = True

            try:
                with open(cache_path, 'w') as file:
                    json.dump(result, file)
            except Exception as e:
                print(f'Failed to write cache for {func.__name__}: {e}')

            return result

        return inner

    return factory

