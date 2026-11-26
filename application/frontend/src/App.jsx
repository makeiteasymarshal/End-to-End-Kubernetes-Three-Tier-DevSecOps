import React, { useEffect, useState } from "react";
import { createTask, deleteTask, fetchHealth, listTasks, updateTaskStatus } from "./api";

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [health, setHealth] = useState(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("medium");
  const [owner, setOwner] = useState("platform-team");
  const [error, setError] = useState("");

  async function refreshAll() {
    try {
      const [h, t] = await Promise.all([fetchHealth(), listTasks()]);
      setHealth(h);
      setTasks(t);
      setError("");
    } catch (err) {
      setError(err.message || "Unable to reach backend API");
    }
  }

  useEffect(() => {
    refreshAll();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!title.trim()) return;
    try {
      await createTask({ title, description, priority, owner, status: "open" });
      setTitle("");
      setDescription("");
      await refreshAll();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleCycleStatus(task) {
    const nextStatus =
      task.status === "open"
        ? "in_progress"
        : task.status === "in_progress"
        ? "completed"
        : "open";
    await updateTaskStatus(task.id, nextStatus);
    await refreshAll();
  }

  async function handleDelete(id) {
    await deleteTask(id);
    await refreshAll();
  }

  return (
    <main className="container">
      <header className="header">
        <div>
          <h1>CloudOps Three-Tier Task Console</h1>
          <p className="subtitle">React + Nginx → FastAPI → PostgreSQL / Amazon RDS</p>
        </div>
        <div className={`badge ${health?.status === "ready" ? "ok" : "warn"}`}>
          API: {health?.status || "checking"} | DB: {health?.database || "checking"}
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <section className="card">
        <h2>Create Platform Task</h2>
        <form onSubmit={handleSubmit} className="form-grid">
          <input
            type="text"
            placeholder="Task title (e.g., Rotate EKS OIDC thumbprint)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Owner (e.g., devsecops-team)"
            value={owner}
            onChange={(e) => setOwner(e.target.value)}
          />
          <select value={priority} onChange={(e) => setPriority(e.target.value)}>
            <option value="low">Low Priority</option>
            <option value="medium">Medium Priority</option>
            <option value="high">High Priority</option>
            <option value="critical">Critical</option>
          </select>
          <input
            type="text"
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <button type="submit">Add Task</button>
        </form>
      </section>

      <section className="card">
        <h2>Active Tasks ({tasks.length})</h2>
        {tasks.length === 0 ? (
          <p className="empty">No tasks yet. Add one above to verify end-to-end RDS persistence.</p>
        ) : (
          <ul className="task-list">
            {tasks.map((task) => (
              <li key={task.id} className="task-item">
                <div>
                  <strong>{task.title}</strong>
                  <span className={`pill ${task.priority}`}>{task.priority}</span>
                  <span className="pill status">{task.status}</span>
                  <p className="meta">
                    Owner: {task.owner} {task.description ? `— ${task.description}` : ""}
                  </p>
                </div>
                <div className="actions">
                  <button onClick={() => handleCycleStatus(task)}>Advance Status</button>
                  <button className="danger" onClick={() => handleDelete(task.id)}>
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
