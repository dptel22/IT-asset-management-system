import os
import re

def replace_tbody(file_path, jinja_code):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace contents of tbody
    new_content = re.sub(r"(<tbody>).*?(</tbody>)", r"\1\n" + jinja_code + r"\n\2", content, flags=re.DOTALL)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated {file_path}")

base = os.path.join(os.path.dirname(__file__), "templates") + os.sep

replace_tbody(base + "transfers.html", """
              {% for t in transfers %}
              <tr>
                <td>{{ t.asset_tag }}<br><small style="color:var(--text-tertiary)">{{ t.brand }} {{ t.model }}</small></td>
                <td>{{ t.from_employee or 'Unassigned' }}</td>
                <td>{{ t.to_employee }}</td>
                <td>{{ t.request_date.split('T')[0] }}</td>
                <td><span class="status-badge status-{{ 'active' if t.status == 'completed' else 'warning' if t.status == 'pending' else 'critical' }}">{{ t.status | title }}</span></td>
                <td><button class="btn btn-icon"><i data-lucide="more-vertical"></i></button></td>
              </tr>
              {% else %}
              <tr><td colspan="6" style="text-align: center;">No transfers found</td></tr>
              {% endfor %}
""")

replace_tbody(base + "maintenance.html", """
              {% for m in maintenance %}
              <tr>
                <td>{{ m.asset_tag }}<br><small style="color:var(--text-tertiary)">{{ m.brand }} {{ m.model }}</small></td>
                <td>{{ m.issue_description }}</td>
                <td>{{ m.reported_by_name }}</td>
                <td>{{ m.reported_date.split('T')[0] }}</td>
                <td><span class="status-badge status-{{ 'active' if m.status == 'completed' else 'warning' if m.status == 'in_progress' else 'critical' }}">{{ m.status.replace('_', ' ') | title }}</span></td>
                <td><button class="btn btn-icon"><i data-lucide="more-vertical"></i></button></td>
              </tr>
              {% else %}
              <tr><td colspan="6" style="text-align: center;">No maintenance records found</td></tr>
              {% endfor %}
""")

replace_tbody(base + "requests.html", """
              {% for r in requests %}
              <tr>
                <td>REQ-{{ r.id[:6].upper() }}</td>
                <td>{{ r.employee_name }}<br><small style="color:var(--text-tertiary)">{{ r.department }}</small></td>
                <td>{{ r.category }}</td>
                <td>{{ r.requested_date.split('T')[0] }}</td>
                <td><span class="status-badge status-{{ 'active' if r.status == 'approved' else 'warning' if r.status == 'pending' else 'critical' }}">{{ r.status | title }}</span></td>
                <td><button class="btn btn-icon"><i data-lucide="more-vertical"></i></button></td>
              </tr>
              {% else %}
              <tr><td colspan="6" style="text-align: center;">No requests found</td></tr>
              {% endfor %}
""")
