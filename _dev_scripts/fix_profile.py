import re

with open('templates/dashboard.html', 'r') as f:
    dashboard_html = f.read()

with open('templates/profile.html', 'r') as f:
    broken_profile_html = f.read()

profile_content = broken_profile_html.split('</html>')[1]
content_match = re.search(r'(<div class="page-header">.*?</script>)', profile_content, re.DOTALL)
actual_profile_content = content_match.group(1)

start_idx = dashboard_html.find('<div class="content-area">')
end_idx = dashboard_html.find('</main>', start_idx)

if start_idx != -1 and end_idx != -1:
    # We want to replace everything from after <div class="content-area"> to right before the </div> that closes content-area.
    # Since we can just replace everything up to </main> minus the closing </div> (assuming it's just `    </div>\n    </main>`)
    
    # Let's extract prefix
    prefix = dashboard_html[:start_idx + len('<div class="content-area">')]
    # Let's extract suffix starting from </main> but prepending a </div> to close content-area
    suffix = '\n      </div>\n    ' + dashboard_html[end_idx:]
    
    new_html = prefix + '\n' + actual_profile_content + suffix
    with open('templates/profile.html', 'w') as out_f:
        out_f.write(new_html)
    print("Successfully fixed templates/profile.html")
else:
    print("Failed")
