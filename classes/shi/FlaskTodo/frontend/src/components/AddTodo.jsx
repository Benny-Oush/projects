import { useState } from 'react'

// Controlled input. Ignores empty/whitespace titles and clears itself only
// after onAdd resolves successfully (App re-throws on failure).
export default function AddTodo({ onAdd }) {
  const [title, setTitle] = useState('')
  const [priority, setPriority] = useState(1)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    const trimmed = title.trim()
    if (!trimmed) return // ignore empty / whitespace-only titles

    setSubmitting(true)
    try {
      await onAdd(trimmed, priority)
      setTitle('') // clear only on success
      setPriority(1)
    } catch {
      // App already surfaced the error; keep the text so the user can retry.
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="add-todo" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="What needs doing?"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        aria-label="New todo title"
      />
      {/* תפריט בחירת עדיפות */}
      <select
        value={priority}
        onChange={(e) => setPriority(Number(e.target.value))}
        className='priority-select'
        aria-label='Priority'
      >
        <option value={1}>Low</option>
        <option value={2}>Medium</option>
        <option value={3}>High</option>
      </select>
      <button type="submit" disabled={submitting || !title.trim()}>
        Add
      </button>
    </form>
  )
}
