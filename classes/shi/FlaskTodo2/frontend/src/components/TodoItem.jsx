// A single row: checkbox (toggle) + title + delete button. Purely driven by
// props; it calls back up to App to mutate the shared state.
import { useState } from 'react'

// A single row: checkbox (toggle) + title + priority + change button + delete button.
export default function TodoItem({ todo, onUpdate, onDelete }) {
  const [isEditingPriority, setIsEditingPriority] = useState(false)

  // המרת מספר העדיפות לטקסט תצוגה
  const priorityLabels = { 1: 'Low', 2: 'Medium', 3: 'High' }
  const currentPriorityLabel = priorityLabels[todo.priority] || 'Low'

  return (
    <li className={`todo-item ${todo.complete ? 'is-complete' : ''}`}>
      <label className="todo-main">
        <input
          type="checkbox"
          checked={todo.complete}
          onChange={() => onUpdate(todo.id, { complete: !todo.complete })}
        />
        <span className="todo-title">{todo.title}</span>
      </label>

      {/* אזור העדיפות: הצגת הטקסט או ה-Select בהתאם למצב העריכה */}
      <div className="priority-container">
        {isEditingPriority ? (
          <select
            value={todo.priority || 1}
            onChange={(e) => {
              onUpdate(todo.id, { priority: Number(e.target.value) })
              setIsEditingPriority(false) // סגירת התפריט לאחר הבחירה
            }}
            onBlur={() => setIsEditingPriority(false)} // סגירה בלחיצה מחוץ לתפריט
            autoFocus
            className="priority-select inline"
            aria-label="Update priority"
          >
            <option value={1}>Low</option>
            <option value={2}>Medium</option>
            <option value={3}>High</option>
          </select>
        ) : (
          <span className="priority-display">
            <span className={`priority-badge p${todo.priority || 1}`}>
              {currentPriorityLabel}
            </span>
            <button
              type="button"
              className="change-priority-btn"
              onClick={() => setIsEditingPriority(true)}
            >
              Change
            </button>
          </span>
        )}
      </div>

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