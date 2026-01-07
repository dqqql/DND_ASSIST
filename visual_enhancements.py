"""
视觉元素优化模块
在适当位置添加微妙的视觉增强，确保所有视觉元素与整体主题保持一致，
维护视觉平衡，避免界面过载
"""

import tkinter as tk
from typing import Dict, Any, Optional, Tuple, List
from theme_system import get_theme_manager


class VisualEnhancer:
    """视觉增强器 - 负责添加微妙的视觉改进"""
    
    def __init__(self):
        self.theme_manager = get_theme_manager()
        self.enhanced_widgets = set()
        self._enhancement_cache = {}
    
    def apply_visual_enhancements(self, app_instance) -> None:
        """为应用程序应用视觉增强"""
        # 添加微妙的阴影效果
        self._add_subtle_shadows(app_instance)
        
        # 增强边框和分隔线
        self._enhance_borders_and_separators(app_instance)
        
        # 添加视觉层次指示器
        self._add_visual_hierarchy_indicators(app_instance)
        
        # 优化图标和符号显示
        self._enhance_icons_and_symbols(app_instance)
        
        # 添加微妙的渐变效果
        self._add_subtle_gradients(app_instance)
        
        # 增强状态指示器
        self._enhance_status_indicators(app_instance)
        
        # 优化内容区域的视觉分离
        self._enhance_content_separation(app_instance)
    
    def _add_subtle_shadows(self, app_instance) -> None:
        """添加微妙的阴影效果"""
        theme = self.theme_manager.get_current_theme()
        
        # 为主要容器添加微妙的深度感
        containers_to_enhance = []
        
        # 内容查看器容器
        if hasattr(app_instance, 'content_text') and hasattr(app_instance, 'text_frame'):
            containers_to_enhance.append(('content_viewer', app_instance.text_frame))
        
        # 文件列表容器
        if hasattr(app_instance, 'file_list'):
            file_list_parent = app_instance.file_list.master
            if file_list_parent:
                containers_to_enhance.append(('file_list', file_list_parent))
        
        # 跑团列表容器
        if hasattr(app_instance, 'campaign_list'):
            campaign_list_parent = app_instance.campaign_list.master
            if campaign_list_parent:
                containers_to_enhance.append(('campaign_list', campaign_list_parent))
        
        # 为容器添加微妙的阴影效果
        for container_type, container in containers_to_enhance:
            self._apply_container_shadow(container, container_type)
    
    def _apply_container_shadow(self, container: tk.Widget, container_type: str) -> None:
        """为容器应用微妙的阴影效果"""
        theme = self.theme_manager.get_current_theme()
        
        try:
            if container_type == 'content_viewer':
                container.configure(
                    relief=tk.RAISED,
                    bd=2,
                    bg=theme.colors.secondary_bg,
                    highlightthickness=1,
                    highlightcolor=theme.colors.border_color,
                    highlightbackground=theme.colors.border_color
                )
            elif container_type in ['file_list', 'campaign_list']:
                container.configure(
                    relief=tk.SUNKEN,
                    bd=1,
                    bg=theme.colors.primary_bg,
                    highlightthickness=1,
                    highlightcolor=theme.colors.border_color,
                    highlightbackground=theme.colors.border_color
                )
        except tk.TclError:
            pass
    
    def _enhance_borders_and_separators(self, app_instance) -> None:
        """增强边框和分隔线"""
        theme = self.theme_manager.get_current_theme()
        
        if hasattr(app_instance, 'root'):
            app_instance.root.configure(bg=theme.colors.primary_bg)
        
        if hasattr(app_instance, 'file_frame'):
            try:
                app_instance.file_frame.configure(
                    relief=tk.FLAT,
                    bd=0,
                    bg=theme.colors.primary_bg
                )
            except tk.TclError:
                pass
        
        if hasattr(app_instance, 'category_frame'):
            try:
                app_instance.category_frame.configure(
                    relief=tk.FLAT,
                    bd=0,
                    bg=theme.colors.primary_bg
                )
            except tk.TclError:
                pass
    
    def _add_visual_hierarchy_indicators(self, app_instance) -> None:
        """添加视觉层次指示器"""
        theme = self.theme_manager.get_current_theme()
        
        title_widgets = []
        
        def find_title_labels(widget):
            try:
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        text = child.cget("text")
                        if text in ["跑团列表", "文件内容"]:
                            title_widgets.append(child)
                    find_title_labels(child)
            except tk.TclError:
                pass
        
        if hasattr(app_instance, 'root'):
            find_title_labels(app_instance.root)
        
        for label in title_widgets:
            try:
                label.configure(
                    font=theme.typography.get_font_tuple(
                        theme.typography.size_large, 
                        theme.typography.weight_bold
                    ),
                    fg=theme.colors.text_primary,
                    bg=theme.colors.primary_bg
                )
            except tk.TclError:
                pass
    
    def _enhance_icons_and_symbols(self, app_instance) -> None:
        """优化图标和符号显示"""
        pass
    
    def _add_subtle_gradients(self, app_instance) -> None:
        """添加微妙的渐变效果"""
        buttons_to_enhance = []
        
        def collect_buttons(widget):
            try:
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        buttons_to_enhance.append(child)
                    collect_buttons(child)
            except tk.TclError:
                pass
        
        if hasattr(app_instance, 'root'):
            collect_buttons(app_instance.root)
        
        for button in buttons_to_enhance:
            try:
                current_relief = button.cget("relief")
                if current_relief == tk.FLAT:
                    button.configure(relief=tk.RAISED, bd=1)
            except tk.TclError:
                pass
    
    def _enhance_status_indicators(self, app_instance) -> None:
        """增强状态指示器"""
        theme = self.theme_manager.get_current_theme()
        
        if hasattr(app_instance, 'category_buttons'):
            for name, button in app_instance.category_buttons.items():
                try:
                    button.configure(
                        relief=tk.RAISED,
                        bd=1,
                        highlightthickness=1,
                        highlightcolor=theme.colors.border_color,
                        highlightbackground=theme.colors.border_color
                    )
                except tk.TclError:
                    pass
        
        action_buttons = []
        if hasattr(app_instance, 'action_button'):
            action_buttons.append(app_instance.action_button)
        if hasattr(app_instance, 'delete_button'):
            action_buttons.append(app_instance.delete_button)
        if hasattr(app_instance, 'back_button'):
            action_buttons.append(app_instance.back_button)
        
        for button in action_buttons:
            try:
                button.configure(
                    relief=tk.RAISED,
                    bd=2,
                    highlightthickness=1,
                    highlightcolor=theme.colors.focus_color,
                    highlightbackground=theme.colors.border_color
                )
            except tk.TclError:
                pass
    
    def _enhance_content_separation(self, app_instance) -> None:
        """优化内容区域的视觉分离"""
        theme = self.theme_manager.get_current_theme()
        
        panels_to_enhance = []
        
        def find_main_panels(widget):
            try:
                for child in widget.winfo_children():
                    if isinstance(child, tk.Frame):
                        pack_info = child.pack_info()
                        if pack_info.get('side') in [tk.LEFT, tk.RIGHT]:
                            panels_to_enhance.append(child)
                    find_main_panels(child)
            except tk.TclError:
                pass
        
        if hasattr(app_instance, 'root'):
            find_main_panels(app_instance.root)
        
        for panel in panels_to_enhance:
            try:
                panel.configure(
                    bg=theme.colors.primary_bg,
                    relief=tk.FLAT,
                    bd=0
                )
            except tk.TclError:
                pass
        
        if hasattr(app_instance, 'content_text'):
            try:
                app_instance.content_text.configure(
                    relief=tk.SUNKEN,
                    bd=2,
                    highlightthickness=1,
                    highlightcolor=theme.colors.border_color,
                    highlightbackground=theme.colors.border_color
                )
            except tk.TclError:
                pass
        
        if hasattr(app_instance, 'image_label'):
            try:
                app_instance.image_label.configure(
                    relief=tk.SUNKEN,
                    bd=2,
                    highlightthickness=1,
                    highlightcolor=theme.colors.border_color,
                    highlightbackground=theme.colors.border_color
                )
            except tk.TclError:
                pass


