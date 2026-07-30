import TodoItem from './TodoItem.jsx'

// Presentational list. Renders an empty state when there are no todos.
export default function TodoList({ todos, onToggle, onPriorityChange, onDelete }) {
  if (todos.length === 0) {
    return (
      <p className="muted empty">Nothing here yet. Add your first todo above.</p>
    )
  }

  const sortedTodos = [...todos].sort((a, b) => {
    const aPriority = typeof a.priority === 'number' ? a.priority : 0
    const bPriority = typeof b.priority === 'number' ? b.priority : 0
    if (aPriority === bPriority) return a.id - b.id
    return bPriority - aPriority
  })

  return (
    <ul className="todo-list">
      {sortedTodos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onPriorityChange={onPriorityChange}
          onDelete={onDelete}
        />
      ))}
    </ul>
  )
}
