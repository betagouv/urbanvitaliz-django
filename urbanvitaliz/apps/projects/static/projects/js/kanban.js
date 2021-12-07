function kanban_app() {
		return {
				dateDisplay: 'toLocaleDateString',
				boards: [
					  // {code: 'DRAFT', title: 'Brouillon', color_class: 'red'},
            {code: 'TO_PROCESS', title: 'A traiter', color_class: 'border-secondary'},
            {code: 'QUESTIONS', title: 'En attente', color_class: 'border-warning'},
            {code: 'READY', title: 'Prêt à aiguiller', color_class: 'border-success'},
            {code: "IN_PROGRESS", title: "Recommandations en cours", color_class: 'border-success'},
            // {code: "REVIEW_REQUEST", title: "Demande de relecture", color_class: 'border-success'},
            {code: "DONE", title: "Aiguillage terminé", color_class: 'border-success'},
            // {code: "STUCK", title: "En Attente/Bloqué", color_class: 'border-error'},

				],

				tasks: [],

        truncate(input, size=30) {
            return input.length > size ? `${input.substring(0, size)}...` : input
        },

				formatDateDisplay(date) {
					  if (this.dateDisplay === 'toDateString') return new Date(date).toDateString();
					  if (this.dateDisplay === 'toLocaleDateString') return new Date(date).toLocaleDateString('fr-FR');

					  return new Date().toLocaleDateString('fr-FR');
				},

        async moveTask(uuid, boardCode) {
            let taskIndex = this.tasks.findIndex(t => t.uuid === uuid);
            task = this.tasks[taskIndex];

            const response = await fetch(`/api/projects/${task.id}/`,
                                         {method: 'PATCH',
                                          cache: 'no-cache',
                                          mode: 'same-origin',
                                          credentials: 'same-origin',
                                          headers: {
                                              'Content-Type': 'application/json',
                                              'X-CSRFToken': Cookies.get('csrftoken')
                                          },
                                          body: JSON.stringify({status: boardCode})
                                         });

            tasksFromApi = await response.json(); //extract JSON from the http response

        },


				async getTasks() {
            var tasksFromApi = [];

            const response = await fetch('/api/projects/');
            tasksFromApi = await response.json(); //extract JSON from the http response

						this.tasks = tasksFromApi.map(t => {
							  return {
                    uuid: this.generateUUID(),
								    id: t.id,
								    name: this.truncate(t.name),
								    status: t.status,
								    boardCode: t.status,
								    date: t.created_on,
                    organization: t.org_name
							  }
						});
				},

				onDragStart(event, uuid) {
					  event.dataTransfer.setData('text/plain', uuid);
					  event.target.classList.add('bg-warning');
				},

				onDragOver(event) {
					  event.preventDefault();
					  return false;
				},

				onDragEnter(event) {
					  event.target.classList.add('bg-info');
				},

				onDragLeave(event) {
					  event.target.classList.remove('bg-info');
				},

				async onDrop(event, boardCode) {
					  event.stopPropagation(); // Stops some browsers from redirecting.
					  event.preventDefault();
					  event.target.classList.remove('bg-info');

					  // console.log('Dropped', this);
					  const id = event.dataTransfer.getData('text');

					  const draggableElement = document.getElementById(id);
					  const dropzone = event.target;

					  dropzone.appendChild(draggableElement);

					  // Update
					  await this.moveTask(id, boardCode);

					  // Get Updated Tasks
					  await this.getTasks();

					  event.dataTransfer.clearData();
				},

				generateUUID() {
					  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
						    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
						    return v.toString(16);
					  });
				},

				dispatchCustomEvents(eventName, message) {
					  let customEvent = new CustomEvent(eventName, { detail: { message: message } });
					  window.dispatchEvent(customEvent);
				},
		}
};