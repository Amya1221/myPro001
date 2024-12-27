import time


def background_update_ohlcv(scriplist, scripdata, ohlcv_data, data_service):
    """
    Background task to update OHLCV data periodically.
    """
    while True:
        print('Updating OHLCV data...')
        try:
            updated_data,updated_symbol = data_service.update_data(ohlcv_data,scriplist,scripdata)
            # Ensure the updated data is merged into the global ohlcv_data
            # print(ohlcv_data)
            ohlcv_data.update(updated_data)  # Update the global OHLCV data
            print('Update successful')
            print(ohlcv_data)
            # Optionally, emit a SocketIO event here to notify clients of the update
            # socketio.emit('ohlcv_update', updated_data)
        except Exception as e:
            print(f'Error during update: {e}')

        # Sleep for 10 minutes before running the task again
        time.sleep(600)  # Update every 10 minutes


def start_background_update_thread(socketio, scriplist, scripdata, ohlcv_data, data_service):
    """
    Start a background thread for updating OHLCV data.
    """
    # Start the background task using SocketIO's background_task feature
    socketio.start_background_task(
        target=background_update_ohlcv,
        scriplist=scriplist,
        scripdata=scripdata,
        ohlcv_data=ohlcv_data,
        data_service=data_service  # Pass the DataService instance
    )
