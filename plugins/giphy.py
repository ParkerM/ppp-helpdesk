from util import http, hook

@hook.api_key('giphy')
@hook.command('gif', autohelp=False)
@hook.command(autohelp=False)
def giphy(inp, api_key=None):
    ".giphy [term] -- gets random gif for a term"

    data = http.get_json("http://api.giphy.com/v1/gifs/random", { "api_key": api_key, "tag": inp })

    return data['data']['image_url']

