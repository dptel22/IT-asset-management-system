with open("ui/ux/employee-dashboard.html") as f:
    text = f.read()

start_idx = text.find('<main class="main-content">')
end_idx = text.find('</main>', start_idx)
print("start_idx:", start_idx)
print("end_idx:", end_idx)
print("text length:", len(text))
