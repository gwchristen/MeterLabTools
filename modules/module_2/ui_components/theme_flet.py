"""
Theme Manager for Flet - Professional color schemes and theming
Provides WCAG 2.1 AA compliant color schemes for Light and Dark themes
"""

import flet as ft
from dataclasses import dataclass
from typing import Optional


@dataclass
class ColorScheme:
    """Color scheme for theming"""
    
    # Primary colors
    primary: str
    primary_hover: str
    primary_light: str
    
    # Secondary colors
    secondary: str
    secondary_hover: str
    
    # Background colors
    background: str
    background_alt: str
    surface: str
    surface_hover: str
    
    # Text colors
    text: str
    text_secondary: str
    text_disabled: str
    
    # Accent colors
    accent: str
    success: str
    warning: str
    error: str
    info: str
    
    # Border colors
    border: str
    border_light: str
    
    # Grid colors
    grid_header: str
    grid_row_alt: str
    grid_row_hover: str
    grid_selected: str


class ThemeManager:
    """Manages Flet themes and provides consistent styling"""
    
    # WCAG 2.1 AA compliant color schemes
    LIGHT_THEME = ColorScheme(
        # Primary - Professional blue
        primary="#2563eb",
        primary_hover="#1d4ed8",
        primary_light="#dbeafe",
        
        # Secondary - Neutral gray
        secondary="#64748b",
        secondary_hover="#475569",
        
        # Backgrounds
        background="#ffffff",
        background_alt="#f8fafc",
        surface="#ffffff",
        surface_hover="#f1f5f9",
        
        # Text
        text="#0f172a",
        text_secondary="#475569",
        text_disabled="#94a3b8",
        
        # Accents
        accent="#8b5cf6",
        success="#22c55e",
        warning="#f59e0b",
        error="#ef4444",
        info="#0ea5e9",
        
        # Borders
        border="#e2e8f0",
        border_light="#f1f5f9",
        
        # Grid
        grid_header="#1e293b",
        grid_row_alt="#f8fafc",
        grid_row_hover="#e0f2fe",
        grid_selected="#dbeafe",
    )
    
    DARK_THEME = ColorScheme(
        # Primary - Professional blue
        primary="#3b82f6",
        primary_hover="#2563eb",
        primary_light="#1e3a8a",
        
        # Secondary - Neutral gray
        secondary="#94a3b8",
        secondary_hover="#cbd5e1",
        
        # Backgrounds
        background="#0f172a",
        background_alt="#1e293b",
        surface="#1e293b",
        surface_hover="#334155",
        
        # Text
        text="#f8fafc",
        text_secondary="#cbd5e1",
        text_disabled="#64748b",
        
        # Accents
        accent="#a78bfa",
        success="#4ade80",
        warning="#fbbf24",
        error="#f87171",
        info="#38bdf8",
        
        # Borders
        border="#334155",
        border_light="#475569",
        
        # Grid
        grid_header="#0f172a",
        grid_row_alt="#1e293b",
        grid_row_hover="#1e3a8a",
        grid_selected="#1e40af",
    )
    
    @staticmethod
    def get_colors(theme: str = "Light") -> ColorScheme:
        """Get color scheme for theme"""
        return ThemeManager.LIGHT_THEME if theme == "Light" else ThemeManager.DARK_THEME
    
    @staticmethod
    def get_flet_theme(theme: str = "Light") -> ft.Theme:
        """Get Flet Theme object for the specified theme"""
        colors = ThemeManager.get_colors(theme)
        
        return ft.Theme(
            color_scheme_seed=colors.primary,
            color_scheme=ft.ColorScheme(
                primary=colors.primary,
                on_primary=ft.Colors.WHITE,
                secondary=colors.secondary,
                on_secondary=ft.Colors.WHITE,
                surface=colors.surface,
                on_surface=colors.text,
                error=colors.error,
                on_error=ft.Colors.WHITE,
            ),
        )
    
    @staticmethod
    def get_theme_mode(theme: str = "Light") -> ft.ThemeMode:
        """Get Flet ThemeMode for the specified theme"""
        return ft.ThemeMode.LIGHT if theme == "Light" else ft.ThemeMode.DARK


def get_status_colors(status: str) -> dict:
    """Get colors for status indicators"""
    status_styles = {
        'active': {
            'bg': '#d1fae5',
            'border': '#22c55e',
            'text': '#065f46',
            'icon': '●'
        },
        'inactive': {
            'bg': '#e5e7eb',
            'border': '#9ca3af',
            'text': '#374151',
            'icon': '○'
        },
        'pending': {
            'bg': '#fef3c7',
            'border': '#f59e0b',
            'text': '#92400e',
            'icon': '◐'
        },
        'error': {
            'bg': '#fee2e2',
            'border': '#ef4444',
            'text': '#991b1b',
            'icon': '✕'
        },
        'success': {
            'bg': '#d1fae5',
            'border': '#22c55e',
            'text': '#065f46',
            'icon': '✓'
        },
        'warning': {
            'bg': '#fed7aa',
            'border': '#f97316',
            'text': '#7c2d12',
            'icon': '⚠'
        },
        'info': {
            'bg': '#dbeafe',
            'border': '#3b82f6',
            'text': '#1e40af',
            'icon': 'ⓘ'
        }
    }
    return status_styles.get(status, status_styles['inactive'])
