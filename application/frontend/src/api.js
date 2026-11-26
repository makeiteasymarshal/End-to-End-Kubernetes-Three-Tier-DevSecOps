const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export async function fetchHealth() {
  const res = await fetch("/health/ready");
  return res.json();
}

export async function listTasks() {
  const res = await fetch(`${API_BASE}/tasks`);
  if (!res.ok) throw new Error("Failed to load tasks");
  return res.json();
}

export async function createTask(payload) {
  const res = await fetch(`${API_BASE}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Failed to create task");
  return res.json();
}

export async function updateTaskStatus(id, status) {
  const res = await fetch(`${API_BASE}/tasks/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status })
  });
  if (!res.ok) throw new Error("Failed to update task");
  return res.json();
}

export async function deleteTask(id) {
  const res = await fetch(`${API_BASE}/tasks/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete task");
}
