// Authentication data
window.auth_data = function () {
  return {
    // Login details
    login_email: "",
    login_password: "",

    // Registration details
    register_name: "",
    register_email: "",
    register_contact: "",
    register_password: "",
    confirm_password: "",
  };
};

// Authentication methods
window.auth_methods = {
  // Show registration page
  show_register() {
    this.page = "register";
    this.message = "";
  },

  // Show login page
  show_login() {
    this.page = "login";
    this.message = "";
  },

  // Register a new user
  register() {
    if (this.register_password !== this.confirm_password) {
      this.message = "Passwords do not match";
      this.message_type = "error";
      return;
    }

    fetch("/api/auth/register", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        name: this.register_name,
        email: this.register_email,
        contact: this.register_contact,
        password: this.register_password,
      }),
    })
      .then((response) => response.json())

      .then((data) => {
        if (data.message === "Registration successful") {
          this.message = data.message;
          this.message_type = "success";

          this.login_email = this.register_email;

          // Clear registration fields
          this.register_name = "";
          this.register_email = "";
          this.register_contact = "";
          this.register_password = "";
          this.confirm_password = "";

          this.page = "login";
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

  // Login an existing user
  login() {
    fetch("/api/auth/login", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      credentials: "include",

      body: JSON.stringify({
        email: this.login_email,
        password: this.login_password,
      }),
    })
      .then((response) => response.json())

      .then((data) => {
        if (data.message === "Login successful") {
          this.user = data.user;

          if (this.user.role === "admin") {
            this.page = "admin_dashboard";
            this.fetch_dashboard_stats();
          } else if (this.user.role === "staff") {
            this.page = "staff_dashboard";
          } else {
            this.page = "dashboard";
          }

          this.message = "Login successful!";
          this.message_type = "success";

          this.login_password = "";
          this.login_email = "";
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

  // Check whether the user is already logged in
  check_login() {
    fetch("/api/auth/me", {
      credentials: "include",
    })
      .then((response) => response.json())

      .then((data) => {
        if (data.logged_in) {
          this.user = data.user;

          if (this.user.role === "admin") {
            this.page = "admin_dashboard";
            this.fetch_dashboard_stats();
          } else if (this.user.role === "staff") {
            this.page = "staff_dashboard";
          } else {
            this.page = "dashboard";
          }
        }
      })

      .catch((error) => {
        console.log(error);
      });
  },

  // Logout the current user
  logout() {
    fetch("/api/auth/logout", {
      method: "POST",
      credentials: "include",
    })
      .then((response) => response.json())
      .then((data) => {
        this.user = null;
        this.page = "login";

        // Reset staff dashboard sections
        this.show_assigned_treks = false;
        this.show_manage_trek = false;
        this.show_participants = false;
        this.assigned_treks = [];
        this.participants = [];
        this.selected_trek = null;
        this.selected_trek_name = "";

        // Reset admin dashboard sections
        this.show_create_trek = false;
        this.show_treks = false;
        this.show_users = false;
        this.show_staff = false;
        this.show_bookings = false;

        this.message = data.message;
        this.message_type = "success";
      })
      .catch((error) => {
        this.message = "Could not connect to the server";
        this.message_type = "error";

        console.log(error);
      });
  },
};
