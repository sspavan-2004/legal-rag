import express from "express";
import { googleCallback, googleStart, login, signup } from "../controllers/authController.js";

const router = express.Router();

router.post("/signup", signup);
router.post("/login", login);
router.get("/google", googleStart);
router.get("/google/callback", googleCallback);

export default router;
