import os

form_css = """
    /* Form Styles */
    .form-group {
      margin-bottom: 20px;
    }
    .form-group label {
      display: block;
      margin-bottom: 8px;
      color: var(--text-secondary);
      font-weight: 500;
      font-size: 14px;
    }
    .form-group label .required {
      color: var(--status-critical);
      margin-left: 4px;
    }
    .form-control {
      width: 100%;
      padding: 12px 16px;
      background: rgba(13, 18, 32, 0.6);
      border: 1px solid var(--border);
      border-radius: var(--radius-input);
      color: var(--text-primary);
      font-family: var(--font-ui);
      font-size: 14px;
      transition: all 0.2s ease;
      appearance: none;
    }
    .form-control:focus {
      outline: none;
      border-color: var(--accent-ice);
      box-shadow: 0 0 0 3px rgba(168, 200, 255, 0.1);
    }
    textarea.form-control {
      resize: vertical;
      min-height: 100px;
    }
    select.form-control {
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%237B8DB5' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 16px center;
      padding-right: 40px;
    }
    .form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
    }
    .form-actions {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      margin-top: 32px;
      padding-top: 24px;
      border-top: 1px solid var(--border);
    }
"""

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        
    if "/* Form Styles */" in content:
        print(f"{filepath} already patched.")
        return

    # Inject CSS before the last </style>
    style_end = content.rfind('</style>')
    if style_end != -1:
        content = content[:style_end] + form_css + content[style_end:]
        
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Patched {filepath}")

patch_file('employee-dashboard.html')
patch_file('dashboard.html')
