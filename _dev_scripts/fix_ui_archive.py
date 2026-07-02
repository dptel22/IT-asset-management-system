with open('templates/archive.html', 'r') as f:
    content = f.read()

dummy_rows = """
              <tr>
                <td>
                  <div class="td-id">AST-0912</div>
                  <div class="td-name">HP EliteBook 840</div>
                </td>
                <td class="td-meta">5CG1234567</td>
                <td><span class="badge badge-neutral">Laptop</span></td>
                <td>Admin User</td>
                <td class="td-meta">Dec 15, 2025</td>
                <td class="td-meta">Hardware failure</td>
              </tr>
              <tr>
                <td>
                  <div class="td-id">AST-0955</div>
                  <div class="td-name">Dell UltraSharp 27"</div>
                </td>
                <td class="td-meta">CN-0123-4567</td>
                <td><span class="badge badge-neutral">Monitor</span></td>
                <td>Jane Doe</td>
                <td class="td-meta">Jan 02, 2026</td>
                <td class="td-meta">Replaced with newer model</td>
              </tr>
              <tr>
                <td>
                  <div class="td-id">AST-0988</div>
                  <div class="td-name">Apple iPad Pro</div>
                </td>
                <td class="td-meta">DLX1234567</td>
                <td><span class="badge badge-neutral">Tablet</span></td>
                <td>Admin User</td>
                <td class="td-meta">Feb 10, 2026</td>
                <td class="td-meta">Screen cracked, out of warranty</td>
              </tr>
"""

import re
# Replace the nunjucks loop with dummy rows
content = re.sub(r'\{% for a in archived_assets %\}.*?\{% endfor %\}', dummy_rows, content, flags=re.DOTALL)

with open('ui/ux/archive.html', 'w') as f:
    f.write(content)

print("Fixed ui/ux/archive.html")
