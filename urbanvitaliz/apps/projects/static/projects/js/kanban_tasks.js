function boardTasksApp(projectId) {
  const options = {
    async fetchData() {
      const response = await fetch(`/api/projects/${projectId}/tasks`);
      return response.json();
    },
    async patchData(data, status, nextData) {
      await fetch(`/api/projects/${projectId}/tasks/${data.id}/`, {
        method: "PATCH",
        cache: "no-cache",
        mode: "same-origin",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": Cookies.get("csrftoken"),
        },
        body: JSON.stringify({ status }),
      });

      if (nextData) {
        await fetch(`/api/projects/${projectId}/tasks/${data.id}/move/`, {
          method: "POST",
          cache: "no-cache",
          mode: "same-origin",
          credentials: "same-origin",
          headers: {
            "X-CSRFToken": Cookies.get("csrftoken"),
          },
          body: new URLSearchParams(`above=${nextData.id}`),
        });
      }
    },
    sortFn(a, b) {
      return a.order - b.order;
    },
    filterFn(d) {
      return true;
    },
    postProcessData(data) {},
  };

  const app = {
    boards: [
      { status: 0, title: "Nouvelles ", color_class: "border-primary" },
      { status: 1, title: "En cours", color_class: "border-secondary" },
      { status: 2, title: "En attente", color_class: "border-warning" },
      { status: 3, title: "Archivées", color_class: "border-error" },
    ],
    currentTaskId: null,
    initModal() {
      const element = document.getElementById("task-preview");
      this.modalHandle = new bootstrap.Modal(element);
      element.addEventListener("shown.bs.modal", () => {
        this.scrollToLastElement();
      });
    },
    onPreviewClick(event, id) {
      this.currentTaskId = id;
      this.modalHandle.show();
    },
    pendingComment: "",
    async onSubmitComment() {
      await fetch(sendCommentUrl(this.currentTask.id), {
        method: "POST",
        cache: "no-cache",
        mode: "same-origin",
        credentials: "same-origin",
        headers: {
          "X-CSRFToken": Cookies.get("csrftoken"),
        },
        body: new URLSearchParams({ comment: this.pendingComment }),
      });
      this.pendingComment = "";
      await this.getData();
    },
    scrollToLastElement() {
      const nodes = this.$root.querySelectorAll(".message");
      this.$nextTick(() => {
        nodes[nodes.length - 1].scrollIntoView();
      });
    },
  };

  return configureBoardApp(app, options);
}

function resourcePreviewUrl(resourceId) {
  return `/ressource/${resourceId}/embed`;
}

function editTaskUrl(taskId) {
  return `/task/${taskId}/update/`;
}

function deleteTaskReminderUrl(taskId) {
  return `/task/${taskId}/remind-delete/`;
}

function sendCommentUrl(taskId) {
  return `/task/${taskId}/followup/`;
}

function formatDate(timestamp) {
  return new Date(timestamp).toLocaleString();
}

function renderMarkdown(content) {
  return marked.parse(content);
}
