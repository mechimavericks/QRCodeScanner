document.addEventListener("DOMContentLoaded", function () {
    let approvedList = [];
    let usedEmails = new Set();

    // Load Approved Excel File
    async function loadApprovedList() {
        const response = await fetch("approved.xlsx");
        const arrayBuffer = await response.arrayBuffer();
        const workbook = XLSX.read(arrayBuffer, { type: "array" });
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const data = XLSX.utils.sheet_to_json(sheet);
        
        approvedList = data.map(row => ({ name: row.Name, email: row.Email, rollno: row.RollNo }));
    }

    loadApprovedList();

    // Initialize QR Code Scanner
    var html5QrcodeScanner = new Html5QrcodeScanner(
        "qr-reader", { fps: 10, qrbox: 250 });
    html5QrcodeScanner.render(handleQRCode);

    function handleQRCode(data,result) {
        try {
            const userData = JSON.parse(data);  // Expecting JSON format
            document.getElementById("name").value = userData.name;
            document.getElementById("email").value = userData.email;
            document.getElementById("rollno").value = userData.rollno;
        } catch (error) {
            document.getElementById("message").textContent = "Invalid QR Code";
        }
    }

    // Handle Form Submission
    document.getElementById("userForm").addEventListener("submit", function (e) {
        e.preventDefault();
        
        const name = document.getElementById("name").value;
        const email = document.getElementById("email").value;
        const rollno = document.getElementById("rollno").value;
        const messageEl = document.getElementById("message");

        if (!email) {
            messageEl.textContent = "No QR code scanned!";
            return;
        }

        if (!approvedList.some(user => user.email === email)) {
            messageEl.textContent = "You are not in the approved list!";
            return;
        }

        if (usedEmails.has(email)) {
            messageEl.textContent = "QR Code already used!";
            return;
        }

        // Mark email as used
        usedEmails.add(email);

        // Save Data to Excel
        addEntryToExcel(name, email, rollno);
        messageEl.textContent = "Entry successfully recorded!";
    });

    // Add entry to Excel file
    function addEntryToExcel(name, email, rollno) {
        const newEntry = { Name: name, Email: email, RollNo: rollno };
        
        let wb = XLSX.utils.book_new();
        let ws = XLSX.utils.json_to_sheet([...approvedList, newEntry]);
        XLSX.utils.book_append_sheet(wb, ws, "Approved");
        
        XLSX.writeFile(wb, "approved.xlsx");
    }
});
