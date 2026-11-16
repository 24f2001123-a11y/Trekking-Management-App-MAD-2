const { createApp } = Vue;

createApp({

    data() {
        return {

            // Current page
            page: "login",

            // Logged-in user
            user: null,

            // Common messages
            message: "",
            message_type: "success",

            // Get data from other JavaScript files
            ...window.auth_data(),
            ...window.admin_data(),
            ...window.staff_data(),
            ...window.user_data()

        };
    },

    methods: {

        // Get methods from other JavaScript files
        ...window.auth_methods,
        ...window.admin_methods,
        ...window.staff_methods,
        ...window.user_methods

    },

    // Run when the page opens
    mounted() {
        this.check_login();
    }

}).mount("#app");
