from . import dm_element


class MatrixElement(dm_element.MatrixElement):
    def update_content(self, quickview=False):
        if self.active and self.enabled:
            color = "#86E7C1"  # turquois
            label = "used"
            tooltip = "Click to deactivate"
        elif self.active and not self.enabled:
            color = "#C9DAD7"  # gray-turquois
            label = "unused\n(disabled)"
            tooltip = "Click to deactivate"
        elif not self.active and self.enabled:
            color = "#EFEFEF"  # light gray
            label = "unused"
            tooltip = "Click to activate"
        else:
            color = "#DCDCDC"  # gray
            label = "used\n(disabled)"
            tooltip = "Click to activate"

        self.setStyleSheet("background-color:{}".format(color))
        self.label.setStyleSheet("background-color:{}".format(color))
        self.label.setText(label)
        self.setToolTip(tooltip)
        self.label.setToolTip(tooltip)
