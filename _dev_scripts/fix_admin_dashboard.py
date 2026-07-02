import re

def fix():
    # 1. Update server.js
    with open('server.js', 'r') as f:
        server = f.read()

    server_find = """    const recent_requests = await query(`
        SELECT r.id, r.request_type, r.category, r.status, r.requested_date, e.name as employee_name
        FROM requests r JOIN employees e ON r.employee_id = e.id
        WHERE r.status = 'pending'
        ORDER BY r.requested_date DESC LIMIT 5
    `);"""

    server_replace = server_find + """
    const recent_maintenance = await query(`
        SELECT m.id, m.status, m.reported_date, m.issue_description, a.asset_tag, a.brand, a.model
        FROM maintenance m JOIN assets a ON m.asset_id = a.id
        ORDER BY m.reported_date DESC LIMIT 5
    `);"""

    server = server.replace(server_find, server_replace)
    
    # Update the res.render
    server = server.replace(
        "res.render('dashboard.html', { stats, recent_assets, recent_requests, department_stats, category_stats });",
        "res.render('dashboard.html', { stats, recent_assets, recent_requests, recent_maintenance, department_stats, category_stats });"
    )

    with open('server.js', 'w') as f:
        f.write(server)
        
    print("Updated server.js")

    # 2. Update dashboard.html
    with open('templates/dashboard.html', 'r') as f:
        html = f.read()

    # Recent Activity
    act_find = """              <div class="feed-list activity-feed">
                <div class="feed-item">
                  <div class="feed-icon"><i data-lucide="user-check" width="16"></i></div>
                  <div>
                    <div class="feed-text">MacBook Pro <span class="font-data">#LP-0421</span> assigned to Priya Sharma</div>
                    <div class="feed-meta">2 hours ago</div>
                  </div>
                </div>
                <div class="feed-item">
                  <div class="feed-icon"><i data-lucide="wrench" width="16"></i></div>
                  <div>
                    <div class="feed-text">Dell Server <span class="font-data">#SV-0032</span> moved to maintenance</div>
                    <div class="feed-meta">5 hours ago</div>
                  </div>
                </div>
                <div class="feed-item">
                  <div class="feed-icon"><i data-lucide="download" width="16"></i></div>
                  <div>
                    <div class="feed-text">New inventory batch (24 items) added</div>
                    <div class="feed-meta">Yesterday at 14:30</div>
                  </div>
                </div>
                <div class="feed-item">
                  <div class="feed-icon"><i data-lucide="trash-2" width="16"></i></div>
                  <div>
                    <div class="feed-text">Lenovo ThinkPad <span class="font-data">#LP-0401</span> retired</div>
                    <div class="feed-meta">Yesterday at 11:15</div>
                  </div>
                </div>
              </div>"""

    act_repl = """              <div class="feed-list activity-feed">
                {% for a in recent_assets %}
                <div class="feed-item">
                  <div class="feed-icon"><i data-lucide="plus-circle" width="16"></i></div>
                  <div>
                    <div class="feed-text">Asset <span class="font-data">{{ a.asset_tag }}</span> added</div>
                    <div class="feed-meta">{{ a.brand }} {{ a.model }} - {{ a.assigned_to_name or 'Unassigned' }}</div>
                  </div>
                </div>
                {% else %}
                <div class="feed-item"><div class="feed-text">No recent activity</div></div>
                {% endfor %}
              </div>"""
    
    html = html.replace(act_find, act_repl)

    # Pending Transfers (Requests)
    req_find = """              <div class="feed-list">
                <div class="feed-item">
                  <div style="flex:1;">
                    <div class="feed-text"><span class="font-data">#LP-0389</span> HP EliteBook 840</div>
                    <div class="feed-meta" style="display:flex; align-items:center; margin-top:8px;">
                      Priya S. <i data-lucide="arrow-right" width="12" class="transfer-arrow"></i> Rohan M.
                    </div>
                  </div>
                  <span class="badge badge-warn">PENDING</span>
                </div>
                <div class="feed-item">
                  <div style="flex:1;">
                    <div class="feed-text"><span class="font-data">#MT-0118</span> LG UltraWide 34"</div>
                    <div class="feed-meta" style="display:flex; align-items:center; margin-top:8px;">
                      IT Pool <i data-lucide="arrow-right" width="12" class="transfer-arrow"></i> Kavya R.
                    </div>
                  </div>
                  <span class="badge badge-warn">PENDING</span>
                </div>
                <div class="feed-item">
                  <div style="flex:1;">
                    <div class="feed-text"><span class="font-data">#MB-0087</span> iPhone 15 Pro</div>
                    <div class="feed-meta" style="display:flex; align-items:center; margin-top:8px;">
                      Vikram N. <i data-lucide="arrow-right" width="12" class="transfer-arrow"></i> HR Pool
                    </div>
                  </div>
                  <span class="badge badge-warn">PENDING</span>
                </div>
              </div>"""
              
    req_repl = """              <div class="feed-list">
                {% for r in recent_requests %}
                <div class="feed-item">
                  <div style="flex:1;">
                    <div class="feed-text">{{ r.request_type }} - {{ r.category }}</div>
                    <div class="feed-meta" style="display:flex; align-items:center; margin-top:8px;">
                      Requested by {{ r.employee_name }}
                    </div>
                  </div>
                  <span class="badge badge-warn">PENDING</span>
                </div>
                {% else %}
                <div class="feed-item"><div class="feed-text">No pending requests</div></div>
                {% endfor %}
              </div>"""

    html = html.replace(req_find, req_repl)

    # Maintenance Alerts
    maint_find = """              <div class="feed-list">
                <div class="feed-item" style="border-left: 2px solid var(--status-critical);">
                  <div style="flex:1;">
                    <div class="feed-text"><span class="font-data">#SV-0032</span> Dell PowerEdge R750</div>
                    <div class="feed-meta">Thermal warning - Rear Fan 2 Failure</div>
                  </div>
                </div>
                <div class="feed-item" style="border-left: 2px solid var(--status-warn);">
                  <div style="flex:1;">
                    <div class="feed-text"><span class="font-data">#NW-0044</span> Cisco Catalyst 9300</div>
                    <div class="feed-meta">Firmware update required (v14.2)</div>
                  </div>
                </div>
                <div class="feed-item" style="border-left: 2px solid var(--status-warn);">
                  <div style="flex:1;">
                    <div class="feed-text"><span class="font-data">#LP-0422</span> MacBook Pro M3</div>
                    <div class="feed-meta">Battery capacity below 80% threshold</div>
                  </div>
                </div>
              </div>"""

    maint_repl = """              <div class="feed-list">
                {% for m in recent_maintenance %}
                <div class="feed-item" style="border-left: 2px solid {% if m.status == 'Open' %}var(--status-critical){% else %}var(--status-warn){% endif %};">
                  <div style="flex:1;">
                    <div class="feed-text"><span class="font-data">{{ m.asset_tag }}</span> Issue reported</div>
                    <div class="feed-meta">{{ m.issue_description | truncate(40) if m.issue_description else 'No description' }}</div>
                  </div>
                </div>
                {% else %}
                <div class="feed-item"><div class="feed-text">No maintenance alerts</div></div>
                {% endfor %}
              </div>"""

    html = html.replace(maint_find, maint_repl)
    
    html = html.replace('<h3 class="card-title"><i data-lucide="arrow-left-right" width="20" height="20" class="text-secondary"></i> Pending Transfers</h3>', 
                        '<h3 class="card-title"><i data-lucide="clock" width="20" height="20" class="text-secondary"></i> Pending Requests</h3>')

    with open('templates/dashboard.html', 'w') as f:
        f.write(html)
        
    print("Updated dashboard.html")

fix()
