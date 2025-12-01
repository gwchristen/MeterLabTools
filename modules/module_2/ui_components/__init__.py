"""
UI Components Package for Created Histories Module
Provides both PyQt6 and Flet versions of all UI components
"""

# PyQt6 Components (original)
try:
    from .theme import ThemeManager, ColorScheme
    from .dashboard_cards import DashboardCard, MetricCard, StatisticsCard
    from .enhanced_grid import EnhancedDataGrid
    from .filter_sidebar import FilterSidebar, FilterBuilder
    from .form_builder import FormBuilder, FieldGroup
    from .validation_feedback import ValidationFeedback, Validator
    from .status_indicators import StatusIndicator, ProgressIndicator
except ImportError:
    # PyQt6 not available
    pass

# Flet Components
try:
    from .theme_flet import ThemeManager as ThemeManagerFlet
    from .theme_flet import ColorScheme as ColorSchemeFlet
    from .theme_flet import get_status_colors
    from .dashboard_cards_flet import MetricCard as MetricCardFlet
    from .dashboard_cards_flet import StatisticsCard as StatisticsCardFlet
    from .dashboard_cards_flet import InfoCard as InfoCardFlet
    from .enhanced_grid_flet import EnhancedDataGrid as EnhancedDataGridFlet
    from .filter_sidebar_flet import FilterSidebar as FilterSidebarFlet
    from .filter_sidebar_flet import FilterBuilder as FilterBuilderFlet
    from .filter_sidebar_flet import FilterCondition as FilterConditionFlet
    from .form_builder_flet import FormBuilder as FormBuilderFlet
    from .form_builder_flet import FieldGroup as FieldGroupFlet
    from .validation_feedback_flet import ValidationFeedback as ValidationFeedbackFlet
    from .validation_feedback_flet import Validator as ValidatorFlet
    from .validation_feedback_flet import ValidationGroup as ValidationGroupFlet
    from .status_indicators_flet import StatusIndicator as StatusIndicatorFlet
    from .status_indicators_flet import ProgressIndicator as ProgressIndicatorFlet
    from .status_indicators_flet import ActivityIndicator as ActivityIndicatorFlet
    from .status_indicators_flet import CountBadge as CountBadgeFlet
except ImportError:
    # Flet not available
    pass

__all__ = [
    # PyQt6 exports
    'ThemeManager',
    'ColorScheme',
    'DashboardCard',
    'MetricCard',
    'StatisticsCard',
    'EnhancedDataGrid',
    'FilterSidebar',
    'FilterBuilder',
    'FormBuilder',
    'FieldGroup',
    'ValidationFeedback',
    'Validator',
    'StatusIndicator',
    'ProgressIndicator',
    # Flet exports
    'ThemeManagerFlet',
    'ColorSchemeFlet',
    'get_status_colors',
    'MetricCardFlet',
    'StatisticsCardFlet',
    'InfoCardFlet',
    'EnhancedDataGridFlet',
    'FilterSidebarFlet',
    'FilterBuilderFlet',
    'FilterConditionFlet',
    'FormBuilderFlet',
    'FieldGroupFlet',
    'ValidationFeedbackFlet',
    'ValidatorFlet',
    'ValidationGroupFlet',
    'StatusIndicatorFlet',
    'ProgressIndicatorFlet',
    'ActivityIndicatorFlet',
    'CountBadgeFlet',
]
