import { ref, push, set, remove, onValue } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js";
import { db } from "./config.js";
import { currentUser, isAdmin, isExpired } from "./auth.js";
import { updateStats, createClassCard } from "./ui.js";

export function handleAddClass(e) {
    e.preventDefault();
    if (isExpired && !isAdmin) return alert("Vui lòng kích hoạt tài khoản!");
    
    const urlInput = document.getElementById('class-url');
    const url = urlInput.value.trim();
    if (!url.includes('classid=')) return alert("Link không hợp lệ!");

    const newClassRef = push(ref(db, `requests/${currentUser.uid}`));
    set(newClassRef, { 
        url: url, name: "Đang chờ check...", code: "...", slots: "?", registration_code: "...",
        last_check: "Chờ worker...", created_at: Date.now(), notification_sent: false
    }).then(() => { urlInput.value = ''; });
}

export function deleteClass(id) {
    if(confirm("Bạn muốn xóa lớp này?")) {
        remove(ref(db, `requests/${currentUser.uid}/${id}`));
    }
}

export function listenToClasses(uid) {
    const classesRef = ref(db, `requests/${uid}`);
    onValue(classesRef, (snapshot) => {
        const container = document.getElementById('class-grid');
        container.innerHTML = '';
        const data = snapshot.val();
        
        if (!data) { 
            updateStats(0, 0);
            document.getElementById('empty-state').classList.remove('hidden');
            return; 
        }
        document.getElementById('empty-state').classList.add('hidden');
        
        let total = 0;
        let avail = 0;
        Object.keys(data).forEach(key => {
            if (typeof data[key] === 'object') {
                total++;
                if (parseInt(data[key].slots) > 0) avail++;
                container.innerHTML += createClassCard(key, data[key]);
            }
        });
        updateStats(total, avail);
    });
}