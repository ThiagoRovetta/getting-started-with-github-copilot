document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  let messageTimeout;

  function showMessage(text, type = "info") {
    clearTimeout(messageTimeout);
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.classList.remove("hidden");

    messageTimeout = setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participantsHtml = details.participants
          .map(
            (participant) => `
              <li>
                <span class="participant-name">${participant}</span>
                <button
                  type="button"
                  class="participant-remove"
                  data-activity="${name}"
                  data-email="${participant}"
                  aria-label="Remove ${participant}"
                >✕</button>
              </li>
            `
          )
          .join("");

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <p><strong>Participants:</strong></p>
            <ul class="participants-list">
              ${participantsHtml}
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);

        activityCard.querySelectorAll(".participant-remove").forEach((button) => {
          button.addEventListener("click", async () => {
            const activity = button.dataset.activity;
            const email = button.dataset.email;
            button.disabled = true;

            try {
              const response = await fetch(
                `/activities/${encodeURIComponent(activity)}/participants/${encodeURIComponent(email)}`,
                {
                  method: "DELETE",
                }
              );

              const result = await response.json();

              if (response.ok) {
                showMessage(result.message, "success");
                await fetchActivities();
              } else {
                showMessage(result.detail || "Failed to remove participant", "error");
                button.disabled = false;
              }
            } catch (error) {
              showMessage("Failed to remove participant. Please try again.", "error");
              button.disabled = false;
              console.error("Error removing participant:", error);
            }
          });
        });
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        await fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  fetchActivities();
});
