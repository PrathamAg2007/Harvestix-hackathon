function predictYield() {
  let crop = document.getElementById("crop").value;
  let soil = document.getElementById("soil").value;
  let weather = document.getElementById("weather").value;

  fetch("http://127.0.0.1:5000/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ crop, soil, weather })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("yield").innerText = data.prediction;
    document.getElementById("confidence").innerText = data.confidence;
    document.getElementById("fertilizer").innerText = data.fertilizer_suggestion;
    document.getElementById("pest").innerText = data.pest_risk;

    let adviceList = document.getElementById("advice");
    adviceList.innerHTML = "";
    data.advice.forEach(point => {
        let li = document.createElement("li");
        li.innerText = point;
        adviceList.appendChild(li);
    });

    document.getElementById("results").classList.remove("hidden");
    })


  .catch(err => console.error("Error:", err));
}