def apply_visual_enhancements(app_instance) -> VisualEnhancer:
    """为应用程序应用视觉增强"""
    enhancer = VisualEnhancer()
    enhancer.apply_visual_enhancements(app_instance)
    return enhancer


def enhance_visual_consistency(app_instance) -> None:
    """增强视觉一致性"""
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    
    def apply_consistent_theming(widget):
        try:
            widget_class = widget.__class__.__name__
            
            if widget_class == "Frame":
                widget.configure(bg=theme.colors.primary_bg)
            elif widget_class == "Label":
                widget.configure(
                    bg=theme.colors.primary_bg,
                    fg=theme.colors.text_primary
                )
            
            for child in widget.winfo_children():
                apply_consistent_theming(child)
        except tk.TclError:
            pass
    
    if hasattr(app_instance, 'root'):
        apply_consistent_theming(app_instance.root)


def add_subtle_visual_effects(widget: tk.Widget, effect_type: str = "shadow") -> None:
    """为单个控件添加微妙的视觉效果"""
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    
    try:
        if effect_type == "shadow":
            widget.configure(
                relief=tk.RAISED,
                bd=1,
                highlightthickness=1,
                highlightcolor=theme.colors.border_color,
                highlightbackground=theme.colors.border_color
            )
        elif effect_type == "border":
            widget.configure(
                relief=tk.SOLID,
                bd=1,
                highlightthickness=1,
                highlightcolor=theme.colors.border_color,
                highlightbackground=theme.colors.border_color
            )
        elif effect_type == "inset":
            widget.configure(
                relief=tk.SUNKEN,
                bd=2,
                highlightthickness=1,
                highlightcolor=theme.colors.border_color,
                highlightbackground=theme.colors.border_color
            )
    except tk.TclError:
        pass


__all__ = [
    'VisualEnhancer',
    'apply_visual_enhancements',
    'enhance_visual_consistency',
    'add_subtle_visual_effects'
]