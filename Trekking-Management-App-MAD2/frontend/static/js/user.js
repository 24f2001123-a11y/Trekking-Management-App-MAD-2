// User dashboard data
window.user_data = function () {
  return {
    // Control dashboard sections
    show_browse_treks: false,
    show_my_bookings: false,
    show_edit_profile: false,

    // Store available treks
    available_treks: [],

    // Search and filter data
    search_trek_name: "",
    search_location: "",
    search_difficulty: "",
    search_duration: "",

    // Selected trek details
    show_trek_details: false,
    selected_trek: null,

    // Store user's booking history
    my_bookings: [],

    // CSV export details
    export_loading: false,
    export_message: "",

    // Profile form data
    profile_name: "",
    profile_contact: "",
  };
};

// User dashboard methods
window.user_methods = {
  // Show Browse Treks section
  show_browse_treks_page() {
    this.show_browse_treks = true;
    this.show_my_bookings = false;
    this.show_edit_profile = false;

    this.available_treks = [];
    this.message = "";

    fetch("/api/user/treks", {
      method: "GET",
      credentials: "include",
    })
      .then((response) => response.json())

      .then((data) => {
        console.log("Treks received:", data);

        if (Array.isArray(data)) {
          this.available_treks = data;
          console.log("Stored treks:", this.available_treks.length);
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

  // Filter treks
  filter_treks() {
    return this.available_treks.filter((trek) => {
      // Trek name filter
      let name_match = trek.trek_name
        .toLowerCase()
        .includes(this.search_trek_name.toLowerCase().trim());

      // Location filter
      let location_match = trek.location
        .toLowerCase()
        .includes(this.search_location.toLowerCase());

      // Difficulty filter
      let difficulty_match = true;

      if (this.search_difficulty !== "") {
        difficulty_match = trek.difficulty === this.search_difficulty;
      }

      // Duration filter
      let duration_match = true;

      if (this.search_duration !== "") {
        duration_match = trek.duration <= Number(this.search_duration);
      }

      return name_match && location_match && difficulty_match && duration_match;
    });
  },

  // Clear all filters
  clear_trek_filters() {
    this.search_trek_name = "";
    this.search_location = "";
    this.search_difficulty = "";
    this.search_duration = "";
  },

  // Show My Bookings section
  show_my_bookings_page() {
    this.show_browse_treks = false;
    this.show_my_bookings = true;
    this.show_edit_profile = false;
    this.show_trek_details = false;

    this.my_bookings = [];
    this.message = "";

    // Get user's booking history
    fetch("/api/user/bookings", {
      method: "GET",
      credentials: "include",
    })
      .then((response) => response.json())

      .then((data) => {
        if (Array.isArray(data)) {
          this.my_bookings = data;
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

  // Show Edit Profile section
  show_edit_profile_page() {
    this.load_profile();
  },

  // Return to User Dashboard
  back_to_user_dashboard() {
    this.show_browse_treks = false;
    this.show_my_bookings = false;
    this.show_edit_profile = false;

    this.show_trek_details = false;
    this.selected_trek = null;

    this.clear_trek_filters();
  },

  // View trek details
  view_trek_details(trek) {
    this.show_browse_treks = false;
    this.show_trek_details = true;

    this.selected_trek = trek;

    this.message = "";
  },

  // Return to available treks
  back_to_available_treks() {
    this.show_trek_details = false;
    this.selected_trek = null;

    this.show_browse_treks = true;
  },

  // Book the selected trek
  book_trek() {
    if (!this.selected_trek) {
      return;
    }

    if (!confirm("Are you sure you want to book this trek?")) {
      return;
    }

    fetch("/api/user/bookings", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      credentials: "include",

      body: JSON.stringify({
        trek_id: this.selected_trek.id,
      }),
    })
      .then((response) => response.json())

      .then((data) => {
        this.message = data.message;

        if (data.message === "Trek booked successfully") {
          this.message_type = "success";

          // Update available slots on the details page
          this.selected_trek.available_slots = data.available_slots;
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

  // Cancel a booking
  cancel_booking(booking_id) {
    if (!confirm("Are you sure you want to cancel this booking?")) {
      return;
    }

    fetch("/api/user/bookings/" + booking_id + "/cancel", {
      method: "PUT",

      credentials: "include",
    })
      .then((response) => response.json())

      .then((data) => {
        this.message = data.message;

        if (data.message === "Booking cancelled successfully") {
          this.message_type = "success";

          // Refresh booking history
          this.show_my_bookings_page();
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

  // Load profile details
  load_profile() {
    this.show_browse_treks = false;
    this.show_my_bookings = false;
    this.show_edit_profile = true;
    this.show_trek_details = false;

    this.profile_name = this.user.name;
    this.profile_contact = this.user.contact || "";

    this.message = "";
  },

  // Start booking history CSV export
  export_booking_history() {
    this.export_loading = true;
    this.export_message = "Preparing your CSV file...";

    fetch("/api/user/bookings/export", {
      method: "POST",
      credentials: "include",
    })
      .then((response) => response.json())

      .then((data) => {
        if (!data.task_id) {
          this.export_loading = false;
          this.export_message = data.message || "Could not start CSV export";
          return;
        }

        // Check export task status
        this.check_booking_export(data.task_id);
      })

      .catch((error) => {
        this.export_loading = false;
        this.export_message = "Could not connect to the server";
        console.log(error);
      });
  },

  // Check CSV export status and download the file
  check_booking_export(task_id) {
    fetch("/api/user/bookings/export/" + task_id, {
      method: "GET",
      credentials: "include",
    })
      .then(async (response) => {
        if (response.status === 202) {
          // Task is still running
          setTimeout(() => {
            this.check_booking_export(task_id);
          }, 2000);

          return;
        }

        if (!response.ok) {
          const data = await response.json();

          this.export_loading = false;
          this.export_message = data.message || "CSV export failed";
          return;
        }

        // Download the CSV file
        const csv_file = await response.blob();

        const download_url = URL.createObjectURL(csv_file);

        const link = document.createElement("a");

        link.href = download_url;
        link.download = "booking_history.csv";

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        URL.revokeObjectURL(download_url);

        this.export_loading = false;
        this.export_message = "Booking history exported successfully!";
      })

      .catch((error) => {
        this.export_loading = false;
        this.export_message = "Could not download CSV file";
        console.log(error);
      });
  },

  // Update user profile
  update_profile() {
    fetch("/api/user/profile", {
      method: "PUT",

      headers: {
        "Content-Type": "application/json",
      },

      credentials: "include",

      body: JSON.stringify({
        name: this.profile_name,
        contact: this.profile_contact,
      }),
    })
      .then((response) => response.json())

      .then((data) => {
        this.message = data.message;

        if (data.message === "Profile updated successfully") {
          this.message_type = "success";

          // Update logged-in user details
          this.user.name = data.user.name;
          this.user.contact = data.user.contact;
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
};
