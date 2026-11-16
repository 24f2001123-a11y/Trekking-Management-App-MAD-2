// Admin dashboard data
window.admin_data = function () {
  return {
    // Dashboard statistics
    dashboard_stats: {
      total_users: 0,
      total_staff: 0,
      total_treks: 0,
      total_bookings: 0,},

    // Create trek form
    show_trek_form: false,

    trek_name: "",
    trek_location: "",
    trek_difficulty: "",
    trek_duration: "",
    trek_slots: "",
    trek_start_date: "",
    trek_end_date: "",

    // Manage treks
    show_treks: false,
    treks: [],

    // Edit trek form
    show_edit_form: false,
    edit_trek_id: "",
    edit_trek_name: "",
    edit_trek_location: "",
    edit_trek_difficulty: "",
    edit_trek_duration: "",
    edit_trek_slots: "",
    edit_trek_start_date: "",
    edit_trek_end_date: "",

    // Manage users
    show_users: false,
    users: [],
    user_search: "",

    // Create staff form
    show_staff_form: false,
    staff_name: "",
    staff_email: "",
    staff_contact: "",
    staff_password: "",
    staff_confirm_password: "",

    // Manage staff
    show_staff: false,
    staff_members: [],
    staff_search: "",

    // Assign staff to trek
    show_assign_form: false,
    assign_trek_id: "",
    assign_trek_name: "",
    selected_staff_id: "",

    // Booking management
    show_bookings: false,
    bookings: [],
    booking_search: "",
  };
};

