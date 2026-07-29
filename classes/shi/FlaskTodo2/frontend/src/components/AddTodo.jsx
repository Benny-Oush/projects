import { useState } from 'react'

// Controlled input. Ignores empty/whitespace titles and clears itself only
// after onAdd resolves successfully (App re-throws on failure).
export default function AddTodo({ onAdd }) {
  const [title, setTitle] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    const trimmed = title.trim()
    if (!trimmed) return // ignore empty / whitespace-only titles

    setSubmitting(true)
    try {
      await onAdd(trimmed)
      setTitle('') // clear only on success
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
      <button type="submit" disabled={submitting || !title.trim()}>
        Add
      </button>
    </form>
  )
}
