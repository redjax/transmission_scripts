import os

from textual.app import App
from textual.widgets import Tree


class FileManagerApp(App):
    def compose(self):
        tree = Tree("Root Directory")
        self.populate_tree(tree.root, os.getcwd())

        yield tree

    def populate_tree(self, node, path):
        try:
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)

                if os.path.isdir(full_path):
                    sub_node = node.add(entry)
                    self.populate_tree(sub_node, full_path)
                else:
                    node.add(entry)
        except PermissionError:
            pass


if __name__ == "__main__":
    FileManagerApp().run()
