# coding=utf-8

"""Test Minimum Needs Tools."""


import unittest
import os

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import (
    standard_data_path, get_qgis_app, load_test_vector_layer)

from qgis.PyQt import QtGui, QtWidgets
from qgis.core import QgsProject

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from safe.gui.tools.minimum_needs.needs_calculator_dialog import (
    NeedsCalculatorDialog)
from safe.utilities.unicode import byteify


class MinimumNeedsTest(unittest.TestCase):

    """Test class to facilitate importing shakemaps."""

    def tearDown(self):
        """Run after each test."""
        result_path_base = standard_data_path('other', 'minimum_needs_perka7')
        # noinspection PyArgumentList
        QgsProject.instance().removeAllMapLayers()
        for extension in ['shp', 'shx', 'dbf', 'prj', 'keywords']:
            path = result_path_base + '.' + extension
            if os.path.exists(path):
                os.remove(path)

    def test_minimum_needs_calculator(self):
        """Test behaviour of the minimum needs function."""
        dialog = NeedsCalculatorDialog(PARENT)
        layer = load_test_vector_layer('other', 'minimum_needs.shp')
        QgsProject.instance().addMapLayers([layer])

        # Set selected layer and displaced field
        dialog.layer.setLayer(layer)
        dialog.displaced.setField('displaced')

        # run minimum needs function
        dialog.accept()

        # get output layer
        layer = dialog.result_layer

        assert layer is not None
        field_names = [field.name() for field in layer.fields()]
        for feature in layer.getFeatures():
            value = [attribute for attribute in feature.attributes()]

        actual_attributes = dict(list(zip(field_names, value)))

        expected_attributes = {
            'displaced': 1000,
            'minimum_needs__rice': 2800,
            'minimum_needs__drinking_water': 17500,
            'minimum_needs__clean_water': 67000,
            'minimum_needs__family_kits': 200,
            'minimum_needs__toilets': 50}

        self.assertDictEqual(
            byteify(expected_attributes),
            byteify(actual_attributes))

    def test_ok_button(self):
        """Test behaviour of Ok button."""
        # Test Ok button without any input in the combo box
        dialog = NeedsCalculatorDialog(PARENT)
        ok_button = dialog.button_box.button(QtWidgets.QDialogButtonBox.Ok)

        self.assertFalse(ok_button.isEnabled())

        # Close because this is a modal dialog
        dialog.reject()

        input_layer = load_test_vector_layer('other', 'minimum_needs.shp')

        QgsProject.instance().addMapLayers([input_layer])

        # Open the dialog again
        dialog = NeedsCalculatorDialog(PARENT)
        ok_button = dialog.button_box.button(QtWidgets.QDialogButtonBox.Ok)

        # Test Ok button with layer and displaced field
        # selected in the combo box
        dialog.layer.setLayer(input_layer)
        dialog.displaced.setField('displaced')

        self.assertTrue(ok_button.isEnabled())


if __name__ == "__main__":
    # noinspection PyArgumentEqualDefault
    suite = unittest.makeSuite(MinimumNeedsTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
