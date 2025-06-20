async function sendMessage() {
  const msg = document.getElementById("msg-input").value;
  const res = await fetch("/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg }),
  });

  const data = await res.json();
  const box = document.getElementById("chat-box");
  box.innerHTML += `<p><b>You:</b> ${msg}</p>`;
  box.innerHTML += `<p><b>Bot:</b> ${data.response}</p>`;
}

document.getElementById("upload-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const res = await fetch("/add_contacts", {
    method: "POST",
    body: formData,
  });

  alert(await res.text());
});
