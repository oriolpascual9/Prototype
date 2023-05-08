// Array to store the transportation data
let transportationData = [];

// Function to run when the document is ready
$(document).ready(function () {
    // Add click event listener to transportation mode buttons
    $("button[data-mode]").on("click", function () {
        // Get the transportation mode from the clicked button
        const mode = $(this).data("mode");

        // Add the transportation mode to the data array
        transportationData.push(mode);

        // Handle data storage and update data visualization
        // Replace the console.log with your own logic to store and visualize the data
        console.log(transportationData);
    });

    // Add click event listener to the return button
    $("#return").on("click", function () {
        // If there is any data in the transportationData array
        if (transportationData.length > 0) {
            // Remove the last transportation mode added
            transportationData.pop();

            // Handle data removal and update data visualization
            // Replace the console.log with your own logic to remove and update the data visualization
            console.log(transportationData);
        }
    });

    // Add any additional JavaScript code related to data visualization and filtering
});