// Admin dashboard methods
window.admin_methods = {
  // Get Admin dashboard statistics
  fetch_dashboard_stats() {
    fetch("/api/admin/dashboard", {
      credentials: "include",
    })
      .then((response) => response.json())

      .then((data) => {
        if (data.total_users !== undefined) {
          this.dashboard_stats.total_users = data.total_users;
          this.dashboard_stats.total_staff = data.total_staff;
          this.dashboard_stats.total_treks = data.total_treks;
          this.dashboard_stats.total_bookings = data.total_bookings;
        } else {
          this.message = data.message;
          this.message_type = "error";
        }
      })

      .catch((error) => {
        this.message = "Could not load dashboard statistics";
        this.message_type = "error";

        console.log(error);
      });
  },

  // Show Create Trek form
  show_create_trek() {
    this.show_trek_form = true;
    this.show_treks = false;
    this.message = "";
  },

  // Create a new trek
  create_trek() {
    fetch("/api/admin/treks", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      credentials: "include",

      body: JSON.stringify({
        trek_name: this.trek_name,
        location: this.trek_location,
        difficulty: this.trek_difficulty,
        duration: this.trek_duration,
        available_slots: this.trek_slots,
        start_date: this.trek_start_date,
        end_date: this.trek_end_date,
      }),
    })
      .then((response) => response.json())

      .then((data) => {
        if (data.message === "Trek created successfully") {
          this.message = data.message;
          this.message_type = "success";

          // Clear form fields
          this.trek_name = "";
          this.trek_location = "";
          this.trek_difficulty = "";
          this.trek_duration = "";
          this.trek_slots = "";
          this.trek_start_date = "";
          this.trek_end_date = "";

          // Hide the form
          this.show_trek_form = false;

          // Update dashboard statistics
          this.fetch_dashboard_stats();
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

  // View all treks
  view_treks() {
    this.show_treks = true;
    this.show_trek_form = false;
    this.show_assign_form = false;

    fetch("/api/admin/treks", {
      credentials: "include",
    })
      .then((response) => response.json())

      .then((data) => {
        if (Array.isArray(data)) {
          this.treks = data;
        } else {
          this.message = data.message || "Could not load treks";
          this.message_type = "error";
        }
      })

      .catch((error) => {
        this.message = "Could not load treks";
        this.message_type = "error";

        console.log(error);
      });
  },

  // Show Edit Trek form
  edit_trek(trek) {
    this.show_treks = false;
    this.show_trek_form = false;
    this.show_edit_form = true;

    this.edit_trek_id = trek.id;
    this.edit_trek_name = trek.trek_name;
    this.edit_trek_location = trek.location;
    this.edit_trek_difficulty = trek.difficulty;
    this.edit_trek_duration = trek.duration;
    this.edit_trek_slots = trek.available_slots;
    this.edit_trek_start_date = trek.start_date;
    this.edit_trek_end_date = trek.end_date;

    this.message = "";
  },

  // Update trek details
  update_trek() {
    fetch("/api/admin/treks/" + this.edit_trek_id, {
      method: "PUT",

      headers: {
        "Content-Type": "application/json",
      },

      credentials: "include",

      body: JSON.stringify({
        trek_name: this.edit_trek_name,
        location: this.edit_trek_location,
        difficulty: this.edit_trek_difficulty,
        duration: this.edit_trek_duration,
        available_slots: this.edit_trek_slots,
        start_date: this.edit_trek_start_date,
        end_date: this.edit_trek_end_date,
      }),
    })
      .then((response) => response.json())

      .then((data) => {
        if (data.message === "Trek updated successfully") {
          this.message = data.message;
          this.message_type = "success";

          this.show_edit_form = false;

          // Refresh the trek list
          this.view_treks();

          // Update dashboard statistics
          this.fetch_dashboard_stats();
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

  // Delete a trek
  delete_trek(trek_id) {
    if (!confirm("Are you sure you want to delete this trek?")) {
      return;
    }

    fetch("/api/admin/treks/" + trek_id, {
      method: "DELETE",

      credentials: "include",
    })
      .then((response) => response.json())

      .then((data) => {
        if (data.message === "Trek deleted successfully") {
          this.message = data.message;
          this.message_type = "success";

          // Refresh the trek list
          this.view_treks();

          // Update dashboard statistics
          this.fetch_dashboard_stats();
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

  // View all users
  view_users() {
    this.show_trek_form = false;
    this.show_treks = false;
    this.show_edit_form = false;
    this.show_users = true;

    this.user_search = "";

    fetch("/api/admin/users", {
      method: "GET",
      credentials: "include",
    })
      .then((response) => response.json())
      .then((data) => {
        this.users = data;
      })
      .catch((error) => {
        this.message = "Could not connect to the server";
        this.message_type = "error";

        console.log(error);
      });
  },

  // Activate or deactivate a user
  change_user_status(user) {
    let new_status = user.status === "Active" ? "Inactive" : "Active";

    fetch("/api/admin/users/" + user.id + "/status", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        status: new_status,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message === "User status updated successfully") {
          this.message = data.message;
          this.message_type = "success";

          this.view_users();
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

  // Blacklist or remove blacklist
  change_user_blacklist(user) {
    let new_status = !user.is_blacklisted;

    fetch("/api/admin/users/" + user.id + "/blacklist", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        is_blacklisted: new_status,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message === "User blacklist status updated successfully") {
          this.message = data.message;
          this.message_type = "success";

          this.view_users();
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

  // Show create staff form
  show_create_staff() {
    this.show_trek_form = false;
    this.show_treks = false;
    this.show_edit_form = false;
    this.show_users = false;
    this.show_staff = false;

    this.show_staff_form = true;

    this.staff_name = "";
    this.staff_email = "";
    this.staff_contact = "";
    this.staff_password = "";
    this.staff_confirm_password = "";

    this.message = "";
  },

  // Create staff account
  create_staff() {
    if (this.staff_password !== this.staff_confirm_password) {
      this.message = "Passwords do not match";
      this.message_type = "error";

      return;
    }

    fetch("/api/admin/staff", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        name: this.staff_name,
        email: this.staff_email,
        contact: this.staff_contact,
        password: this.staff_password,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message === "Staff account created successfully") {
          this.message = data.message;
          this.message_type = "success";

          this.show_staff_form = false;

          this.fetch_dashboard_stats();
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

  // View all staff members
  view_staff() {
    this.show_trek_form = false;
    this.show_treks = false;
    this.show_edit_form = false;
    this.show_users = false;
    this.show_staff_form = false;

    this.show_staff = true;
    this.staff_search = "";

    fetch("/api/admin/staff", {
      method: "GET",
      credentials: "include",
    })
      .then((response) => response.json())
      .then((data) => {
        this.staff_members = data;
      })
      .catch((error) => {
        this.message = "Could not connect to the server";
        this.message_type = "error";

        console.log(error);
      });
  },

  // Activate or deactivate staff
  change_staff_status(staff) {
    let new_status = staff.status === "Active" ? "Inactive" : "Active";

    fetch("/api/admin/staff/" + staff.id + "/status", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        status: new_status,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message === "Staff status updated successfully") {
          this.message = data.message;
          this.message_type = "success";

          this.view_staff();
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

  // Blacklist or remove blacklist
  change_staff_blacklist(staff) {
    let new_status = !staff.is_blacklisted;

    fetch("/api/admin/staff/" + staff.id + "/blacklist", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        is_blacklisted: new_status,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message === "Staff blacklist status updated successfully") {
          this.message = data.message;
          this.message_type = "success";

          this.view_staff();
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

  // Show staff assignment form
  show_assign_staff(trek) {
    this.show_treks = false;
    this.show_trek_form = false;
    this.show_edit_form = false;
    this.show_users = false;
    this.show_staff = false;
    this.show_staff_form = false;

    this.show_assign_form = true;

    this.assign_trek_id = trek.id;
    this.assign_trek_name = trek.trek_name;
    this.selected_staff_id = "";

    this.message = "";

    fetch("/api/admin/staff", {
      method: "GET",
      credentials: "include",
    })
      .then((response) => response.json())
      .then((data) => {
        this.staff_members = data;
      })
      .catch((error) => {
        this.message = "Could not connect to the server";
        this.message_type = "error";

        console.log(error);
      });
  },

  // Assign selected staff to trek
  assign_staff() {
    if (!this.selected_staff_id) {
      this.message = "Please select a staff member";
      this.message_type = "error";

      return;
    }

    fetch("/api/admin/treks/" + this.assign_trek_id + "/assign-staff", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        staff_id: this.selected_staff_id,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message === "Staff assigned successfully") {
          this.message = data.message;
          this.message_type = "success";

          this.show_assign_form = false;

          this.view_treks();
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

  // Remove staff assignment
  remove_staff_assignment(trek_id) {
    if (!confirm("Are you sure you want to remove this staff assignment?")) {
      return;
    }

    fetch("/api/admin/treks/" + trek_id + "/assign-staff", {
      method: "DELETE",
      credentials: "include",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message === "Staff assignment removed successfully") {
          this.message = data.message;
          this.message_type = "success";

          this.view_treks();
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

  // View all bookings
  view_bookings() {
    this.show_trek_form = false;
    this.show_treks = false;
    this.show_edit_form = false;
    this.show_users = false;
    this.show_staff = false;
    this.show_staff_form = false;
    this.show_assign_form = false;
    this.show_bookings = true;

    this.message = "";

    fetch("/api/admin/bookings", {
      method: "GET",
      credentials: "include",
    })
      .then((response) => response.json())
      .then((data) => {
        this.bookings = data;
      })
      .catch((error) => {
        this.message = "Could not connect to the server";
        this.message_type = "error";

        console.log(error);
      });
  },

  // Search bookings
  search_bookings() {
    let search = this.booking_search.toLowerCase();

    return this.bookings.filter((booking) => {
      return (
        booking.user_name.toLowerCase().includes(search) ||
        booking.trek_name.toLowerCase().includes(search) ||
        booking.user_email.toLowerCase().includes(search)
      );
    });
  },

  // Cancel a booking
  cancel_booking(booking_id) {
    if (!confirm("Are you sure you want to cancel this booking?")) {
      return;
    }

    fetch("/api/admin/bookings/" + booking_id + "/cancel", {
      method: "PUT",
      credentials: "include",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message === "Booking cancelled successfully") {
          this.message = data.message;
          this.message_type = "success";

          // Refresh bookings
          this.view_bookings();

          // Refresh dashboard statistics
          this.fetch_dashboard_stats();
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

  // Cancel editing
  cancel_edit() {
    this.show_edit_form = false;
    this.show_treks = true;
    this.message = "";
  },
};
