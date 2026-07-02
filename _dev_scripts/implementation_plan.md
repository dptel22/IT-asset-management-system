# Implement Add User and Edit Profile Functionality

The user has pointed out that they cannot add new users ("add new user is not working") and cannot edit their profile ("why cant we edit"). This is because these features were only mocked in the offline UI and lack backend routing and database connections.

## Proposed Changes

### Database Schema Updates (`db.js`)
- Modify the `employees` table schema (via `ALTER TABLE`) to add new columns required by the Profile mockup:
  - `emergency_contact TEXT`
  - `address TEXT`

### Add New User (`server.js` and templates)
- Add `GET /employees/new` route to render `templates/add-user.html`.
- Add `POST /employees` route to handle the form submission. This will:
  - Create a new record in `users` (with a default password or random one).
  - Create a new record in `employees` linked to the user.
- Update `templates/employee-directory.html` to make the "Add Employee" button a link `<a href="/employees/new">`.
- Update `templates/add-user.html` so the form has `method="POST" action="/employees"` instead of the mock `onsubmit="event.preventDefault();"`. Ensure the input fields have correct `name` attributes mapping to the backend (e.g., `name="name"`, `name="email"`, `name="department"`, `name="role"`).

### Edit Profile (`server.js` and templates)
- Add `POST /profile` route to handle profile updates. It will update the `phone`, `emergency_contact`, and `address` fields in the `employees` table for the logged-in user.
- Update `templates/profile.html` so the form has `method="POST" action="/profile"` and the inputs have correct `name` attributes (`phone`, `emergency_contact`, `address`). Change the "Save Changes" button to a `type="submit"`.

## Open Questions
- Is there any other editing functionality that was not working? For example, did you also mean editing an asset from the offline mockups, or was it specifically about the Profile editing?
