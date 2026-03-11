import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import User from "../models/User.js";

const generateToken = (userId) => {
  return jwt.sign({ userId }, process.env.JWT_SECRET, { expiresIn: "7d" });
};

export const signup = async (req, res, next) => {
  try {
    const { name, email, password } = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({ message: "All fields are required" });
    }

    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(409).json({ message: "Email already registered" });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const user = await User.create({
      name,
      email,
      password: hashedPassword,
      provider: "local",
    });

    const token = generateToken(user._id);

    return res.status(201).json({
      message: "Signup successful",
      token,
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
      },
    });
  } catch (error) {
    next(error);
  }
};

export const login = async (req, res, next) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: "Email and password are required" });
    }

    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({ message: "Invalid credentials" });
    }

    if (user.provider !== "local") {
      return res.status(400).json({ message: "Use Google login for this account" });
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(401).json({ message: "Invalid credentials" });
    }

    const token = generateToken(user._id);

    return res.status(200).json({
      message: "Login successful",
      token,
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
      },
    });
  } catch (error) {
    next(error);
  }
};

export const googleStart = (req, res) => {
  const clientId = process.env.GOOGLE_CLIENT_ID;
  const redirectUri = process.env.GOOGLE_REDIRECT_URI;

  if (!clientId || !redirectUri) {
    return res.status(500).json({ message: "Google OAuth not configured" });
  }

  const redirectUrl =
    "https://accounts.google.com/o/oauth2/v2/auth?" +
    new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      response_type: "code",
      scope: "openid email profile",
      access_type: "online",
      prompt: "consent",
    }).toString();

  return res.redirect(redirectUrl);
};

export const googleCallback = async (req, res, next) => {
  try {
    const { code } = req.query;
    const clientId = process.env.GOOGLE_CLIENT_ID;
    const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
    const redirectUri = process.env.GOOGLE_REDIRECT_URI;
    const clientUrl = process.env.CLIENT_URL;

    if (!code) {
      return res.status(400).json({ message: "Missing OAuth code" });
    }

    if (!clientId || !clientSecret || !redirectUri || !clientUrl) {
      return res.status(500).json({ message: "Google OAuth not configured" });
    }

    const tokenResponse = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        client_id: clientId,
        client_secret: clientSecret,
        code,
        redirect_uri: redirectUri,
        grant_type: "authorization_code",
      }),
    });

    const tokenData = await tokenResponse.json();
    if (!tokenData.access_token) {
      return res.status(401).json({ message: "Google token exchange failed" });
    }

    const userResponse = await fetch("https://openidconnect.googleapis.com/v1/userinfo", {
      headers: {
        Authorization: `Bearer ${tokenData.access_token}`,
      },
    });

    const googleUser = await userResponse.json();
    const email = googleUser.email;
    if (!email) {
      return res.status(400).json({ message: "Google email not available" });
    }

    let user = await User.findOne({ email });
    if (!user) {
      user = await User.create({
        name: googleUser.name || "Google User",
        email,
        provider: "google",
        googleId: String(googleUser.sub || ""),
        avatarUrl: googleUser.picture || "",
      });
    } else {
      if (!user.googleId && googleUser.sub) {
        user.googleId = String(googleUser.sub);
      }
      if (!user.avatarUrl && googleUser.picture) {
        user.avatarUrl = googleUser.picture;
      }
      await user.save();
    }

    const token = generateToken(user._id);
    const redirectUrl = `${clientUrl}/oauth/google?token=${encodeURIComponent(token)}`;
    return res.redirect(redirectUrl);
  } catch (error) {
    next(error);
  }
};
