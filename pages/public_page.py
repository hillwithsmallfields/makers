from untemplate.throw_out_your_templates_p3 import htmltags as T
import django.urls
import model.configuration
import pages.page_pieces
import pages.event_page
import model.timeline

conf=None

def public_page():
    """Produce the home page people get when not logged in."""
    global conf
    if conf == None:
        conf = model.configuration.get_config()
    current_events = pages.event_page.event_table_section(timeline.present_events().events, True)
    upcoming_events = pages.event_page.event_table_section(timeline.future_events().events, True)
    content = [T.div[
        T.form(action=django.urls.reverse("users:login"))[T.input(type='email address', name='identifier'),
                                               T.input(type='password', name='password')],
        T.p["Welcome to "+conf['organization']['title']+"."],
        pages.page_pieces.announcements_section(),
        T.h2["Current events"],
        (current_events
         if current_events and len(current_events) > 0
         else T.p["No events are listed as current."]),
        T.h2["Upcoming events"],
        (upcoming_events
         if upcoming_events and len(upcoming_events) > 0
         else T.p["No upcoming events are listed."])]]
    content += [ ]
    return content
