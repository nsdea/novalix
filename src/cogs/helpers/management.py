try:
    from . import config
except ImportError:
    import config
    
import socket
import discord

def testing_mode():
    # check if the host is just a developement system
    return socket.gethostname() in ['uwuntu', 'RTX3090', 'nexus']

def color(style='primary'):
    return discord.Color(config.load()[f'color-{style}'])