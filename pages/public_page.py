from untemplate.throw_out_your_templates_p3 import htmltags as T
import django.urls
import model.configuration
import pages.page_pieces
import pages.event_page
import model.timeline

conf=None

def public_page(django_request):
    """Produce the home page people get when not logged in."""
    global conf
    if conf == None:
        conf = model.configuration.get_config()
    current_events = model.timeline.Timeline.present_events().events()
    current_events_text = (pages.event_page.event_table_section(
        current_events,
        None,
        django_request)
                           if len(current_events) > 0
                           else None)
    upcoming_events = model.timeline.Timeline.future_events().events()
    upcoming_events_text = (pages.event_page.event_table_section(
        upcoming_events,
        None,
        django_request,
        with_signup=True)
                            if len(upcoming_events) > 0
                            else None)
    content = [T.div[
        # T.form(action=django.urls.reverse("users:login"))[T.input(type='text', name='identifier'),
        #                                        T.input(type='password', name='password')],
        T.p["Welcome to "+conf['organization']['title']+"."],
        T.h2["Announcements"],
        pages.page_pieces.announcements_section(),
        T.h2["Current events"],
        current_events_text or T.p["No events are listed as current."],
        T.h2["Upcoming events"],
        (upcoming_events_text or T.p["No upcoming events are listed."])]]
    # content += [ ]
    return content
