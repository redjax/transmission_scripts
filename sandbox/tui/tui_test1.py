from textual.app import App
from textual.widgets import Header, Footer, Static


class HelloWorldApp(App):
    def compose(self):
        yield Header()
        yield Static("Hello, World!", id="hello-text")
        yield Footer()


if __name__ == "__main__":
    HelloWorldApp().run()
