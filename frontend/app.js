const tasksUrl = "/api/tasks";
const initialTasks = [
  { id: 1, title: "Explore the API documentation", completed: false },
  { id: 2, title: "Query tasks from the frontend", completed: false },
  { id: 3, title: "Practice Docker Compose", completed: false },
];
let tasksStatusElement;

function renderTasks(tasks) {
  const tasksList = document.querySelector("#tasks-list");
  if (!tasksList) return;
  tasksList.replaceChildren();
  tasks.forEach((task) => {
    const link = document.createElement("a");
    link.className = `task-link${task.completed ? " completed" : ""}`;
    link.href = tasksUrl;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = `${task.completed ? "✓" : "○"} ${task.title}`;
    tasksList.append(link);
  });
}

async function loadTasks() {
  const tasksStatus = document.querySelector("#tasks-status");
  const refreshButton = document.querySelector("#refresh-tasks");
  tasksStatus.textContent = "Loading tasks from the backend…";
  refreshButton.disabled = true;
  try {
    const response = await fetch(tasksUrl, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const tasks = await response.json();
    renderTasks(tasks);
    tasksStatus.textContent = `${tasks.length} task(s) received from FastAPI.`;
  } catch (error) {
    tasksStatus.textContent = "Tasks could not be loaded. Check /api/tasks in Network.";
    console.error("Backend request failed:", error);
  } finally {
    refreshButton.disabled = false;
  }
}

async function createTask(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const titleInput = document.querySelector("#task-title");
  const submitButton = form.querySelector("button");
  const title = titleInput.value.trim();
  if (!title) return;

  submitButton.disabled = true;
  tasksStatusElement.textContent = "Saving the task…";
  try {
    const response = await fetch(tasksUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ title }),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    titleInput.value = "";
    await loadTasks();
  } catch (error) {
    tasksStatusElement.textContent = "The task could not be saved. Check /api/tasks in Network.";
    console.error("Task creation failed:", error);
  } finally {
    submitButton.disabled = false;
  }
}

function startFrontend() {
  const tasksStatus = document.querySelector("#tasks-status");
  const refreshButton = document.querySelector("#refresh-tasks");
  const createTaskForm = document.querySelector("#create-task-form");
  tasksStatusElement = tasksStatus;
  renderTasks(initialTasks);
  tasksStatus.textContent = "Initial tasks. Updating from the backend…";
  refreshButton.addEventListener("click", loadTasks);
  createTaskForm.addEventListener("submit", createTask);
  loadTasks();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", startFrontend);
} else {
  startFrontend();
}
