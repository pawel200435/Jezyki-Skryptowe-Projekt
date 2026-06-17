import webview
from app import create_app
# enums import
from app.enums.WindowProperties import WindowProperties

# create flask app instance
app = create_app()



if __name__ == '__main__':
    #creating desktop window
    webview.create_window(
        title=WindowProperties.NAME.value, 
        url=app,
        width=WindowProperties.WIDTH.value,
        height=WindowProperties.HEIGHT.value,
        resizable=WindowProperties.RESIZABLE.value,
        min_size=WindowProperties.MIN_SIZE.value
    )

    webview.start()