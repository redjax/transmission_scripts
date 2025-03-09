from textual.app import App
from textual.widgets import Header, Footer, Static


class HelloWorldApp(App):
    CSS = """
    #hello-text {
        color: green;
        background: black;
        border: round yellow;
    }
    """

    def compose(self):
        yield Header()
        yield Static("Hello, World!", id="hello-text")
        yield Footer()


if __name__ == "__main__":
    HelloWorldApp().run()
