import re

with open('templates/add-user.html', 'r') as f:
    content = f.read()

# Replace form tag
content = re.sub(
    r'<form id="addUserForm" onsubmit="event\.preventDefault\(\);[^"]+">',
    r'<form id="addUserForm" method="POST" action="/employees">',
    content
)

# Replace inputs to add name attributes
content = content.replace('<input type="text" class="form-control" required placeholder="Enter full name">',
                          '<input type="text" name="name" class="form-control" required placeholder="Enter full name">')

content = content.replace('<input type="email" class="form-control" required placeholder="name@company.com">',
                          '<input type="email" name="email" class="form-control" required placeholder="name@company.com">')

# Add name="department" to select
content = content.replace('<select class="form-control" required>', '<select name="department" class="form-control" required>', 1)

# Add name="role" to select
content = content.replace('<select class="form-control" required>', '<select name="role" class="form-control" required>', 1)

# Third select is manager
content = content.replace('<select class="form-control" required>', '<select name="manager" class="form-control" required>', 1)

# Add an error message display at the top of the form
error_html = """
              {% if error %}
              <div style="background-color: var(--bg-surface); border-left: 4px solid var(--status-critical); padding: 12px; margin-bottom: 24px; color: var(--status-critical);">
                {{ error }}
              </div>
              {% endif %}
              <div class="form-grid">
"""
content = content.replace('<div class="form-grid">', error_html, 1)

# I also need a location input for user. I will add a hidden input for location just in case, or default it in backend.
# Actually I'll patch server.js to default location if missing, or add it to add-user.html.
# In add-user.html there is no location field! Let's default location in server.js.

with open('templates/add-user.html', 'w') as f:
    f.write(content)
print("templates/add-user.html patched")
