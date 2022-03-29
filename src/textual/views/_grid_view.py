from ..screen import Screen
from ..layouts.grid import GridLayout


class GridView(Screen, layout=GridLayout):
    @property
    def grid(self) -> GridLayout:
        assert isinstance(self.layout, GridLayout)
        return self.layout
