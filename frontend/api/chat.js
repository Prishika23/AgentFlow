
export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const backendUrl = process.env.AGENTFLOW_BACKEND_URL;
  const token = process.env.AGENTFLOW_TOKEN;

  if (!backendUrl || !token) {
    return res.status(500).json({
      detail: "Backend proxy is not configured.",
    });
  }

  try {
    const response = await fetch(
      `${backendUrl.replace(/\/+$/, "")}/api/chat`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-agentflow-token": token,
        },
        body: JSON.stringify(req.body),
        signal: AbortSignal.timeout(65000),
      }
    );

    const data = await response.json();
    return res.status(response.status).json(data);
  } catch (error) {
    console.error("AgentFlow backend request failed:", error);
    return res.status(502).json({
      detail: "The local AgentFlow backend is unavailable.",
    });
  }
}
