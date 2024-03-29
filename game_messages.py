import tcod as libtcod
import textwrap

from components.graphics import colors

class Message:
    def __init__(self, text, color=colors.get('dark')):
        self.text = text
        self.color = color


class MessageLog:
    def __init__(self, x, width, height):
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def add_message(self, message):
        # Split the message if necessary, among multiple lines
        message.text = "> " + message.text
        new_msg_lines = textwrap.wrap(message.text, self.width)
        #new_msg_lines.append("")

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room for the new one
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line as a Message object, with the text and the color
            self.messages.append(Message(line, message.color))