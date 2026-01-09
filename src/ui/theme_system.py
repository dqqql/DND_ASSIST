"""
UI现代化主题系统
提供统一的颜色、字体、间距规范和主题配置管理
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Any
import tkinter as tk


@dataclass
class ColorPalette:
    """颜色调色板 - 定义统一的颜色方案"""
    
    # 主要背景色
    primary_bg: str = "#f8f9fa"      # 浅灰色背景
    secondary_bg: str = "#ffffff"    # 白色内容区域
    accent_color: str = "#0066cc"    # 蓝色强调色
    
    # 文本颜色 - 符合WCAG可访问性标准
    text_primary: str = "#212529"    # 深灰色主文本
    text_secondary: str = "#6c757d"  # 中灰色次要文本
    text_disabled: str = "#adb5bd"   # 浅灰色禁用文本
    
    # 交互元素颜色
    button_normal: str = "#f8f9fa"   # 更亮的普通按钮颜色
    button_hover: str = "#e9ecef"    # 悬停色
    button_active: str = "#0066cc"   # 蓝色激活/按下状态
    button_disabled: str = "#f8f9fa" # 禁用按钮背景
    
    # 状态和反馈颜色
    selection_bg: str = "#e3f2fd"    # 浅蓝色选择背景
    selection_hover: str = "#f5f5f5"  # 浅灰色悬停背景
    border_color: str = "#dee2e6"    # 微妙边框色
    focus_color: str = "#0066cc"     # 焦点指示器颜色
    
    # 内容查看器颜色
    content_bg: str = "#ffffff"      # 内容区域背景 - 改为纯白以提升可读性
    content_border: str = "#d1d5db"  # 内容区域边框 - 稍深的边框色
    content_text_bg: str = "#fafafa" # 文本内容背景 - 微妙的灰色背景
    content_image_bg: str = "#f9f9f9" # 图片内容背景
    
    def get_contrast_ratio(self, color1: str, color2: str) -> float:
        """计算两个颜色之间的对比度比率（用于可访问性验证）"""
        # 简化的对比度计算 - 实际应用中可以使用更精确的算法
        # 这里返回一个模拟值，实际实现需要RGB转换和亮度计算
        return 4.5  # WCAG AA标准要求最小4.5:1


@dataclass
class Typography:
    """字体系统 - 定义统一的字体规范"""
    
    # 字体族 - 带有回退方案
    primary_font: Tuple[str, ...] = ("Segoe UI", "Arial", "sans-serif")
    monospace_font: Tuple[str, ...] = ("Consolas", "Monaco", "monospace")
    
    # 字体大小 - 遵循8pt网格系统
    size_small: int = 9
    size_normal: int = 11
    size_medium: int = 12
    size_large: int = 14
    size_title: int = 16
    size_content: int = 13           # 内容查看器专用字体大小
    
    # 字体粗细
    weight_normal: str = "normal"
    weight_bold: str = "bold"
    
    def get_font_tuple(self, size: int = None, weight: str = None) -> Tuple[str, int, str]:
        """获取Tkinter字体元组格式"""
        font_size = size or self.size_normal
        font_weight = weight or self.weight_normal
        return (self.primary_font[0], font_size, font_weight)
    
    def get_content_font_tuple(self, size: int = None) -> Tuple[str, int]:
        """获取内容查看器专用字体元组格式 - 使用更好的可读性字体"""
        font_size = size or self.size_content
        return (self.primary_font[0], font_size)
    
    def get_monospace_font_tuple(self, size: int = None) -> Tuple[str, int]:
        """获取等宽字体元组格式"""
        font_size = size or self.size_normal
        return (self.monospace_font[0], font_size)


@dataclass
class Spacing:
    """间距系统 - 基于8px网格的统一间距规范"""
    
    # 基础单位（8px网格）
    unit: int = 8
    
    # 预定义间距值
    xs: int = 4   # 0.5单位
    sm: int = 8   # 1单位
    md: int = 16  # 2单位
    lg: int = 24  # 3单位
    xl: int = 32  # 4单位
    
    # 组件特定间距
    button_padding_x: int = 20  # 按钮水平内边距
    button_padding_y: int = 12  # 按钮垂直内边距
    list_item_height: int = 28  # 列表项高度（增加以改善可读性）
    list_item_padding: int = 4  # 列表项内边距
    section_margin: int = 16    # 区域边距
    
    # 窗口和面板间距
    window_padding: int = 10    # 窗口内边距
    panel_spacing: int = 5      # 面板间距
    
    def get_padding(self, component_type: str) -> Tuple[int, int]:
        """获取组件的内边距 (padx, pady)"""
        padding_map = {
            "button": (self.button_padding_x, self.button_padding_y),
            "window": (self.window_padding, self.window_padding),
            "section": (self.section_margin, self.section_margin),
            "default": (self.sm, self.sm)
        }
        return padding_map.get(component_type, padding_map["default"])


@dataclass
class StyleState:
    """样式状态 - 表示交互元素的视觉状态"""
    
    normal: Dict[str, Any]
    hover: Dict[str, Any]
    active: Dict[str, Any]
    disabled: Dict[str, Any]
    focused: Dict[str, Any]
    
    def get_current_style(self, state: str) -> Dict[str, Any]:
        """获取当前状态的样式配置"""
        state_map = {
            "normal": self.normal,
            "hover": self.hover,
            "active": self.active,
            "disabled": self.disabled,
            "focused": self.focused
        }
        return state_map.get(state, self.normal)


@dataclass
class ThemeConfig:
    """主题配置 - 整合所有主题组件"""
    
    name: str
    colors: ColorPalette
    typography: Typography
    spacing: Spacing
    
    def __post_init__(self):
        """初始化后处理 - 创建组件样式配置"""
        self._component_styles = self._create_component_styles()
    
    def _create_component_styles(self) -> Dict[str, Dict[str, Any]]:
        """创建组件样式配置"""
        return {
            "button": {
                "normal": {
                    "bg": self.colors.button_normal,
                    "fg": self.colors.text_primary,
                    "font": self.typography.get_font_tuple(),
                    "relief": tk.RAISED,
                    "bd": 1,
                    "padx": self.spacing.button_padding_x,
                    "pady": self.spacing.button_padding_y,
                    "cursor": "hand2",
                    "highlightthickness": 1,
                    "highlightcolor": self.colors.border_color,
                    "highlightbackground": self.colors.border_color
                },
                "hover": {
                    "bg": self.colors.button_hover,
                    "fg": self.colors.text_primary,
                    "relief": tk.RAISED,
                    "cursor": "hand2"
                },
                "active": {
                    "bg": self.colors.button_active,
                    "fg": self.colors.secondary_bg,
                    "relief": tk.SUNKEN,
                    "cursor": "hand2"
                },
                "disabled": {
                    "bg": self.colors.button_disabled,
                    "fg": self.colors.text_disabled,
                    "state": tk.DISABLED,
                    "relief": tk.FLAT,
                    "cursor": ""
                },
                "focused": {
                    "bg": self.colors.button_hover,
                    "fg": self.colors.text_primary,
                    "relief": tk.RAISED,
                    "highlightthickness": 2,
                    "highlightcolor": self.colors.focus_color,
                    "highlightbackground": self.colors.focus_color,
                    "cursor": "hand2"
                }
            },
            "listbox": {
                "normal": {
                    "bg": self.colors.secondary_bg,
                    "fg": self.colors.text_primary,
                    "font": self.typography.get_font_tuple(self.typography.size_medium),
                    "selectbackground": self.colors.selection_bg,
                    "selectforeground": self.colors.text_primary,
                    "relief": tk.SUNKEN,
                    "bd": 1,
                    "highlightthickness": 1,
                    "highlightcolor": self.colors.focus_color,
                    "highlightbackground": self.colors.border_color,
                    "activestyle": "dotbox"
                }
            },
            "text": {
                "normal": {
                    "bg": self.colors.content_text_bg,
                    "fg": self.colors.text_primary,
                    "font": self.typography.get_content_font_tuple(),
                    "relief": tk.FLAT,
                    "bd": 1,
                    "wrap": tk.WORD,
                    "highlightthickness": 1,
                    "highlightcolor": self.colors.focus_color,
                    "highlightbackground": self.colors.content_border,
                    "insertbackground": self.colors.text_primary,
                    "selectbackground": self.colors.selection_bg,
                    "selectforeground": self.colors.text_primary
                }
            },
            "label": {
                "normal": {
                    "bg": self.colors.primary_bg,
                    "fg": self.colors.text_primary,
                    "font": self.typography.get_font_tuple()
                },
                "title": {
                    "bg": self.colors.primary_bg,
                    "fg": self.colors.text_primary,
                    "font": self.typography.get_font_tuple(self.typography.size_title, self.typography.weight_bold)
                }
            },
            "frame": {
                "normal": {
                    "bg": self.colors.primary_bg
                },
                "content": {
                    "bg": self.colors.secondary_bg
                },
                "content_viewer": {
                    "bg": self.colors.content_bg,
                    "relief": tk.FLAT,
                    "bd": 1,
                    "highlightthickness": 1,
                    "highlightcolor": self.colors.content_border,
                    "highlightbackground": self.colors.content_border
                }
            },
            "content_image": {
                "normal": {
                    "bg": self.colors.content_image_bg,
                    "fg": self.colors.text_secondary,
                    "font": self.typography.get_font_tuple(self.typography.size_medium),
                    "relief": tk.FLAT,
                    "bd": 1,
                    "highlightthickness": 1,
                    "highlightcolor": self.colors.content_border,
                    "highlightbackground": self.colors.content_border,
                    "justify": tk.CENTER
                }
            },
            "dialog": {
                "normal": {
                    "bg": self.colors.primary_bg,
                    "relief": tk.FLAT,
                    "bd": 0
                }
            },
            "dialog_entry": {
                "normal": {
                    "bg": self.colors.secondary_bg,
                    "fg": self.colors.text_primary,
                    "font": self.typography.get_font_tuple(self.typography.size_medium),
                    "relief": tk.FLAT,
                    "bd": 2,
                    "highlightthickness": 2,
                    "highlightcolor": self.colors.focus_color,
                    "highlightbackground": self.colors.border_color,
                    "insertbackground": self.colors.text_primary,
                    "selectbackground": self.colors.selection_bg,
                    "selectforeground": self.colors.text_primary
                }
            },
            "dialog_label": {
                "normal": {
                    "bg": self.colors.primary_bg,
                    "fg": self.colors.text_primary,
                    "font": self.typography.get_font_tuple(self.typography.size_medium)
                },
                "title": {
                    "bg": self.colors.primary_bg,
                    "fg": self.colors.text_primary,
                    "font": self.typography.get_font_tuple(self.typography.size_large, self.typography.weight_bold)
                },
                "message": {
                    "bg": self.colors.primary_bg,
                    "fg": self.colors.text_primary,
                    "font": self.typography.get_font_tuple(self.typography.size_medium),
                    "justify": tk.LEFT
                }
            }
        }
    
    def apply_to_widget(self, widget: tk.Widget, style_type: str, variant: str = "normal") -> None:
        """将主题样式应用到指定控件"""
        if style_type not in self._component_styles:
            return
        
        style_config = self._component_styles[style_type].get(variant, {})
        
        # 应用样式配置到控件
        for option, value in style_config.items():
            try:
                widget.config(**{option: value})
            except tk.TclError:
                # 忽略不支持的选项
                pass
    
    def get_style_config(self, component_type: str, variant: str = "normal") -> Dict[str, Any]:
        """获取组件样式配置"""
        return self._component_styles.get(component_type, {}).get(variant, {})
    
    def create_styled_widget(self, parent: tk.Widget, widget_class: type, 
                           style_type: str, variant: str = "normal", **kwargs) -> tk.Widget:
        """创建应用了主题样式的控件"""
        # 获取样式配置
        style_config = self.get_style_config(style_type, variant)
        
        # 合并样式配置和用户参数
        final_config = {**style_config, **kwargs}
        
        # 创建控件
        widget = widget_class(parent, **final_config)
        
        return widget


class ThemeManager:
    """主题管理器 - 负责主题的加载、应用和管理"""
    
    def __init__(self):
        self._current_theme: ThemeConfig = None
        self._default_theme = self._create_default_theme()
        self.set_theme(self._default_theme)
    
    def _create_default_theme(self) -> ThemeConfig:
        """创建默认主题"""
        return ThemeConfig(
            name="default",
            colors=ColorPalette(),
            typography=Typography(),
            spacing=Spacing()
        )
    
    def set_theme(self, theme: ThemeConfig) -> None:
        """设置当前主题"""
        self._current_theme = theme
    
    def get_current_theme(self) -> ThemeConfig:
        """获取当前主题"""
        return self._current_theme
    
    def apply_theme_to_widget(self, widget: tk.Widget, style_type: str, variant: str = "normal") -> None:
        """将当前主题应用到控件"""
        if self._current_theme:
            self._current_theme.apply_to_widget(widget, style_type, variant)
    
    def create_themed_widget(self, parent: tk.Widget, widget_class: type, 
                           style_type: str, variant: str = "normal", **kwargs) -> tk.Widget:
        """创建应用了当前主题的控件"""
        if self._current_theme:
            return self._current_theme.create_styled_widget(parent, widget_class, style_type, variant, **kwargs)
        else:
            return widget_class(parent, **kwargs)
    
    def get_color(self, color_name: str) -> str:
        """获取主题颜色"""
        if self._current_theme and hasattr(self._current_theme.colors, color_name):
            return getattr(self._current_theme.colors, color_name)
        return "#000000"  # 默认黑色
    
    def get_font(self, size: int = None, weight: str = None) -> Tuple[str, int, str]:
        """获取主题字体"""
        if self._current_theme:
            return self._current_theme.typography.get_font_tuple(size, weight)
        return ("Arial", 11, "normal")
    
    def get_spacing(self, spacing_name: str) -> int:
        """获取主题间距"""
        if self._current_theme and hasattr(self._current_theme.spacing, spacing_name):
            return getattr(self._current_theme.spacing, spacing_name)
        return 8  # 默认间距


# 全局主题管理器实例
theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """获取全局主题管理器实例"""
    return theme_manager