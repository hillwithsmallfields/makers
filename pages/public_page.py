from nevow import tags as T
import configuration
import page_pieces
import timeline

conf=None

def public_page():
    """Produce the home page people get when not logged in."""
    global conf
    if conf == None:
        conf = configuration.get_config()
    current_events = page.pieces.eventlist(timeline.present_events().events)
    upcoming_events = page.pieces.eventlist(timeline.future_events().events)
    content = [T.div[
        T.form(action=conf['server']['login'])[T.input(type='email address', name='identifier'),
                                               T.input(type='password', name='password')],
        T.p["Welcome to "+conf['organization']['title']+"."],
        page_pieces.announcements_section(),
        T.h2["Current events"],
        current_events if current_events and len(current_events) > 0 else T.p["No events are listed as current."],
        T.h2["Upcoming events"],
        upcoming_events if upcoming_events and len(upcoming_events) > 0 else T.p["No upcoming events are listed."]]]
    content += [
    return content
