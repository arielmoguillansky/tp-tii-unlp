let limitError = document.getElementById("limitError");
let errorMsgEl = document.getElementById("prediction_error");
let responseEl = document.getElementById("prediction_response");
let tableBody = document.getElementsByTagName("tbody")[0];
let payloadEl = document.getElementById("requestPayload");
let loadingMsg = document.getElementById("prediction_loading");

function addUri() {
  if (checkPayloadLimit()) return;
  let uriInput = document.getElementById("entity_uri");
  let uriVal = uriInput.value;
  if (!uriVal) return;
  let payloadEl = document.getElementById("requestPayload");
  let uri = document.createElement("li");
  uri.innerHTML = uriVal;
  let deleteButton = document.createElement("div");
  deleteButton.innerHTML = "Eliminar";
  deleteButton.onclick = () => removeUri(uri);
  payloadEl.appendChild(uri);
  payloadEl.appendChild(deleteButton);
  uriInput.value = "";
}
function addId() {
  if (checkPayloadLimit()) return;
  let idInput = document.getElementById("entity_id");
  let idValue = idInput.value;
  if (!idValue) return;
  let payloadEl = document.getElementById("requestPayload");
  let entityId = document.createElement("li");
  entityId.innerHTML = idValue;
  let deleteButton = document.createElement("div");
  deleteButton.innerHTML = "Eliminar";
  deleteButton.onclick = () => removeUri(entityId);
  payloadEl.appendChild(entityId);
  payloadEl.appendChild(deleteButton);
  idInput.value = "";
}

function removeUri(el) {
  limitError.innerHTML = "";
  el.nextSibling.remove();
  el.remove();
}

function checkPayloadLimit() {
  const numberOfChildren = payloadEl.getElementsByTagName("li").length;
  let limitError = document.getElementById("limitError");

  if (numberOfChildren >= 3) {
    limitError.innerHTML =
      "Solo se pueden agregar hasta 3 elementos en su tipo de suscripción. Para poder enviar más datos, suscríbase al plan premium.";
    return true;
  } else {
    limitError.innerHTML = "";
    return false;
  }
}

function predict() {
  responseEl.style.display = "none";
  errorMsgEl.innerHTML = "";
  tableBody.innerHTML = "";
  loadingMsg.style.display = "block";
  const values = document
    .getElementById("requestPayload")
    .getElementsByTagName("li");
  let payload = [];
  for (let i = 0; i < values.length; i++) {
    let value = values[i].innerHTML.trim();
    let numValue = Number(value);

    payload.push(isNaN(numValue) ? value : numValue);
  }

  fetch("/predict", {
    method: "POST",
    body: JSON.stringify({ payload }),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      loadingMsg.style.display = "none";
      if (!data.allowed && typeof data.error === "string") {
        errorMsgEl.innerHTML = data.error;
        return;
      }
      if (!data.allowed && data.error) {
        errorMsgEl.innerHTML = data.error?.message;
        if (data.error.time_left) {
          let predictBtn = document.getElementById("predictBtn");
          predictBtn.disabled = true;
          let timeLeft = data.error.time_left;
          let countdown = setInterval(() => {
            timeLeft--;
            if (timeLeft < 0) {
              predictBtn.disabled = false;
              clearInterval(countdown);
              errorMsgEl.innerHTML = "";
              return;
            }
            errorMsgEl.innerHTML = `${data.error.message}. Espere ${timeLeft} segundos antes de intentar de nuevo.`;
          }, 1000);
        }
        return;
      }
      if (data.allowed && data.response) {
        payloadEl.innerHTML = "";
        responseEl.style.display = "block";
        const indexes = data.response.indexes[0];
        const scores = data.response.scores[0];

        indexes.forEach((index, i) => {
          const row = document.createElement("tr");
          row.innerHTML = `
                <td>${index}</td>
                <td>${scores[i].toFixed(
                  6
                )}</td> <!-- Format score to 6 decimal places -->
            `;
          tableBody.appendChild(row);
        });

        document.getElementById("prediction_response").style.display = "block";
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      errorMsgEl.innerHTML = "Ha ocurrido un error al realizar la predicción.";
      loadingMsg.style.display = "none";
    });
}
