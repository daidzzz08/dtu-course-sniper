import { onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { auth } from "./config.js";
import { handleAuth, checkUserStatus, logout, loadSystemAnnouncement } from "./auth.js";
import { switchTab, closeModal } from "./ui.js";
import { handleAddClass, deleteClass } from "./app.js";
import { saveAnnouncement, extendUser, openVipModal, closeVipModal, saveVipConfig } from "./admin.js";

// --- GÁN HÀM VÀO WINDOW ---
window.handleAuth = handleAuth;
window.switchTab = switchTab;
window.closeModal = closeModal;
window.logout = logout;
window.handleAddClass = handleAddClass;
window.deleteClass = deleteClass;
window.saveAnnouncement = saveAnnouncement;
window.extendUser = extendUser;

// New VIP Functions
window.openVipModal = openVipModal;
window.closeVipModal = closeVipModal;
window.saveVipConfig = saveVipConfig;

// --- INIT ---
onAuthStateChanged(auth, (user) => {
    if (user) {
        checkUserStatus(user.uid);
        loadSystemAnnouncement();
    } else {
        document.getElementById('auth-container').classList.remove('hidden');
        document.getElementById('app-container').classList.add('hidden');
    }
});