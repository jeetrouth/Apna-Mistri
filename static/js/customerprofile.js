
const inputs = document.querySelectorAll("input, textarea");
const editBtn = document.getElementById("editBtn");
const saveBtn = document.getElementById("saveBtn");

// Start in VIEW mode
inputs.forEach(i => i.disabled = true);

// Edit click
editBtn.addEventListener("click", () => {
  inputs.forEach(i => i.disabled = false);
  editBtn.style.display = "none";
  saveBtn.style.display = "block";
});

// Save click
saveBtn.addEventListener("click", () => {

  const payload = {
    name: document.querySelector("input[type=text]").value,
    phone: document.querySelectorAll("input")[1].value,
    email: document.querySelector("input[type=email]").value,
    address: {city: document.querySelectorAll("input")[2].value, fulladdr: document.querySelector("textarea").value,pincode: document.querySelectorAll("input")[3].value}
    
  };

  fetch("/api/update-profile", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  })
  .then(res => res.json())
  .then(data => {
    if(data.success){
      alert("Profile Updated");
      inputs.forEach(i => i.disabled = true);
      saveBtn.style.display = "none";
      editBtn.style.display = "block";
    }
  });

});
