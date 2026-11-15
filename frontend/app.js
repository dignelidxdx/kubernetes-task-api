const tasksUrl = "/api/tasks";
const initialTasks = [
  { id: 1, title: "Explorar la documentación de la API", completed: false },
  { id: 2, title: "Consultar tareas desde el frontend", completed: false },
  { id: 3, title: "Practicar Docker Compose", completed: false },
];

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
  tasksStatus.textContent = "Consultando tareas desde el backend…";
  refreshButton.disabled = true;
  try {
    const response = await fetch(tasksUrl, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const tasks = await response.json();
    renderTasks(tasks);
    tasksStatus.textContent = `${tasks.length} tarea(s) recibida(s) desde FastAPI.`;
  } catch (error) {
    tasksStatus.textContent = "No se pudieron cargar las tareas. Revisá /api/tasks en Network.";
    console.error("Error consultando el backend:", error);
  } finally {
    refreshButton.disabled = false;
  }
}

function startFrontend() {
  const tasksStatus = document.querySelector("#tasks-status");
  const refreshButton = document.querySelector("#refresh-tasks");
  renderTasks(initialTasks);
  tasksStatus.textContent = "Tareas iniciales. Actualizando desde el backend…";
  refreshButton.addEventListener("click", loadTasks);
  loadTasks();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", startFrontend);
} else {
  startFrontend();
}
