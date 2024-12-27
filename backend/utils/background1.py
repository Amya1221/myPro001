import time
from multiprocessing import Process, Manager


def background_update_ohlcv(scriplist, scripdata, ohlcv_data, data_service):
    """
    Background task to update OHLCV data periodically.
    """
    while True:
        print('Updating OHLCV data...')
        try:
            updated_data, updated_symbol = data_service.update_data(ohlcv_data, scriplist, scripdata)
            # Update the shared dictionary with new data
            for key, value in updated_data.items():
                ohlcv_data[key] = value  # This updates the shared data accessible to the main process
            print('Update successful')
        except Exception as e:
            print(f'Error during update: {e}')

        # Sleep for 10 minutes before the next update
        time.sleep(600)


def start_background_update_process(scriplist, scripdata, ohlcv_data, data_service):
    """
    Starts the background update task in a separate process.
    """
    print('background process starts')
    process = Process(
        target=background_update_ohlcv,
        args=(scriplist, scripdata, ohlcv_data, data_service),
        daemon=True  # Daemon process to exit with the main process
    )
    process.start()
    print(f"Started background update process with PID {process.pid}")
