function selectRole(role) {

    if (role === "worker") {
        window.location.href = "/worker-onboarding";
    } 
    else if (role === "customer") {
        window.location.href = "/customer-dashboard";
    }

}
