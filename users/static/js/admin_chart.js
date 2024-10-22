// Get the context of the canvas element we want to select
const ctx = document.getElementById('patientsChart').getContext('2d');

// Create a new Chart object
const chart = new Chart(ctx, {
    type: 'pie', // Chart type
    data: {
        labels: ['In Patients', 'Out Patients'], // Labels for the data
        datasets: [{
            label: 'Patient Distribution',
            data: [patients_in, patients_out], // Dynamic data passed from Django template
            backgroundColor: ['#FF6384', '#36A2EB'], // Colors for the slices
        }]
    },
    options: {
        responsive: true, // Make the chart responsive
    }
});
