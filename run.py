import webview
from app import create_app
import threading
# enums import
from app.enums.WindowProperties import WindowProperties
from sync_rss import sync_warnings_to_db

# create flask app instance
app = create_app()



if __name__ == '__main__':
    #run scraper automatically on startup
    with app.app_context():
        sync_warnings_to_db()

    #new thread for flask to work in background on port 5000
    flask_thread = threading.Thread(
        target=app.run,
        kwargs={'port': 5000}
    )
    flask_thread.daemon = True
    flask_thread.start()

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