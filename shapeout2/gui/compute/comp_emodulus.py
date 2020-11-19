import pkg_resources

from dclab.features.emodulus.viscosity import KNOWN_MEDIA

from PyQt5 import uic, QtCore, QtGui, QtWidgets

from ..analysis.ana_slot import SlotPanel
from ..widgets import show_wait_cursor


class ComputeEmodulus(QtWidgets.QDialog):
    #: Emitted when the pipeline is to be changed
    pipeline_changed = QtCore.pyqtSignal(dict)

    def __init__(self, parent, pipeline, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, parent, *args, **kwargs)
        path_ui = pkg_resources.resource_filename(
            "shapeout2.gui.compute", "comp_emodulus.ui")
        uic.loadUi(path_ui, self)
        # main
        self.parent = self.parent

        # set pipeline
        self.pipeline = pipeline

        # ui choices
        self.comboBox_medium.clear()
        choices = KNOWN_MEDIA + ["other"]
        for choice in choices:
            if choice == "CellCarrierB":
                name = "CellCarrier B"  # [sic]
            else:
                name = choice
            self.comboBox_medium.addItem(name, choice)
        self.comboBox_medium.addItem("not defined", "undefined")
        self.comboBox_medium.addItem("unchanged", "unchanged")
        self.comboBox_medium.currentIndexChanged.connect(self.on_cb_medium)
        self.comboBox_medium.setCurrentIndex(self.comboBox_medium.count()-1)

        self.comboBox_temp.clear()
        self.comboBox_temp.addItem("From feature", "feature")
        self.comboBox_temp.addItem("From meta data", "config")
        self.comboBox_temp.addItem("Manual", "manual")
        self.comboBox_temp.currentIndexChanged.connect(self.on_cb_temp)
        self.comboBox_temp.setCurrentIndex(self.comboBox_temp.count()-1)

        # buttons
        btn_ok = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        btn_ok.clicked.connect(self.on_ok)
        btn_cancel = self.buttonBox.button(QtGui.QDialogButtonBox.Cancel)
        btn_cancel.clicked.connect(self.on_cancel)

    @QtCore.pyqtSlot()
    def on_cancel(self):
        self.close()

    @QtCore.pyqtSlot()
    def on_ok(self):
        self.set_emodulus_properties()
        self.update_ui()

    def on_cb_medium(self):
        """User changed medium"""
        medium = self.comboBox_medium.currentData()
        if medium in KNOWN_MEDIA + ["unchanged"]:
            self.doubleSpinBox_visc.setEnabled(False)
            self.comboBox_temp.setEnabled(True)
        else:
            self.doubleSpinBox_visc.setEnabled(True)
            self.comboBox_temp.setEnabled(False)
        self.on_cb_temp()

    def on_cb_temp(self):
        """User changed temperature"""
        temp = self.comboBox_temp.currentData()

        if not self.comboBox_temp.isEnabled() or temp in ["feature", "config"]:
            self.doubleSpinBox_temp.setEnabled(False)
        else:
            self.doubleSpinBox_temp.setEnabled(True)

    @show_wait_cursor
    @QtCore.pyqtSlot()
    def set_emodulus_properties(self):
        """Set the given emodulus properties for all datasets"""
        medium = self.comboBox_medium.currentData()
        if self.comboBox_temp.isEnabled():
            temp = self.comboBox_temp.currentData()
        else:
            temp = None
        if self.doubleSpinBox_temp.isEnabled():
            tempval = self.doubleSpinBox_temp.value()
        else:
            tempval = None
        if self.doubleSpinBox_visc.isEnabled():
            viscval = self.doubleSpinBox_visc.value()
        else:
            viscval = None

        if len(self.pipeline.slots) == 0:
            return

        for slot in self.pipeline.slots:
            ds = slot.get_dataset()

            # Use the internal sanity checks to determine whether
            # or not we can set the medium or temperature scenarios.
            choices_medium = SlotPanel.get_dataset_choices_medium(ds)
            choices_temp = SlotPanel.get_dataset_choices_temperature(ds)
            if medium in [m[1] for m in choices_medium]:
                state = slot.__getstate__()
                state["emodulus"]["emodulus medium"] = medium
                slot.__setstate__(state)

                # Set the viscosity here, because unknown media are
                # available.
                if viscval is not None:
                    state["emodulus"]["emodulus viscosity"] = viscval

            if temp in [t[1] for t in choices_temp]:  # temp is not None
                state = slot.__getstate__()
                state["emodulus"]["emodulus scenario"] = temp
                if tempval is not None:
                    state["emodulus"]["emodulus temperature"] = tempval
                slot.__setstate__(state)

            print(state["emodulus"])

    def update_ui(self):
        """Update all relevant parts of the main user interface"""
        state = self.pipeline.__getstate__()
        self.pipeline_changed.emit(state)