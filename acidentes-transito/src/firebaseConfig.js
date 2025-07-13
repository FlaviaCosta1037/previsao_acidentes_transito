
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyCz2SlIB5cubReLEtuoExivmPUnc9AR4NQ",
  authDomain: "acidente-transito.firebaseapp.com",
  projectId: "acidente-transito",
  storageBucket: "acidente-transito.appspot.com", // corrigido: .app -> .com
  messagingSenderId: "387813084188",
  appId: "1:387813084188:web:5793e24149d567610ce3d9",
  measurementId: "G-TSV3J36KPT"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

export { db };
