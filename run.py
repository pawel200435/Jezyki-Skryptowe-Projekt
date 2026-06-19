import webview
from app import create_app
import threading
# enums import
from app.enums.WindowProperties import WindowProperties

# create flask app instance
app = create_app()



if __name__ == '__main__':

    #new thread for flask to work in background on port 5000
    flash_thread = threading.Thread(
        target=app.run,
        kwargs={'port': 5000}
    )
    flash_thread.daemon = True
    flash_thread.start()

    #creating desktop window
    webview.create_window(
        title=WindowProperties.NAME.value, 
        url="http://127.0.0.1:5000",
        width=WindowProperties.WIDTH.value,
        height=WindowProperties.HEIGHT.value,
        resizable=WindowProperties.RESIZABLE.value,
        min_size=WindowProperties.MIN_SIZE.value
    )

    webview.start()