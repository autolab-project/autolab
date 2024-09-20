# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 18:45:37 2024

@author: jonathan
"""

from typing import Dict


theme = {
    'dark': {
        'text_color': "#f0f0f0",
        'text_disabled_color': "#a0a0a0",
        'default': "#3c3c3c",
        'primary_color': "#3c3c3c",
        'secondary_color': "#2c2c2c",
        'tertiary_color': "#2e2e2e",
        'hover_color': "#555555",
        'pressed_color': "#666666",
        'selected_color': "#005777",
        'border_color': "#5c5c5c",
        'main_hover': "#005777",
        }
    }


def get_theme(theme_name: str) -> Dict[str, str]:
    return theme.get(theme_name)


def create_stylesheet(theme: Dict[str, str]) -> str:
    stylesheet = f"""
        QWidget {{
            background-color: {theme['default']};
            color: {theme['text_color']};
        }}
        QFrame {{
            background-color: {theme['primary_color']};
            border-radius: 8px;
        }}
        QFrame[frameShape='1'], QFrame[frameShape='2'], QFrame[frameShape='3'], QFrame[frameShape='6'] {{
            border: 1px solid {theme['border_color']};
        }}
        #line_V {{
            border-left: 1px solid {theme['border_color']};
        }}
        #line_H {{
            border-top: 1px solid {theme['border_color']};
        }}
        QPushButton {{
            background-color: {theme['secondary_color']};
            border: 1px solid {theme['border_color']};
            border-radius: 6px;
            padding: 4px;
            margin: 2px;
        }}
        QPushButton:hover {{
            background-color: {theme['hover_color']};
            border: 1px solid {theme['border_color']};
        }}
        QPushButton:pressed {{
            background-color: {theme['pressed_color']};
        }}
        QPushButton:disabled {{
            background-color: {theme['primary_color']};
            color: {theme['text_disabled_color']};
            border: 1px solid {theme['border_color']};
            border-radius: 6px;
        }}
        QCheckBox {{
            background-color: {theme['primary_color']};
            border-radius: 4px;
        }}
        QLineEdit, QTextEdit {{
            background-color: {theme['secondary_color']};
            border: 1px solid {theme['border_color']};
            border-radius: 4px;
        }}
        QLineEdit:disabled, QLineEdit[readOnly="true"] {{
            background-color: {theme['primary_color']};
            color: {theme['text_disabled_color']};
            border: 1px solid {theme['border_color']};
            border-radius: 4px;
        }}
        QComboBox {{
            background-color: {theme['secondary_color']};
            padding: 3px;
            border-radius: 5px;
        }}
        QTreeView {{
            alternate-background-color: {theme['secondary_color']};
            border-radius: 6px;
        }}
        QHeaderView::section {{
            background-color: {theme['secondary_color']};
            border: 1px solid {theme['primary_color']};
        }}
        QTabWidget::pane {{
            border: 1px solid {theme['border_color']};
            border-radius: 5px;
        }}
        QTabBar::tab {{
            background-color: {theme['tertiary_color']};
            border: 1px solid {theme['border_color']};
            padding: 5px;
            border-radius: 4px;
        }}
        QTabBar::tab:hover {{
            background-color: {theme['primary_color']};
            border: 1px solid {theme['hover_color']};
        }}
        QTabBar::tab:selected {{
            background-color: {theme['primary_color']};
            border: 1px solid {theme['hover_color']};
            margin-top: -2px;
            border-radius: 4px;
        }}
        QTabBar::tab:selected:hover {{
            background-color: {theme['primary_color']};
            border: 1px solid {theme['hover_color']};
            margin-top: -2px;
        }}
        QTabBar::tab:!selected {{
            margin-top: 2px;
        }}
        QMenuBar {{
            background-color: {theme['secondary_color']};
            border-radius: 5px;
        }}
        QMenuBar::item {{
            background-color: transparent;
            padding: 4px 10px;
            border-radius: 4px;
        }}
        QMenuBar::item:selected {{
            background-color: {theme['primary_color']};
            border: 1px solid {theme['pressed_color']};
        }}
        QMenu {{
            background-color: {theme['secondary_color']};
            border: 1px solid {theme['border_color']};
            border-radius: 6px;
        }}
        QMenu::item {{
            background-color: {theme['secondary_color']};
        }}
        QMenu::item:selected {{
            background-color: {theme['primary_color']};
        }}
        QMenu::item:disabled {{
            background-color: {theme['primary_color']};
            color: {theme['text_disabled_color']};
        }}
        QTreeWidget {{
            background-color: {theme['tertiary_color']};
            alternate-background-color: {theme['primary_color']};
        }}
        QTreeWidget::item {{
            border: none;
        }}
        QTreeWidget::item:hover {{
            background-color: {theme['main_hover']};
        }}
        QTreeWidget::item:selected {{
            background-color: {theme['selected_color']};
        }}
        QTreeWidget::item:selected:hover {{
            background-color: {theme['main_hover']};
        }}
        QScrollBar:vertical {{
            border: 1px solid {theme['primary_color']};
            background-color: {theme['tertiary_color']};
            width: 16px;
            border-radius: 6px;
        }}
        QScrollBar:horizontal {{
            border: 1px solid {theme['primary_color']};
            background-color: {theme['tertiary_color']};
            height: 16px;
            border-radius: 6px;
        }}
        QScrollBar::handle {{
            background-color: {theme['border_color']};
            border: 1px solid {theme['pressed_color']};
            border-radius: 6px;
        }}
        QScrollBar::handle:hover {{
            background-color: {theme['pressed_color']};
        }}
        QScrollBar::add-line, QScrollBar::sub-line {{
            background-color: {theme['primary_color']};
        }}
    """

    return stylesheet
