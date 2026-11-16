
window.staff_data = function () {
  return {
    // My Assigned Treks
    show_assigned_treks: false,
    assigned_treks: [],

    // Manage Treks page
    show_manage_treks: false,

    // Manage trek form
    show_manage_trek: false,
    selected_trek: null,
    manage_available_slots: "",
    manage_trek_status: "",

    // Participants page
    show_participant_treks: false,
    show_participants: false,
    participants: [],
    selected_trek_name: "",
  };
};

window.staff_methods = {

  // Load assigned treks from the backend
  load_assigned_treks() {
    fetch("/api/staff/treks", {
      method: "GET",
      credentials: "include",
    })
      .then((response) => response.json())
      .then((data) => {
        if (Array.isArray(data)) {
          this.assigned_treks = data;
        } else {
          this.message = data.message;
          this.message_type = "error";
        }
      })
      .catch((error) => {
        this.message = "Could not connect to the server";
        this.message_type = "error";
        console.log(error);
      });
  },

  // Open My Assigned Treks
  view_assigned_treks() {
    this.show_assigned_treks = true;
    this.show_manage_treks = false;
    this.show_manage_trek = false;
    this.show_participant_treks = false;
    this.show_participants = false;

    this.message = "";
    this.load_assigned_treks();
  },

  // Open Manage Treks page
  open_manage_treks_page() {
    this.show_assigned_treks = false;
    this.show_manage_treks = true;
    this.show_manage_trek = false;
    this.show_participant_treks = false;
    this.show_participants = false;

    this.message = "";
    this.load_assigned_treks();
  },

  // Open Participants page
  open_participants_page() {
    this.show_assigned_treks = false;
    this.show_manage_treks = false;
    this.show_manage_trek = false;
    this.show_participant_treks = true;
    this.show_participants = false;

    this.message = "";
    this.load_assigned_treks();
  },

  // Open trek management form
  show_manage_trek_form(trek) {
    this.show_assigned_treks = false;
    this.show_manage_treks = false;
    this.show_manage_trek = true;
    this.show_participant_treks = false;
    this.show_participants = false;

    this.selected_trek = trek;
    this.manage_available_slots = trek.available_slots;
    this.manage_trek_status = trek.status;

    this.message = "";
  },

  // Save trek changes
  save_trek_changes() {
    fetch("/api/staff/treks/" + this.selected_trek.id, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        available_slots: this.manage_available_slots,
        status: this.manage_trek_status,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message === "Trek updated successfully") {
          this.message = data.message;
          this.message_type = "success";

          this.selected_trek = null;
          this.show_manage_trek = false;

          // Return to Manage Treks page
          this.open_manage_treks_page();
        } else {
          this.message = data.message;
          this.message_type = "error";
        }
      })
      .catch((error) => {
        this.message = "Could not connect to the server";
        this.message_type = "error";
        console.log(error);
      });
  },

  // Cancel trek editing
  cancel_manage_trek() {
    this.show_manage_trek = false;
    this.selected_trek = null;
    this.open_manage_treks_page();
  },

  // View participants of a trek
  view_participants(trek) {
    this.show_assigned_treks = false;
    this.show_manage_treks = false;
    this.show_manage_trek = false;
    this.show_participant_treks = false;
    this.show_participants = true;

    this.selected_trek_name = trek.trek_name;
    this.participants = [];

    this.message = "";

    fetch("/api/staff/treks/" + trek.id + "/participants", {
      method: "GET",
      credentials: "include",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.participants) {
          this.participants = data.participants;
        } else {
          this.message = data.message;
          this.message_type = "error";
        }
      })
      .catch((error) => {
        this.message = "Could not connect to the server";
        this.message_type = "error";
        console.log(error);
      });
  },

  // Return to the list of treks on Participants page
  back_to_participant_treks() {
    this.show_participants = false;
    this.show_participant_treks = true;
    this.participants = [];
  },

  // Mark a trek as completed
  complete_trek(trek) {
    if (!confirm("Are you sure you want to mark this trek as completed?")) {
      return;
    }

    fetch("/api/staff/treks/" + trek.id + "/complete", {
      method: "PUT",
      credentials: "include",
    })
      .then((response) => response.json())
      .then((data) => {
        this.message = data.message;

        if (data.message === "Trek marked as completed successfully") {
          this.message_type = "success";
          this.view_assigned_treks();
        } else {
          this.message_type = "error";
        }
      })
      .catch((error) => {
        this.message = "Could not connect to the server";
        this.message_type = "error";
        console.log(error);
      });
  },

  // Return to Staff Dashboard
  back_to_staff_dashboard() {
    this.show_assigned_treks = false;
    this.show_manage_treks = false;
    this.show_manage_trek = false;
    this.show_participant_treks = false;
    this.show_participants = false;

    this.selected_trek = null;
    this.selected_trek_name = "";
    this.participants = [];
    this.message = "";
  },
};
