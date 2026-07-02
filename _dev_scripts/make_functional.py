import re

path = '/Users/rithanyamagesh/Downloads/employee-dashboard.html'
with open(path, 'r') as f:
    content = f.read()

# Replace links with javascript modal triggers for New Request
content = re.sub(r'<a href="requests\.html"[^>]*class="btn btn-primary"[^>]*>([\s\S]*?)</a>', r'<button class="btn btn-primary" onclick="openModal(\'requestModal\')">\1</button>', content)
content = re.sub(r'<a href="requests\.html"[^>]*class="card"[^>]*>([\s\S]*?)</a>', r'<div class="card" style="cursor:pointer;" onclick="openModal(\'requestModal\')">\1</div>', content)

# Replace links for Report Issue
content = re.sub(r'<a href="add-issue\.html"[^>]*class="card"[^>]*>([\s\S]*?)</a>', r'<div class="card" style="cursor:pointer;" onclick="openModal(\'issueModal\')">\1</div>', content)

# Modals HTML and Javascript to append before </body>
modals_html = """
  <!-- Modals -->
  <div id="modalOverlay" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); backdrop-filter:blur(4px); z-index:1000; align-items:center; justify-content:center;">
    
    <!-- New Request Modal -->
    <div id="requestModal" class="card" style="display:none; width:450px; background:var(--bg-surface); border-radius:var(--radius-modal); border:1px solid var(--border-glow); box-shadow:0 10px 30px rgba(0,0,0,0.5); flex-direction:column; gap:16px;">
      <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border); padding-bottom:12px; margin-bottom:12px;">
        <h3 style="margin:0;">New Asset Request</h3>
        <button class="btn btn-outline" style="padding:4px 8px; border:none;" onclick="closeModals()"><i data-lucide="x"></i></button>
      </div>
      <div>
        <label style="display:block; margin-bottom:6px; font-size:13px; color:var(--text-secondary);">Asset Type</label>
        <select id="reqType" style="width:100%; padding:10px; background:var(--bg-void); border:1px solid var(--border); color:var(--text-primary); border-radius:var(--radius-input); margin-bottom:16px;">
          <option>Laptop</option>
          <option>Monitor</option>
          <option>Accessories</option>
        </select>
        <label style="display:block; margin-bottom:6px; font-size:13px; color:var(--text-secondary);">Reason for Request</label>
        <textarea id="reqReason" rows="3" style="width:100%; padding:10px; background:var(--bg-void); border:1px solid var(--border); color:var(--text-primary); border-radius:var(--radius-input); margin-bottom:16px; resize:none;"></textarea>
        <button class="btn btn-primary" style="width:100%;" onclick="submitRequest()">Submit Request</button>
      </div>
    </div>

    <!-- Report Issue Modal -->
    <div id="issueModal" class="card" style="display:none; width:450px; background:var(--bg-surface); border-radius:var(--radius-modal); border:1px solid var(--border-glow); box-shadow:0 10px 30px rgba(0,0,0,0.5); flex-direction:column; gap:16px;">
      <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border); padding-bottom:12px; margin-bottom:12px;">
        <h3 style="margin:0;">Report Issue</h3>
        <button class="btn btn-outline" style="padding:4px 8px; border:none;" onclick="closeModals()"><i data-lucide="x"></i></button>
      </div>
      <div>
        <label style="display:block; margin-bottom:6px; font-size:13px; color:var(--text-secondary);">Select Asset</label>
        <select id="issueAsset" style="width:100%; padding:10px; background:var(--bg-void); border:1px solid var(--border); color:var(--text-primary); border-radius:var(--radius-input); margin-bottom:16px;">
          <option>MacBook Pro 14" (#LP-0421)</option>
          <option>Logitech MX Master 3 (#PH-0088)</option>
        </select>
        <label style="display:block; margin-bottom:6px; font-size:13px; color:var(--text-secondary);">Issue Description</label>
        <textarea id="issueDesc" rows="3" style="width:100%; padding:10px; background:var(--bg-void); border:1px solid var(--border); color:var(--text-primary); border-radius:var(--radius-input); margin-bottom:16px; resize:none;"></textarea>
        <button class="btn btn-primary" style="width:100%; background:var(--status-warn); color:#000;" onclick="submitIssue()">Submit Issue</button>
      </div>
    </div>

  </div>

  <script>
    function openModal(id) {
      document.getElementById('modalOverlay').style.display = 'flex';
      document.getElementById('requestModal').style.display = 'none';
      document.getElementById('issueModal').style.display = 'none';
      document.getElementById(id).style.display = 'flex';
    }
    function closeModals() {
      document.getElementById('modalOverlay').style.display = 'none';
    }
    
    function updateKPI(index, increment) {
      const kpis = document.querySelectorAll('.kpi-value');
      if (kpis.length > index) {
        let val = parseInt(kpis[index].innerText) || 0;
        kpis[index].innerText = val + increment;
      }
    }

    function addActivityItem(text, meta, icon, colorClass, borderClass) {
      const feed = document.querySelector('.activity-feed');
      if (!feed) return;
      const html = `
        <div class="feed-item fade-up">
          <div class="feed-icon" style="color: ${colorClass}; border-color: ${borderClass};">
            <i data-lucide="${icon}" width="16" height="16"></i>
          </div>
          <div>
            <div class="feed-text">${text}</div>
            <div class="feed-meta">${meta}</div>
          </div>
        </div>
      `;
      feed.insertAdjacentHTML('afterbegin', html);
      lucide.createIcons();
    }

    function submitRequest() {
      const type = document.getElementById('reqType').value;
      addActivityItem(
        `${type} request submitted`, 
        `Request #RQ-${Math.floor(Math.random()*1000)} · Just now`,
        'clock',
        'var(--status-warn)',
        'rgba(245,158,11,0.3)'
      );
      updateKPI(1, 1); // Increment pending requests KPI
      closeModals();
      document.getElementById('reqReason').value = '';
    }

    function submitIssue() {
      const asset = document.getElementById('issueAsset').value;
      addActivityItem(
        `Issue reported for ${asset.split(' ')[0]}`, 
        `Ticket #TK-${Math.floor(Math.random()*1000)} · Just now`,
        'alert-triangle',
        'var(--status-critical)',
        'rgba(239,68,68,0.3)'
      );
      closeModals();
      document.getElementById('issueDesc').value = '';
    }
  </script>
</body>
"""

content = re.sub(r'</body>', modals_html, content)

with open(path, 'w') as f:
    f.write(content)
