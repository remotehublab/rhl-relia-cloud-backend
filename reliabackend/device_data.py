from reliabackend import redis_store

def delete_existing_session_data(session_identifier:  str):
    """
    Delete the existing session data so when the user loads a new task,
    does not see data from previous tasks.
    """

    devices_key = f'relia:data-uploader:sessions:{session_identifier}:devices'
    devices_set = redis_store.smembers(devices_key) or []

    for binary_device_name in devices_set:
        device_identifier: str = binary_device_name.decode()

        blocks_key = f'relia:data-uploader:sessions:{session_identifier}:devices:{device_identifier}:blocks'
        block_set = redis_store.smembers(blocks_key) or []

        for binary_block_name in block_set:
            block_identifier: str = binary_block_name.decode()
            redis_store.delete(f'relia:data-uploader:sessions:{session_identifier}:devices:{device_identifier}:blocks:{block_identifier}:from-gnuradio')
            redis_store.delete(f'relia:data-uploader:sessions:{session_identifier}:devices:{device_identifier}:blocks:{block_identifier}:alive')

        redis_store.delete(blocks_key)
    redis_store.delete(devices_key)
