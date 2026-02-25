// Toggle workers popup
function toggleWorkers(){
document.getElementById("workersPopup").classList.toggle("show");
}

// Search filter
document.getElementById("searchInput").addEventListener("keyup", function(){
let value = this.value.toLowerCase();
let workers = document.querySelectorAll(".worker");

workers.forEach(function(worker){
let skill = worker.getAttribute("data-skill");
worker.style.display = skill.includes(value) ? "flex" : "none";
});
});

// ===== CHAT SYSTEM =====
let currentWorker = "";

function openChat(name){
currentWorker = name;

document.getElementById("chatBox").style.display="block";
document.getElementById("chatTitle").innerText="Chat with "+name;

/* ⭐ PRO CHANGE */
document.body.classList.add("chat-open");
}

function closeChat(){
document.getElementById("chatBox").style.display="none";

/* ⭐ PRO CHANGE */
document.body.classList.remove("chat-open");
}
function sendMessage(){
let input=document.getElementById("chatInput");
let msg=input.value;
if(msg==="") return;

let box=document.getElementById("chatMessages");
box.innerHTML += "<p><b>You:</b> "+msg+"</p>";
input.value="";
}

// ===== LOGIN / PROFILE =====
function goLogin(){
alert("Login page opening (Demo)");
}

function goProfile(){
alert("Opening My Profile (Demo)");
}