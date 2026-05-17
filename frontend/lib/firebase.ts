/**
 * Firebase client SDK initialization.
 *
 * Reads NEXT_PUBLIC_FIREBASE_* env vars (see .env at repo root). Safe to import
 * from any client component; guards against double-init in Next.js HMR /
 * server/client boundary.
 */

import { getApp, getApps, initializeApp, type FirebaseApp, type FirebaseOptions } from "firebase/app";
import { getAuth, type Auth } from "firebase/auth";
import { getFirestore, type Firestore } from "firebase/firestore";
import { getStorage, type FirebaseStorage } from "firebase/storage";

function requireEnv(key: string): string {
  const value = process.env[key];
  if (!value) {
    // Don't throw at module-load on the server - surface a clear error only
    // when the SDK is actually exercised. This keeps `next build` working
    // even if env vars are missing in the build environment.
    return "";
  }
  return value;
}

const firebaseConfig: FirebaseOptions = {
  apiKey: requireEnv("NEXT_PUBLIC_FIREBASE_API_KEY"),
  authDomain: requireEnv("NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN"),
  projectId: requireEnv("NEXT_PUBLIC_FIREBASE_PROJECT_ID"),
  storageBucket: requireEnv("NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET"),
  messagingSenderId: requireEnv("NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID"),
  appId: requireEnv("NEXT_PUBLIC_FIREBASE_APP_ID"),
  measurementId: requireEnv("NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID"),
};

// Defer init until the SDK is actually exercised. Eager init at module
// import would crash `next build` static generation when the build env has
// no Firebase env vars (auth/invalid-api-key thrown from the worker).
let _app: FirebaseApp | null = null;
function ensureApp(): FirebaseApp {
  if (_app) return _app;
  if (!firebaseConfig.apiKey || !firebaseConfig.projectId) {
    throw new Error(
      "Firebase is not configured. Set NEXT_PUBLIC_FIREBASE_* env vars to enable client SDK."
    );
  }
  _app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
  return _app;
}

export const firebaseApp: FirebaseApp = new Proxy({} as FirebaseApp, {
  get: (_t, prop) => Reflect.get(ensureApp() as object, prop),
});
export const firebaseAuth: Auth = new Proxy({} as Auth, {
  get: (_t, prop) => Reflect.get(getAuth(ensureApp()) as object, prop),
});
export const firestore: Firestore = new Proxy({} as Firestore, {
  get: (_t, prop) => Reflect.get(getFirestore(ensureApp()) as object, prop),
});
export const firebaseStorage: FirebaseStorage = new Proxy({} as FirebaseStorage, {
  get: (_t, prop) => Reflect.get(getStorage(ensureApp()) as object, prop),
});

export function isFirebaseConfigured(): boolean {
  return Boolean(firebaseConfig.apiKey && firebaseConfig.projectId);
}
