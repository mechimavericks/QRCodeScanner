document.addEventListener("DOMContentLoaded", function () {
    const serverUrl = "https://qrcodescanner-b98i.onrender.com/scan-qr/";

    const html5QrcodeScanner = new Html5QrcodeScanner("qr-reader", { fps: 10, qrbox: 250 });
    html5QrcodeScanner.render(handleQRCode);

    function handleQRCode(data) {
        try {
            const userData = JSON.parse(data);
            document.getElementById("message").textContent = `QR Code Scanned!`;
            document.getElementById("message").style.color = "green"; // Add green color for success
            document.getElementById("name").value = userData.name || '';
            document.getElementById("email").value = userData.email || '';
            document.getElementById("rollno").value = userData.rollno || '';
        } catch (error) {
            console.log("Qr Scan Error", error);
            document.getElementById("message").textContent = "Invalid QR Code";
            document.getElementById("message").style.color = "red"; // Add red color for error
        }
    }

    const submitBtn = document.getElementById("submit");
    document.getElementById("userForm").addEventListener("submit", function (event) {
        event.preventDefault();
        submitBtn.disabled = true;
        submitBtn.textContent = "Submitting...";
        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const rollno = document.getElementById("rollno").value.trim();
        const message = document.getElementById("message");
        if (!name || !email || !rollno) {
            message.innerHTML = "Please fill all the fields";
            message.style.color = "red";
            submitBtn.disabled = false;
            submitBtn.textContent = "Submit";
            return;
        }

        fetch(`${serverUrl}?email=${email}`, {
            method: "POST",
        })
            .then(response => response.json())
            .then(data => {
                message.innerHTML = data.detail;
                message.style.color = "green"; // Add green color for success
                submitBtn.disabled = false;
                submitBtn.textContent = "Submit";
            }).catch(error => {
                console.error("Fetch error:", error);
                message.innerHTML = "An error occurred";
                message.style.color = "red"; // Add red color for error
                submitBtn.disabled = false;
                submitBtn.textContent = "Submit";
            });

    });

});