import pygame
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.core.ui_window import UIWindow


class UIMessageWindow(UIWindow):
    def __init__(self, message_window_rect, message_title, html_message, ui_manager,
                 element_ids=None, object_id=None):
        if element_ids is None:
            new_element_ids = ['message_window']
        else:
            new_element_ids = element_ids.copy()
            new_element_ids.append('message_window')
        super().__init__(message_window_rect, ui_manager, new_element_ids, object_id)

        self.bg_colour = self.ui_manager.get_theme().get_colour(self.object_id, self.element_ids, 'dark_bg')

        # create shadow
        shadow_padding = (2, 2)
        background_surface = pygame.Surface((self.rect.width - shadow_padding[0]*2,
                                             self.rect.height - shadow_padding[1]*2))
        background_surface.fill(self.bg_colour)
        self.image = self.ui_manager.get_shadow(self.rect.size)
        self.image.blit(background_surface, shadow_padding)

        self.get_container().relative_rect.width = self.rect.width - shadow_padding[0] * 2
        self.get_container().relative_rect.height = self.rect.height - shadow_padding[1] * 2
        self.get_container().relative_rect.x = self.get_container().relative_rect.x + shadow_padding[0]
        self.get_container().relative_rect.y = self.get_container().relative_rect.y + shadow_padding[1]
        self.get_container().update_containing_rect_position()

        self.menu_bar = UIButton(relative_rect=pygame.Rect((0, 0),
                                                           ((self.rect.width - shadow_padding[0] * 2) - 20, 20)),
                                 text=message_title,
                                 ui_manager=ui_manager,
                                 ui_container=self.get_container(),
                                 object_id='#message_window_title_bar',
                                 element_ids=self.element_ids
                                 )
        self.menu_bar.set_hold_range((100, 100))

        self.grabbed_window = False
        self.starting_grab_difference = (0, 0)

        self.close_window_button = UIButton(relative_rect=pygame.Rect(((self.rect.width - shadow_padding[0] * 2) - 20,
                                                                       0),
                                                                      (20, 20)),
                                            text='╳',
                                            ui_manager=ui_manager,
                                            ui_container=self.get_container(),
                                            element_ids=self.element_ids
                                            )

        self.done_button = UIButton(relative_rect=pygame.Rect(((self.rect[2] / 2) + 45,
                                                               self.rect[3] - 30), (70, 20)),
                                    text="Dismiss",
                                    ui_manager=ui_manager,
                                    ui_container=self.get_container(),
                                    tool_tip_text="<font face=fira_code color=normal_text size=2>"
                                                  "Click to get rid of this message.</font>",
                                    element_ids=self.element_ids
                                    )

        text_block_rect = pygame.Rect((0, 20),
                                      (self.rect.width - shadow_padding[0] * 2,
                                       self.rect.height - 50))
        self.text_block = UITextBox(html_message, text_block_rect, ui_manager=ui_manager,
                                    ui_container=self.get_container(),
                                    element_ids=self.element_ids)

    def update(self, time_delta):
        if self.alive():

            if self.done_button.check_pressed_and_reset():
                self.kill()

            if self.menu_bar.held:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if not self.grabbed_window:
                    self.window_stack.move_window_to_front(self)
                    self.grabbed_window = True
                    self.starting_grab_difference = (mouse_x - self.rect.x,
                                                     mouse_y - self.rect.y)

                current_grab_difference = (mouse_x - self.rect.x,
                                           mouse_y - self.rect.y)

                adjustment_required = (current_grab_difference[0] - self.starting_grab_difference[0],
                                       current_grab_difference[1] - self.starting_grab_difference[1])

                self.rect.x += adjustment_required[0]
                self.rect.y += adjustment_required[1]
                self.get_container().relative_rect.x += adjustment_required[0]
                self.get_container().relative_rect.y += adjustment_required[1]
                self.get_container().update_containing_rect_position()

            else:
                self.grabbed_window = False

            if self.close_window_button.check_pressed_and_reset():
                self.kill()

        super().update(time_delta)
