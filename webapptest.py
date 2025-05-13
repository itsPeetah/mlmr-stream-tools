from src.webapp import WebApp, WebAppSettings


settings = WebAppSettings(__name__, 30000)
app = WebApp(settings)


def hello():
    return "Hello, webapp!"


app.register_get("/helo", hello)

app.start()
