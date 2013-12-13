
def output(message, messagetype='debug', details=None, source=None, returning=True, printing=True, exit=None):
    
    messagetypes = {
                'success':  {'exit': False, 'color': 'green' },
                'error':    {'exit': True,  'color': 'red'   },
                'warning':  {'exit': False, 'color': 'yellow'},
                'notice':   {'exit': False, 'color': 'yellow'},
                'info':     {'exit': False, 'color': 'yellow'},
                'debug':    {'exit': False, 'color': 'yellow'},
            }

    trigger_exit = None
    if messagetype.lower() in messagetypes:
        string = '[%s] [%s] %s' % (source, color(messagetype, messagetypes[messagetype.lower()]['color']), message)
        if 'exit' in messagetypes[messagetype.lower()]:
            trigger_exit = messagetypes[messagetype.lower()]['exit']
    else:
        string = '[%s] [%s] %s' % (messagetype, source, message)

    if exit is not None:
        trigger_exit = exit

    if details is not None:
        from pprint import pformat
        string += '\n\t' + pformat(details).replace('\n','\n\t\t')

    if printing:
        print string

    if trigger_exit:
        from sys import exit
        exit(1)

    if returning:
        return string

def color(string, color=None, bgcolor=None, style=None):

    # supported (bg-)colors: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
    # supported styles: DIM, NORMAL, BRIGHT, RESET_ALL

    from colorama import Fore, Back, Style

    format_str = ''
    format_reset = '%s%s%s' % (Fore.RESET, Back.RESET, Style.RESET_ALL)

    if color is not None and hasattr(Fore, color.upper()):
        format_str += getattr(Fore, color.upper())

    if bgcolor is not None and hasattr(Back, bgcolor.upper()):
        format_str += getattr(Back, bgcolor.upper())

    if style is not None and hasattr(Style, style.upper()):
        format_str += getattr(Style, style.upper())

    return '%s%s%s' % (format_str, string, format_reset)

def rect_from_picture(image, position=None):
    import pygame
    image_obj = pygame.image.load("data/"+str(image))
    rect = image_obj.get_rect() 
    if not position == None:
        rect[0], rect[1] = (position[0], position[1],)
    
    return rect

#def do_rects_overlap(rect1, rect2):
#   import pygame
#   from pygame.locals import *
#   for a, b in [(rect1, rect2), (rect2, rect1)]:
#       if ((isPointInsideRect(a.left,  a.top,    b)) or
#           (isPointInsideRect(a.left,  a.bottom, b)) or
#           (isPointInsideRect(a.right, a.top,    b)) or
#           (isPointInsideRect(a.right, a.bottom, b))):
#           return True
#   return False

