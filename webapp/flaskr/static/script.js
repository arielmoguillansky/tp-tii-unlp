document.getElementById("registrationForm").addEventListener("submit", async function(event) {
  event.preventDefault();

  const user_email = document.getElementById("user_email").value;
  const user_type = document.getElementById("user_type").value;

  const responseDiv = document.getElementById("response");

  const response = await fetch("http://localhost:5001/register", {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
      },
      body: JSON.stringify({ email: user_email, type: user_type })
  });

  const data = await response.json();
  if (response.ok) {
      responseDiv.innerHTML = `Allowed: ${data.allowed}`;
      if (!data.allowed) {
          responseDiv.innerHTML += `<br>Time left: ${data.time_left} seconds`;
      }
  } else {
      responseDiv.innerHTML = `Error: ${data.error}`;
  }
});

document.getElementById("loginForm").addEventListener("submit", async function(event) {
  event.preventDefault();

  const user_email = document.getElementById("user_email").value;

  const response = await fetch("http://localhost:5001/login", {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
      },
      body: JSON.stringify({ email: user_email })
  });

  const data = await response.json();
  if (response.ok) {
      responseDiv.innerHTML = `Allowed: ${data.allowed}`;
      if (!data.allowed) {
          responseDiv.innerHTML += `<br>Time left: ${data.time_left} seconds`;
      }
  } else {
      responseDiv.innerHTML = `Error: ${data.error}`;
  }
});
