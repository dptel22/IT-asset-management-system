import os

toast_css = """
    /* Toast Notifications */
    .toast-container {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .toast {
      min-width: 280px;
      padding: 16px 20px;
      background: rgba(6, 10, 20, 0.95);
      border: 1px solid var(--border);
      border-radius: var(--radius-card);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
      color: var(--text-primary);
      font-family: var(--font-ui);
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 12px;
      transform: translateX(120%);
      opacity: 0;
      transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
      backdrop-filter: blur(8px);
    }
    .toast.show {
      transform: translateX(0);
      opacity: 1;
    }
    .toast.success { border-left: 4px solid var(--status-active); }
    .toast.error { border-left: 4px solid var(--status-critical); }
    .toast.warning { border-left: 4px solid var(--status-warn); }
    .toast.info { border-left: 4px solid var(--accent-ice); }
"""

toast_js = """
    function showToast(message, type = 'info') {
      let container = document.getElementById('toast-container');
      if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
      }
      
      const toast = document.createElement('div');
      toast.className = `toast ${type}`;
      
      let iconName = 'info';
      if(type === 'success') iconName = 'check-circle';
      if(type === 'error') iconName = 'alert-triangle';
      if(type === 'warning') iconName = 'alert-circle';
      
      toast.innerHTML = `<i data-lucide="${iconName}" style="color: var(--status-${type === 'success' ? 'active' : type === 'error' ? 'critical' : type === 'warning' ? 'warn' : 'info'})"></i> <span>${message}</span>`;
      
      container.appendChild(toast);
      lucide.createIcons();
      
      // Trigger reflow to apply animation
      void toast.offsetWidth;
      toast.classList.add('show');
      
      setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
      }, 4000);
    }
"""

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        
    if "function showToast" in content:
        print(f"{filepath} already patched.")
        return

    # Inject CSS before the last </style>
    style_end = content.rfind('</style>')
    if style_end != -1:
        content = content[:style_end] + toast_css + content[style_end:]
        
    # Inject JS inside the existing script block at the end
    script_block = content.rfind('<script>')
    if script_block != -1:
        content = content[:script_block+8] + toast_js + content[script_block+8:]
        
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Patched {filepath}")

patch_file('employee-dashboard.html')
patch_file('dashboard.html')
patch_file('index.html')
