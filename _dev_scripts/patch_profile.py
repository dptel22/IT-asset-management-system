import re

with open('templates/profile.html', 'r') as f:
    content = f.read()

content = content.replace('<form id="profileForm">', '<form id="profileForm" method="POST" action="/profile">')

# Replace inputs with names
content = content.replace(
    '<input type="tel" class="form-control" value="+91 9876543210" disabled id="phoneInput">',
    '<input type="tel" name="phone" class="form-control" value="{{ employee.phone or \'\' }}" disabled id="phoneInput">'
)
content = content.replace(
    '<input type="tel" class="form-control" value="+91 8765432109" disabled id="emergencyInput">',
    '<input type="tel" name="emergency_contact" class="form-control" value="{{ employee.emergency_contact or \'\' }}" disabled id="emergencyInput">'
)
content = content.replace(
    '<input type="text" class="form-control" value="Bengaluru, India" disabled id="addressInput">',
    '<input type="text" name="address" class="form-control" value="{{ employee.address or \'\' }}" disabled id="addressInput">'
)

# And we should update the other non-editable inputs to show actual DB values
content = content.replace(
    '<input type="text" class="form-control" value="Myra Iyer" disabled>',
    '<input type="text" class="form-control" value="{{ employee.name }}" disabled>'
)
content = content.replace(
    '<input type="text" class="form-control" value="EMP-0145" disabled>',
    '<input type="text" class="form-control" value="{{ employee.id | shortid }}" disabled>'
)
content = content.replace(
    '<input type="email" class="form-control" value="myra.iyer0@cognixasset.com" disabled>',
    '<input type="email" class="form-control" value="{{ employee.email }}" disabled>'
)
content = content.replace(
    '<input type="text" class="form-control" value="Engineering" disabled>',
    '<input type="text" class="form-control" value="{{ employee.department }}" disabled>'
)

# Update the "Save Changes" button type
content = content.replace(
    '<button type="button" class="btn btn-primary" onclick="saveProfile()">Save Changes</button>',
    '<button type="submit" class="btn btn-primary">Save Changes</button>'
)

# Add success message handling
success_html = """
              {% if success %}
              <div style="background-color: var(--bg-surface); border-left: 4px solid var(--status-active); padding: 12px; margin-bottom: 24px; color: var(--status-active);">
                Profile updated successfully.
              </div>
              {% endif %}
              <h3 class="card-title"
"""
content = content.replace('<h3 class="card-title"', success_html, 1)

# Replace the Myra Iyer hardcoded profile header
content = content.replace('<h3>Myra Iyer</h3>', '<h3>{{ employee.name }}</h3>')
content = content.replace('<div class="status-badge status-active" style="display: inline-block;">Active</div>', '<div class="status-badge status-active" style="display: inline-block; text-transform: capitalize;">{{ employee.status }}</div>')

with open('templates/profile.html', 'w') as f:
    f.write(content)
print("templates/profile.html patched")
