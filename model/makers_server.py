# Stuff for talking to the rest of the server --- very prone to change when we get real

def mailer(address, text):
    """Send a message to an address."""
    with open("/tmp/mailings", 'w+') as outfile:
        outfile.write("\nTo: " + address + "\n\n" + text)

def generate_page(template, person, event):
    """Generate a web page from a template."""
    pass
