import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { getDatabase } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js";

const firebaseConfig = {
    apiKey: "AIzaSyAjgMEBvwLopIA0smZXY8zpWL3uxiLjQtE",
    authDomain: "tool-theo-doi-slot.firebaseapp.com",
    projectId: "tool-theo-doi-slot",
    storageBucket: "tool-theo-doi-slot.firebasestorage.app",
    messagingSenderId: "84464301578",
    appId: "1:84464301578:web:3ea64e467eca65e847d1f3",
    databaseURL: "https://tool-theo-doi-slot-default-rtdb.asia-southeast1.firebasedatabase.app"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getDatabase(app);