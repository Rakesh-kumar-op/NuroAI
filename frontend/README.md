# GutBrain AI - Frontend Dashboard

This is the frontend dashboard for the Gut-Brain Neurodegenerative Vulnerability Assessment platform. It provides a multimodal view of patient risk scores, historical trends, and voice/microbiome analysis.

## 🛠️ Tech Stack
*   **Framework:** React.js (via Vite)
*   **Styling:** Tailwind CSS (v3)
*   **Icons:** Lucide-React
*   **Data Visualization:** Recharts

## 🚀 Getting Started for Backend Integration

To run this frontend locally and start wiring up your APIs, follow these steps:

**1. Install Dependencies**
Ensure you have Node.js installed, then run:
\`\`\`bash
npm install
\`\`\`

**2. Start the Development Server**
\`\`\`bash
npm run dev
\`\`\`
The application will be available at `http://localhost:5173`.

## 🔌 API Integration Points (Action Required)

Currently, the dashboard uses mocked JSON data located at the top of `src/App.jsx`. The backend team will need to replace these mock arrays with live API calls. 

Please target the following data structures:
*   `radarData`: Expects 5 scores (Microbiome, Voice, HRV, Inflammation, AMR) out of 100.
*   `microbiomeData`: Expects an array of objects containing bacterial strain names and their percentage values.
*   `trendData`: Expects historical time-series data for the multi-line chart.

## 📁 Folder Structure Notes
*   `src/App.jsx`: Contains the main layout, Recharts components, and current routing state.
*   `tailwind.config.js`: Contains the Tailwind setup. Do not overwrite without consulting the frontend team.