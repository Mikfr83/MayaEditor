# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'helpwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be removed when recompiling UI file!
################################################################################

# ruff: noqa: F403, F405

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_form(object):
    def setupUi(self, form):
        if not form.objectName():
            form.setObjectName("form")
        form.resize(400, 300)
        self.grid_layout = QGridLayout(form)
        self.grid_layout.setObjectName("grid_layout")
        self.help_items = QComboBox(form)
        self.help_items.setObjectName("help_items")

        self.grid_layout.addWidget(self.help_items, 1, 1, 1, 1)

        self.search_help = QLineEdit(form)
        self.search_help.setObjectName("search_help")

        self.grid_layout.addWidget(self.search_help, 1, 0, 1, 1)

        self.label = QLabel(form)
        self.label.setObjectName("label")

        self.grid_layout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(form)

        QMetaObject.connectSlotsByName(form)

    # setupUi

    def retranslateUi(self, form):
        form.setWindowTitle(QCoreApplication.translate("form", "Form", None))
        self.label.setText(QCoreApplication.translate("form", "Search Help", None))

    # retranslateUi
