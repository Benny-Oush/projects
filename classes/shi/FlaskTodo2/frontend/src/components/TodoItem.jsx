// A single row: checkbox (toggle) + title + delete button. Purely driven by
// props; it calls back up to App to mutate the shared state.
export default function TodoItem({ todo, onToggle, onPriorityChange, onDelete }) {
  return (
    <li className={`todo-item ${todo.complete ? 'is-complete' : ''}`}>
      <label className="todo-main">
        <input
          type="checkbox"
          checked={todo.complete}
          onChange={() => onToggle(todo.id, !todo.complete)}
        />
        <span className="todo-title">{todo.title}</span>
      </label>

      <label className="todo-priority">
        Priority
        <input
          type="number"
          min="0"
          value={todo.priority ?? 0}
          onChange={(event) =>
            onPriorityChange(todo.id, Number(event.target.value))
          }
          aria-label={`Priority for ${todo.title}`}
        />
      </label>

      <button
        type="button"
        className="delete"
        onClick={() => onDelete(todo.id)}
        aria-label={`Delete ${todo.title}`}
      >
        ×
      </button>
    </li>
  )
}
