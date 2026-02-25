/* =====================================================
   WORKER DASHBOARD JS (CLEANED & IMPROVED VERSION)
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* ================= VIEW ALL REQUESTS ================= */

    const viewAllBtn = document.getElementById("viewAllRequests");

    if (viewAllBtn) {
        viewAllBtn.addEventListener("click", function () {

            const extraCards = document.querySelectorAll(".extra-request");

            extraCards.forEach(card => {
                card.classList.toggle("hidden");
            });

            this.textContent =
                this.textContent.trim() === "View All"
                    ? "Show Less"
                    : "View All";
        });
    }


    /* ================= ONLINE / OFFLINE ================= */

    const toggle = document.getElementById("onlineToggle");
    const statusText = document.getElementById("statusText");

    if (toggle && statusText) {
        toggle.addEventListener("change", function () {
            statusText.textContent = this.checked ? "Online" : "Offline";
        });
    }


    /* ================= CIRCULAR PROGRESS ================= */

    const circles = document.querySelectorAll(".circle");

    circles.forEach(circle => {
        const percent = parseInt(circle.dataset.percent) || 0;

        circle.style.background =
            `conic-gradient(#3b82f6 ${percent}%, #e2e8f0 ${percent}%)`;
    });


    /* ================= JOB HISTORY TABS ================= */

    const tabButtons = document.querySelectorAll(".tabs button");
    const historyRows = document.querySelectorAll("#historyTableBody tr");

    tabButtons.forEach(button => {
        button.addEventListener("click", function () {

            tabButtons.forEach(btn => btn.classList.remove("active"));
            this.classList.add("active");

            const selectedStatus = this.textContent.trim().toLowerCase();

            historyRows.forEach(row => {
                const rowStatus = row.dataset.status.toLowerCase();

                if (!selectedStatus || rowStatus === selectedStatus) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            });
        });
    });


    /* ================= CALENDAR SYSTEM ================= */

    const modal = document.getElementById("calendarModal");
    const openCalendar = document.getElementById("openCalendar");
    const closeCalendar = document.getElementById("closeCalendar");
    const calendarGrid = document.getElementById("calendarGrid");
    const monthYearLabel = document.getElementById("calendarMonthYear");
    const prevBtn = document.getElementById("prevMonth");
    const nextBtn = document.getElementById("nextMonth");
    const jobDetailsBox = document.getElementById("calendarJobDetails");

    let currentDate = new Date();
    let currentMonth = currentDate.getMonth();
    let currentYear = currentDate.getFullYear();

    const monthNames = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ];

    /* SAMPLE JOB DATA (Backend will replace later) */
    const jobs = [
        {
            work_type: "Bathroom Repair",
            customer: "Customer A",
            start: "2026-02-10",
            end: "2026-02-14"
        },
        {
            work_type: "Electrical Fix",
            customer: "Customer B",
            start: "2026-02-12",
            end: "2026-02-15"
        }
    ];


    function renderCalendar(year, month) {

        if (!calendarGrid) return;

        calendarGrid.innerHTML = "";
        if (jobDetailsBox) jobDetailsBox.innerHTML = "";

        if (monthYearLabel) {
            monthYearLabel.textContent = `${monthNames[month]} ${year}`;
        }

        const firstDay = new Date(year, month, 1).getDay();
        const totalDays = new Date(year, month + 1, 0).getDate();

        for (let i = 0; i < firstDay; i++) {
            calendarGrid.appendChild(document.createElement("div"));
        }

        for (let day = 1; day <= totalDays; day++) {

            const dateObj = new Date(year, month, day);
            const dateStr = dateObj.toISOString().split("T")[0];

            let classes = "calendar-day";

            jobs.forEach(job => {

                if (dateStr >= job.start && dateStr <= job.end) {

                    if (dateStr === job.start) {
                        classes += " start-date";
                    }
                    else if (dateStr === job.end) {
                        classes += " end-date";
                    }
                    else {
                        classes += " middle-date";
                    }
                }
            });

            const dayDiv = document.createElement("div");
            dayDiv.className = classes;
            dayDiv.innerHTML = `<strong>${day}</strong>`;
            dayDiv.dataset.date = dateStr;

            dayDiv.addEventListener("click", function () {
                showJobsForDate(dateStr);
            });

            calendarGrid.appendChild(dayDiv);
        }
    }


    function showJobsForDate(dateStr) {

        if (!jobDetailsBox) return;

        jobDetailsBox.innerHTML = `<h4>Jobs on ${dateStr}</h4>`;

        const jobsOnDate = jobs.filter(job =>
            dateStr >= job.start && dateStr <= job.end
        );

        if (jobsOnDate.length === 0) {
            jobDetailsBox.innerHTML += "<p>No jobs on this day.</p>";
            return;
        }

        jobsOnDate.forEach(job => {
            jobDetailsBox.innerHTML += `
                <div class="calendar-job-item">
                    <strong>${job.work_type}</strong>
                    <p>Customer: ${job.customer}</p>
                    <p>${job.start} → ${job.end}</p>
                </div>
            `;
        });
    }


    /* MONTH NAVIGATION */

    if (prevBtn) {
        prevBtn.addEventListener("click", function () {
            currentMonth--;
            if (currentMonth < 0) {
                currentMonth = 11;
                currentYear--;
            }
            renderCalendar(currentYear, currentMonth);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener("click", function () {
            currentMonth++;
            if (currentMonth > 11) {
                currentMonth = 0;
                currentYear++;
            }
            renderCalendar(currentYear, currentMonth);
        });
    }
/* ================= NEW JOB ACTIONS ================= */

document.querySelectorAll(".job-actions .primary").forEach(btn => {
    btn.addEventListener("click", function () {
        alert("Job Accepted");
    });
});

document.querySelectorAll(".job-actions .danger").forEach(btn => {
    btn.addEventListener("click", function () {
        alert("Job Declined");
    });
});

document.querySelectorAll(".job-actions .outline").forEach(btn => {
    btn.addEventListener("click", function () {
        alert("View Job Details");
    });
});
/* ================= ONGOING JOB ACTIONS ================= */

const openDetailsBtn = document.querySelector(".ongoing-card .outline");
const markCompleteBtn = document.querySelector(".ongoing-card .primary");

if (openDetailsBtn) {
    openDetailsBtn.addEventListener("click", function () {
        alert("Opening Job Details...");
    });
}

if (markCompleteBtn) {
    markCompleteBtn.addEventListener("click", function () {
        alert("Job Marked Completed");
    });
}
    /* MODAL CONTROL (Better Way) */

    if (openCalendar && modal) {
        openCalendar.addEventListener("click", function () {
            modal.style.display = "flex";
            renderCalendar(currentYear, currentMonth);
        });
    }

    if (closeCalendar && modal) {
        closeCalendar.addEventListener("click", function () {
            modal.style.display = "none";
        });
    }

    window.addEventListener("click", function (e) {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });

});