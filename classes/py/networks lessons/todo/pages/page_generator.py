

def task_form(edit_id=None):
    txt = 'Edit' if edit_id is not None else 'Add'
    cancel = '<a href="/">Cancel</a>'
    return f"""
    <form method="POST" action="/">
        <input type="text" name="task" placeholder="{txt} a task">
        <input type="hidden" name="edit_id" value="{edit_id if edit_id is not None else '0'}">
        <button type="submit">{txt}</button>
        {cancel if edit_id is None else ''}
    </form>
    """

def task_row(details):
    (id, task, status, created_at) = details
    return f"""
        <tr>
            <td>{task}</td>
            <td>{status}</td>
            <td>{created_at}</td>
            <td>
                <a href="/complete?id={id}">Complete</a>
                <a href="/edit?id={id}">Edit</a>
                <a href="/delete?id={id}">Delete</a>
            </td>
        </tr>
    """

def task_rows(tasks):
    return '\n'.join([task_row(t) for t in tasks])

def create_page(tasks, edit_id=None):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Tasks</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>My Tasks</h1>
    {task_form(edit_id)}
    <table>
        <tr>
            <th>Task</th>
            <th>Status</th>
            <th>Created At</th>
            <th>Actions</th>
        </tr>
        {task_rows(tasks)}
    </table>
</body>
</html>
    """