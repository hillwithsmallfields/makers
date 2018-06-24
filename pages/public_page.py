from nevow import tags as T
import configuration

conf=None

def public_page():
    """Produce the home page people get when not logged in."""
    global conf
    if conf == None:
        conf = configuration.get_config()
    content = [T.div[T.p["Welcome to "+conf['organization']['title']+"."]]]
    # todo: add timeline of public events
    return content
