from vk_api.keyboard import VkKeyboard, VkKeyboardColor

keyboard_ontime = VkKeyboard(one_time=False)
keyboard_ontime.add_button('найти', color=VkKeyboardColor.SECONDARY)
keyboard_ontime.add_line()
keyboard_ontime.add_button('в избранное', color=VkKeyboardColor.POSITIVE)
keyboard_ontime.add_line()
keyboard_ontime.add_button('в избранном', color=VkKeyboardColor.POSITIVE)
