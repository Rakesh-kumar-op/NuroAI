const BACKEND_URL = "http://127.0.0.1:8000";

export async function predictRisk(payload) {

  const response = await fetch(
    `${BACKEND_URL}/predict`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify(payload)
    }
  );

  return await response.json();
}