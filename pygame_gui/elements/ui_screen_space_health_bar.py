from typing import Union, Dict

import pygame

from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import UIElement
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape


class UIScreenSpaceHealthBar(UIElement):
    """
    A UI that will display health capacity and current health for a sprite in 'screen space'.
    That means it won't move with the camera. This is a good choice for a user/player sprite.

    :param relative_rect: The rectangle that defines the size and position of the health bar.
    :param manager: The UIManager that manages this element.
    :param sprite_to_monitor: The sprite we are displaying the health of.
    :param container: The container that this element is within. If set to None will be the root
                      window's container.
    :param parent_element: The element this element 'belongs to' in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's relative_rect is relative to.

    """
    def __init__(self,
                 relative_rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 sprite_to_monitor: Union[pygame.sprite.Sprite, None] = None,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[str, None] = None,
                 anchors: Dict[str, str] = None):

        element_ids, object_ids = self._create_valid_ids(container=container,
                                                         parent_element=parent_element,
                                                         object_id=object_id,
                                                         element_id='screen_space_health_bar')

        super().__init__(relative_rect, manager, container,
                         starting_height=1,
                         layer_thickness=1,
                         element_ids=element_ids,
                         object_ids=object_ids,
                         anchors=anchors)

        self.current_health = 50
        self.health_capacity = 100
        self.health_percentage = self.current_health / self.health_capacity

        self.font = None
        self.border_width = None
        self.shadow_width = None
        self.border_colour = None
        self.bar_unfilled_colour = None
        self.bar_filled_colour = None
        self.text_shadow_colour = None
        self.text_colour = None
        self.text_horiz_alignment = 'center'
        self.text_vert_alignment = 'center'
        self.text_horiz_alignment_padding = 1
        self.text_vert_alignment_padding = 1

        self.border_rect = None
        self.capacity_width = None
        self.capacity_height = None
        self.capacity_rect = None
        self.current_health_rect = None

        self.drawable_shape = None
        self.shape_type = 'rectangle'
        self.shape_corner_radius = None

        if sprite_to_monitor is not None:
            if not hasattr(sprite_to_monitor, 'health_capacity'):
                raise AttributeError('Sprite does not have health_capacity attribute')
            if not hasattr(sprite_to_monitor, 'current_health'):
                raise AttributeError('Sprite does not have current_health attribute')
            self.sprite_to_monitor = sprite_to_monitor
        else:
            self.sprite_to_monitor = None
        self.set_image(None)
        self.background_text = None
        self.foreground_text = None

        self.rebuild_from_changed_theme_data()

    def set_sprite_to_monitor(self, sprite_to_monitor: pygame.sprite.Sprite):
        """
        Sprite to monitor the health of. Must have 'health_capacity' and 'current_health'
        attributes.

        :param sprite_to_monitor:

        """
        if not hasattr(sprite_to_monitor, 'health_capacity'):
            raise AttributeError('Sprite does not have health_capacity attribute')
        if not hasattr(sprite_to_monitor, 'current_health'):
            raise AttributeError('Sprite does not have current_health attribute')
        self.sprite_to_monitor = sprite_to_monitor

    def rebuild(self):
        """
        Rebuild the health bar entirely because the theming data has changed.

        """
        border_rect_width = self.rect.width - (self.shadow_width * 2)
        border_rect_height = self.rect.height - (self.shadow_width * 2)
        self.border_rect = pygame.Rect((self.shadow_width,
                                        self.shadow_width),
                                       (border_rect_width, border_rect_height))

        self.capacity_width = self.rect.width - (self.shadow_width * 2) - self.border_width * 2
        self.capacity_height = self.rect.height - (self.shadow_width * 2) - self.border_width * 2
        self.capacity_rect = pygame.Rect((self.shadow_width + self.border_width,
                                          self.shadow_width + self.border_width),
                                         (self.capacity_width, self.capacity_height))

        self.current_health_rect = pygame.Rect((self.shadow_width + self.border_width,
                                                self.shadow_width + self.border_width),
                                               (int(self.capacity_width * self.health_percentage),
                                                self.capacity_height))

        self.redraw()

    def redraw(self):
        """
        Redraws the health bar rectangles and text onto the underlying sprite's image surface.
        Takes a little while so we only do it when the health has changed.
        """
        health_display_string = str(self.current_health) + "/" + str(self.health_capacity)

        theming_parameters = {'normal_bg': self.bar_unfilled_colour,
                              'normal_border': self.border_colour,
                              'border_width': self.border_width,
                              'shadow_width': self.shadow_width,
                              'shape_corner_radius': self.shape_corner_radius,
                              'filled_bar': self.bar_filled_colour,
                              'filled_bar_width_percentage': self.health_percentage,
                              'font': self.font,
                              'text': health_display_string,
                              'normal_text': self.text_colour,
                              'text_shadow': self.text_shadow_colour,
                              'text_horiz_alignment': self.text_horiz_alignment,
                              'text_vert_alignment': self.text_vert_alignment,
                              'text_horiz_alignment_padding': self.text_horiz_alignment_padding,
                              'text_vert_alignment_padding': self.text_vert_alignment_padding,
                              }

        if self.shape_type == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ['normal'], self.ui_manager)
        elif self.shape_type == 'rounded_rectangle':
            self.drawable_shape = RoundedRectangleShape(self.rect, theming_parameters,
                                                        ['normal'], self.ui_manager)

        self.set_image(self.drawable_shape.get_surface('normal'))

    def update(self, time_delta: float):
        """
        Updates the health bar sprite's image with the latest health data from the
        sprite we are monitoring. Only triggers a rebuild if the health values have changed.

        :param time_delta: time passed in seconds between one call to this method and the next.

        """
        super().update(time_delta)
        if (self.alive() and self.sprite_to_monitor is not None and
                (self.sprite_to_monitor.health_capacity != self.health_capacity or
                 self.current_health != self.sprite_to_monitor.current_health)):
            self.current_health = self.sprite_to_monitor.current_health
            self.health_capacity = self.sprite_to_monitor.health_capacity
            self.health_percentage = self.current_health / self.health_capacity

            rect_width = int(self.capacity_width * self.health_percentage)
            self.current_health_rect = pygame.Rect((self.shadow_width + self.border_width,
                                                    self.shadow_width + self.border_width),
                                                   (rect_width,
                                                    self.capacity_height))
            self.redraw()

    def rebuild_from_changed_theme_data(self):
        """
        Called by the UIManager to check the theming data and rebuild whatever needs rebuilding
        for this element when the theme data has changed.
        """
        has_any_changed = False

        font = self.ui_theme.get_font(self.object_ids, self.element_ids)
        if font != self.font:
            self.font = font
            has_any_changed = True

        shape_type = 'rectangle'
        shape_type_string = self.ui_theme.get_misc_data(self.object_ids,
                                                        self.element_ids,
                                                        'shape')
        if shape_type_string is not None and shape_type_string in ['rectangle',
                                                                   'rounded_rectangle']:
            shape_type = shape_type_string
        if shape_type != self.shape_type:
            self.shape_type = shape_type
            has_any_changed = True

        if self._check_shape_theming_changed(defaults={'border_width': 1,
                                                       'shadow_width': 2,
                                                       'shape_corner_radius': 2}):
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                             self.element_ids,
                                                             'normal_border')
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        bar_unfilled_colour = self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                   self.element_ids,
                                                                   'unfilled_bar')
        if bar_unfilled_colour != self.bar_unfilled_colour:
            self.bar_unfilled_colour = bar_unfilled_colour
            has_any_changed = True

        bar_filled_colour = self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                 self.element_ids,
                                                                 'filled_bar')
        if bar_filled_colour != self.bar_filled_colour:
            self.bar_filled_colour = bar_filled_colour
            has_any_changed = True

        text_shadow_colour = self.ui_theme.get_colour(self.object_ids,
                                                      self.element_ids,
                                                      'text_shadow')
        if text_shadow_colour != self.text_shadow_colour:
            self.text_shadow_colour = text_shadow_colour
            has_any_changed = True

        text_colour = self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                           self.element_ids,
                                                           'normal_text')
        if text_colour != self.text_colour:
            self.text_colour = text_colour
            has_any_changed = True

        if has_any_changed:
            self.rebuild()
