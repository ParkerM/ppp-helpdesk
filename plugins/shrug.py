"<@tompepper> its like we're slack"

from util import hook, http

@hook.command(autohelp=False)
def shrug(inp):
    ".shrug <text>"

    return (u'\u203e\\_(\u30c4)_/\u203e %s' % unicode(inp)).strip()

